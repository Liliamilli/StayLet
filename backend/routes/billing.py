"""
Billing and subscription routes for Staylet.
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone, timedelta
import uuid
import os
import logging

from models.database import db
from models.schemas import (
    SubscriptionResponse, SubscriptionUpdate, PlanLimitCheck,
    CheckoutRequest, CheckoutResponse, PaymentStatusResponse
)
from utils.auth import get_current_user
from utils.constants import SUBSCRIPTION_PLANS, TRIAL_DAYS
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest, CheckoutSessionResponse, CheckoutStatusResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Billing"])

STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(current_user: dict = Depends(get_current_user)):
    """Get current user's subscription details."""
    plan = current_user.get("subscription_plan", "solo")
    status = current_user.get("subscription_status", "trial")
    plan_info = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS["solo"])
    
    # Check if trial expired
    if status == "trial" and current_user.get("trial_end"):
        trial_end = datetime.fromisoformat(current_user["trial_end"].replace('Z', '+00:00'))
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > trial_end:
            status = "expired"
            await db.users.update_one({"id": current_user["id"]}, {"$set": {"subscription_status": "expired"}})
    
    property_count = await db.properties.count_documents({"user_id": current_user["id"], "property_status": "active"})
    
    # Calculate trial days remaining
    trial_days_remaining = None
    if status == "trial" and current_user.get("trial_end"):
        trial_end = datetime.fromisoformat(current_user["trial_end"].replace('Z', '+00:00'))
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)
        trial_days_remaining = max(0, (trial_end - datetime.now(timezone.utc)).days)
    
    # Determine upgrade/downgrade options
    plan_order = ["solo", "portfolio", "operator"]
    current_idx = plan_order.index(plan) if plan in plan_order else 0
    can_upgrade = current_idx < len(plan_order) - 1
    can_downgrade = current_idx > 0 and property_count <= SUBSCRIPTION_PLANS[plan_order[current_idx - 1]]["property_limit"]
    
    return SubscriptionResponse(
        plan=plan,
        plan_name=plan_info["name"],
        status=status,
        property_limit=plan_info["property_limit"],
        property_count=property_count,
        trial_start=current_user.get("trial_start"),
        trial_end=current_user.get("trial_end"),
        trial_days_remaining=trial_days_remaining,
        price_monthly=plan_info["price_monthly"],
        price_yearly=plan_info["price_yearly"],
        features=plan_info["features"],
        can_upgrade=can_upgrade,
        can_downgrade=can_downgrade
    )


@router.get("/subscription/plans")
async def get_subscription_plans():
    """Get all available subscription plans."""
    return {"plans": SUBSCRIPTION_PLANS, "trial_days": TRIAL_DAYS}


@router.post("/subscription/change", response_model=SubscriptionResponse)
async def change_subscription(update: SubscriptionUpdate, current_user: dict = Depends(get_current_user)):
    """Change subscription plan."""
    new_plan = update.plan.lower()
    if new_plan not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan selected")
    
    new_plan_info = SUBSCRIPTION_PLANS[new_plan]
    
    # Check if downgrade is possible
    property_count = await db.properties.count_documents({"user_id": current_user["id"], "property_status": "active"})
    if property_count > new_plan_info["property_limit"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot downgrade to {new_plan_info['name']} plan. You have {property_count} properties but the limit is {new_plan_info['property_limit']}."
        )
    
    now = datetime.now(timezone.utc).isoformat()
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"subscription_plan": new_plan, "subscription_status": "active", "updated_at": now}}
    )
    
    plan_order = ["solo", "portfolio", "operator"]
    current_idx = plan_order.index(new_plan) if new_plan in plan_order else 0
    can_upgrade = current_idx < len(plan_order) - 1
    can_downgrade = current_idx > 0 and property_count <= SUBSCRIPTION_PLANS[plan_order[current_idx - 1]]["property_limit"]
    
    return SubscriptionResponse(
        plan=new_plan,
        plan_name=new_plan_info["name"],
        status="active",
        property_limit=new_plan_info["property_limit"],
        property_count=property_count,
        trial_start=current_user.get("trial_start"),
        trial_end=current_user.get("trial_end"),
        trial_days_remaining=None,
        price_monthly=new_plan_info["price_monthly"],
        price_yearly=new_plan_info["price_yearly"],
        features=new_plan_info["features"],
        can_upgrade=can_upgrade,
        can_downgrade=can_downgrade
    )


@router.get("/subscription/check-limit", response_model=PlanLimitCheck)
async def check_property_limit(current_user: dict = Depends(get_current_user)):
    """Check if user can add another property."""
    plan = current_user.get("subscription_plan", "solo")
    status = current_user.get("subscription_status", "trial")
    plan_info = SUBSCRIPTION_PLANS.get(plan, SUBSCRIPTION_PLANS["solo"])
    
    property_count = await db.properties.count_documents({"user_id": current_user["id"], "property_status": "active"})
    property_limit = plan_info["property_limit"]
    
    # Check if trial expired
    if status == "trial" and current_user.get("trial_end"):
        trial_end = datetime.fromisoformat(current_user["trial_end"].replace('Z', '+00:00'))
        if trial_end.tzinfo is None:
            trial_end = trial_end.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > trial_end:
            return PlanLimitCheck(
                allowed=False, current_count=property_count, limit=property_limit, plan=plan,
                message="Your trial has expired. Please upgrade to continue using Staylet."
            )
    
    if property_count >= property_limit:
        plan_order = ["solo", "portfolio", "operator"]
        current_idx = plan_order.index(plan) if plan in plan_order else 0
        if current_idx < len(plan_order) - 1:
            next_plan = plan_order[current_idx + 1]
            next_plan_info = SUBSCRIPTION_PLANS[next_plan]
            return PlanLimitCheck(
                allowed=False, current_count=property_count, limit=property_limit, plan=plan,
                message=f"You've reached the {property_limit} property limit. Upgrade to {next_plan_info['name']} for up to {next_plan_info['property_limit']} properties."
            )
        return PlanLimitCheck(
            allowed=False, current_count=property_count, limit=property_limit, plan=plan,
            message=f"You've reached the maximum of {property_limit} properties. Contact support for enterprise options."
        )
    
    return PlanLimitCheck(allowed=True, current_count=property_count, limit=property_limit, plan=plan, message=None)


@router.post("/payments/checkout", response_model=CheckoutResponse)
async def create_checkout_session(request: Request, checkout_request: CheckoutRequest, current_user: dict = Depends(get_current_user)):
    """Create a Stripe checkout session."""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    
    plan = checkout_request.plan.lower()
    if plan not in SUBSCRIPTION_PLANS:
        raise HTTPException(status_code=400, detail="Invalid plan selected")
    
    plan_info = SUBSCRIPTION_PLANS[plan]
    billing_cycle = checkout_request.billing_cycle.lower()
    amount = float(plan_info["price_yearly"]) if billing_cycle == "annual" else float(plan_info["price_monthly"])
    
    origin_url = checkout_request.origin_url.rstrip('/')
    success_url = f"{origin_url}/app/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/app/billing"
    
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    session_id = str(uuid.uuid4())
    metadata = {
        "user_id": current_user["id"],
        "user_email": current_user["email"],
        "plan": plan,
        "billing_cycle": billing_cycle,
        "internal_session_id": session_id
    }
    
    checkout_req = CheckoutSessionRequest(
        amount=amount, currency="gbp", success_url=success_url, cancel_url=cancel_url, metadata=metadata
    )
    
    try:
        session: CheckoutSessionResponse = await stripe_checkout.create_checkout_session(checkout_req)
        
        now = datetime.now(timezone.utc).isoformat()
        transaction = {
            "id": session_id, "stripe_session_id": session.session_id,
            "user_id": current_user["id"], "user_email": current_user["email"],
            "plan": plan, "billing_cycle": billing_cycle, "amount": amount, "currency": "gbp",
            "payment_status": "pending", "status": "initiated", "created_at": now, "updated_at": now
        }
        await db.payment_transactions.insert_one(transaction)
        
        return CheckoutResponse(checkout_url=session.url, session_id=session.session_id)
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")


@router.get("/payments/status/{session_id}", response_model=PaymentStatusResponse)
async def get_payment_status(session_id: str, current_user: dict = Depends(get_current_user)):
    """Get payment status and update subscription if paid."""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    
    transaction = await db.payment_transactions.find_one({"stripe_session_id": session_id}, {"_id": 0})
    if not transaction:
        raise HTTPException(status_code=404, detail="Payment session not found")
    
    if transaction.get("payment_status") == "paid":
        return PaymentStatusResponse(
            status="complete", payment_status="paid", plan=transaction.get("plan"),
            billing_cycle=transaction.get("billing_cycle"), success=True, message="Payment already processed"
        )
    
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
    
    try:
        status: CheckoutStatusResponse = await stripe_checkout.get_checkout_status(session_id)
        now = datetime.now(timezone.utc).isoformat()
        
        await db.payment_transactions.update_one(
            {"stripe_session_id": session_id},
            {"$set": {"payment_status": status.payment_status, "status": status.status, "updated_at": now}}
        )
        
        if status.payment_status == "paid":
            plan = transaction.get("plan", "solo")
            billing_cycle = transaction.get("billing_cycle", "monthly")
            subscription_end = (datetime.now(timezone.utc) + timedelta(days=365 if billing_cycle == "annual" else 30)).isoformat()
            
            await db.users.update_one(
                {"id": transaction["user_id"]},
                {"$set": {
                    "subscription_plan": plan, "subscription_status": "active",
                    "subscription_start": now, "subscription_end": subscription_end,
                    "billing_cycle": billing_cycle, "updated_at": now
                }}
            )
            
            return PaymentStatusResponse(
                status=status.status, payment_status=status.payment_status, plan=plan,
                billing_cycle=billing_cycle, success=True,
                message=f"Successfully subscribed to {SUBSCRIPTION_PLANS[plan]['name']} plan!"
            )
        elif status.status == "expired":
            return PaymentStatusResponse(
                status=status.status, payment_status=status.payment_status, success=False,
                message="Payment session expired. Please try again."
            )
        return PaymentStatusResponse(
            status=status.status, payment_status=status.payment_status, success=False,
            message="Payment is being processed..."
        )
    except Exception as e:
        logger.error(f"Stripe status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check payment status: {str(e)}")


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        now = datetime.now(timezone.utc).isoformat()
        
        if webhook_response.session_id:
            await db.payment_transactions.update_one(
                {"stripe_session_id": webhook_response.session_id},
                {"$set": {
                    "payment_status": webhook_response.payment_status,
                    "webhook_event_type": webhook_response.event_type,
                    "webhook_event_id": webhook_response.event_id,
                    "updated_at": now
                }}
            )
            
            if webhook_response.payment_status == "paid":
                transaction = await db.payment_transactions.find_one(
                    {"stripe_session_id": webhook_response.session_id}, {"_id": 0}
                )
                
                if transaction:
                    plan = transaction.get("plan", "solo")
                    billing_cycle = transaction.get("billing_cycle", "monthly")
                    subscription_end = (datetime.now(timezone.utc) + timedelta(days=365 if billing_cycle == "annual" else 30)).isoformat()
                    
                    await db.users.update_one(
                        {"id": transaction["user_id"]},
                        {"$set": {
                            "subscription_plan": plan, "subscription_status": "active",
                            "subscription_start": now, "subscription_end": subscription_end,
                            "billing_cycle": billing_cycle, "updated_at": now
                        }}
                    )
        
        return {"received": True}
    except Exception as e:
        logger.error(f"Stripe webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")
