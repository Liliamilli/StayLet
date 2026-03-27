import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Switch } from '../components/ui/switch';
import { 
    CreditCard, 
    Check, 
    Building2, 
    Clock, 
    AlertTriangle,
    Sparkles,
    Crown,
    Zap,
    ArrowRight,
    Loader2,
    Receipt,
    Calendar,
    Percent
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const PLAN_ICONS = {
    solo: Building2,
    portfolio: Zap,
    operator: Crown
};

const PLAN_COLORS = {
    solo: { bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-200', accent: 'bg-slate-600' },
    portfolio: { bg: 'bg-blue-100', text: 'text-blue-700', border: 'border-blue-200', accent: 'bg-blue-600' },
    operator: { bg: 'bg-purple-100', text: 'text-purple-700', border: 'border-purple-200', accent: 'bg-purple-600' }
};

function PlanCard({ plan, planKey, isCurrentPlan, subscription, onSelect, loading, isAnnual }) {
    const Icon = PLAN_ICONS[planKey] || Building2;
    const colors = PLAN_COLORS[planKey] || PLAN_COLORS.solo;
    const isPopular = planKey === 'portfolio';
    const canSelect = !isCurrentPlan && (
        plan.property_limit > (subscription?.property_count || 0) || 
        plan.property_limit > (subscription?.property_limit || 1)
    );
    const isDowngrade = plan.property_limit < (subscription?.property_limit || 1);
    const cantDowngrade = isDowngrade && (subscription?.property_count || 0) > plan.property_limit;
    const isTrial = subscription?.status === 'trial' || subscription?.status === 'expired';
    
    const monthlyPrice = plan.price_monthly;
    const yearlyPrice = plan.price_yearly;
    const yearlyMonthly = Math.round(yearlyPrice / 12);
    const savings = (monthlyPrice * 12) - yearlyPrice;
    const savingsPercent = Math.round((savings / (monthlyPrice * 12)) * 100);

    const getButtonText = () => {
        if (isDowngrade) return 'Downgrade';
        if (isTrial) return 'Subscribe';
        return 'Upgrade';
    };

    return (
        <div className={`
            relative rounded-xl border-2 p-6 transition-all
            ${isCurrentPlan ? 'border-blue-500 bg-blue-50/50' : colors.border + ' bg-white hover:border-slate-300'}
            ${isPopular && !isCurrentPlan ? 'ring-2 ring-blue-500 ring-offset-2' : ''}
        `}>
            {isPopular && !isCurrentPlan && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-blue-600 text-white text-xs font-medium rounded-full">
                    Most Popular
                </div>
            )}
            
            {isCurrentPlan && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-emerald-600 text-white text-xs font-medium rounded-full flex items-center gap-1">
                    <Check className="w-3 h-3" />
                    Current Plan
                </div>
            )}
            
            {isAnnual && !isCurrentPlan && (
                <div className="absolute -top-3 right-4 px-2 py-1 bg-emerald-500 text-white text-xs font-medium rounded-full flex items-center gap-1">
                    <Percent className="w-3 h-3" />
                    Save £{savings}/yr
                </div>
            )}

            <div className="text-center mb-6">
                <div className={`w-12 h-12 ${colors.bg} rounded-xl flex items-center justify-center mx-auto mb-3`}>
                    <Icon className={`w-6 h-6 ${colors.text}`} />
                </div>
                <h3 className="text-xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                    {plan.name}
                </h3>
                <div className="mt-2">
                    {isAnnual ? (
                        <>
                            <span className="text-3xl font-bold text-slate-900">£{yearlyMonthly}</span>
                            <span className="text-slate-500">/month</span>
                            <p className="text-sm text-slate-500 mt-1">
                                £{yearlyPrice} billed annually
                            </p>
                            <p className="text-xs text-emerald-600 font-medium">
                                Save {savingsPercent}% vs monthly
                            </p>
                        </>
                    ) : (
                        <>
                            <span className="text-3xl font-bold text-slate-900">£{monthlyPrice}</span>
                            <span className="text-slate-500">/month</span>
                            <p className="text-sm text-slate-500 mt-1">
                                billed monthly
                            </p>
                        </>
                    )}
                </div>
            </div>

            <ul className="space-y-3 mb-6">
                {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm">
                        <Check className={`w-4 h-4 mt-0.5 flex-shrink-0 ${colors.text}`} />
                        <span className="text-slate-700">{feature}</span>
                    </li>
                ))}
            </ul>

            {isCurrentPlan ? (
                <Button disabled className="w-full" variant="outline">
                    <Check className="w-4 h-4 mr-2" />
                    Current Plan
                </Button>
            ) : cantDowngrade ? (
                <Button disabled className="w-full" variant="outline">
                    Remove properties to downgrade
                </Button>
            ) : (
                <Button 
                    onClick={() => onSelect(planKey)}
                    disabled={loading}
                    className={`w-full ${isDowngrade ? 'bg-slate-600 hover:bg-slate-700' : colors.accent + ' hover:opacity-90'} text-white`}
                    data-testid={`plan-${planKey}-btn`}
                >
                    {loading ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                        <>
                            {getButtonText()}
                            {!isDowngrade && <ArrowRight className="w-4 h-4 ml-2" />}
                        </>
                    )}
                </Button>
            )}
        </div>
    );
}

export default function BillingPage() {
    const { subscription, refreshSubscription } = useAuth();
    const [plans, setPlans] = useState(null);
    const [loading, setLoading] = useState(true);
    const [changingPlan, setChangingPlan] = useState(false);
    const [selectedPlan, setSelectedPlan] = useState(null);
    const [isAnnual, setIsAnnual] = useState(false);

    useEffect(() => {
        fetchPlans();
    }, []);

    const fetchPlans = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/subscription/plans`);
            setPlans(response.data.plans);
        } catch (error) {
            console.error('Failed to fetch plans:', error);
        } finally {
            setLoading(false);
        }
    };

    const handlePlanChange = async (planKey) => {
        const planInfo = plans[planKey];
        const isUpgrade = planInfo.property_limit > subscription.property_limit;
        const billingCycle = isAnnual ? 'annual' : 'monthly';
        const price = isAnnual ? planInfo.price_yearly : planInfo.price_monthly;
        
        // For upgrades, redirect to Stripe checkout
        if (isUpgrade || subscription.status === 'trial' || subscription.status === 'expired') {
            const confirmMessage = `You're about to subscribe to the ${planInfo.name} plan for £${price}/${isAnnual ? 'year' : 'month'}. Continue to secure checkout?`;
            if (!window.confirm(confirmMessage)) {
                return;
            }
            
            setChangingPlan(true);
            setSelectedPlan(planKey);
            
            try {
                const response = await axios.post(`${API_URL}/api/payments/checkout`, {
                    plan: planKey,
                    billing_cycle: billingCycle,
                    origin_url: window.location.origin
                });
                
                // Redirect to Stripe checkout
                window.location.href = response.data.checkout_url;
            } catch (error) {
                console.error('Failed to create checkout session:', error);
                alert(error.response?.data?.detail || 'Failed to start checkout. Please try again.');
                setChangingPlan(false);
                setSelectedPlan(null);
            }
        } else {
            // For downgrades (active paid users), use direct plan change
            if (!window.confirm(`Are you sure you want to downgrade to the ${planInfo.name} plan?`)) {
                return;
            }
            
            setChangingPlan(true);
            setSelectedPlan(planKey);
            try {
                await axios.post(`${API_URL}/api/subscription/change`, { plan: planKey });
                await refreshSubscription();
            } catch (error) {
                console.error('Failed to change plan:', error);
                alert(error.response?.data?.detail || 'Failed to change plan. Please try again.');
            } finally {
                setChangingPlan(false);
                setSelectedPlan(null);
            }
        }
    };

    const formatDate = (dateStr) => {
        if (!dateStr) return '—';
        return new Date(dateStr).toLocaleDateString('en-GB', { 
            day: 'numeric', 
            month: 'long', 
            year: 'numeric' 
        });
    };

    if (loading) {
        return (
            <div className="animate-pulse space-y-6">
                <div className="h-8 bg-slate-200 rounded w-48" />
                <div className="h-64 bg-slate-200 rounded-lg" />
            </div>
        );
    }

    const isTrialActive = subscription?.status === 'trial' && subscription?.trial_days_remaining > 0;
    const isTrialExpired = subscription?.status === 'expired';

    return (
        <div data-testid="billing-page">
            {/* Page header */}
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-slate-900 mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
                    Billing & Subscription
                </h1>
                <p className="text-slate-500">
                    Manage your subscription plan and billing details
                </p>
            </div>

            {/* Trial Banner */}
            {isTrialActive && (
                <div className="mb-6 p-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl text-white">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-white/20 rounded-lg">
                                <Sparkles className="w-5 h-5" />
                            </div>
                            <div>
                                <p className="font-semibold">Free Trial Active</p>
                                <p className="text-sm text-blue-100">
                                    {subscription.trial_days_remaining} days remaining • Ends {formatDate(subscription.trial_end)}
                                </p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-sm text-blue-100">Trial includes full access to</p>
                            <p className="font-semibold">{subscription.plan_name} plan features</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Trial Expired Banner */}
            {isTrialExpired && (
                <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl">
                    <div className="flex items-center gap-3">
                        <AlertTriangle className="w-5 h-5 text-amber-600" />
                        <div>
                            <p className="font-semibold text-amber-900">Your trial has expired</p>
                            <p className="text-sm text-amber-700">
                                Choose a plan below to continue using Staylet.
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Current Subscription Card */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 mb-8">
                <h2 className="text-lg font-semibold text-slate-900 mb-4" style={{ fontFamily: 'Outfit, sans-serif' }}>
                    Current Subscription
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div>
                        <p className="text-sm text-slate-500 mb-1">Plan</p>
                        <p className="font-semibold text-slate-900 text-lg">{subscription?.plan_name || 'Solo'}</p>
                    </div>
                    <div>
                        <p className="text-sm text-slate-500 mb-1">Status</p>
                        <span className={`
                            inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium
                            ${subscription?.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 
                              subscription?.status === 'trial' ? 'bg-blue-100 text-blue-700' : 
                              'bg-amber-100 text-amber-700'}
                        `}>
                            {subscription?.status === 'active' && <Check className="w-3.5 h-3.5" />}
                            {subscription?.status === 'trial' && <Clock className="w-3.5 h-3.5" />}
                            {subscription?.status === 'expired' && <AlertTriangle className="w-3.5 h-3.5" />}
                            {subscription?.status === 'active' ? 'Active' : 
                             subscription?.status === 'trial' ? 'Trial' : 'Expired'}
                        </span>
                    </div>
                    <div>
                        <p className="text-sm text-slate-500 mb-1">Properties</p>
                        <p className="font-semibold text-slate-900">
                            {subscription?.property_count || 0} / {subscription?.property_limit || 1}
                        </p>
                    </div>
                    <div>
                        <p className="text-sm text-slate-500 mb-1">Monthly Price</p>
                        <p className="font-semibold text-slate-900">
                            £{subscription?.price_monthly || 19}/month
                        </p>
                    </div>
                </div>
            </div>

            {/* Plans Grid */}
            <div className="mb-8">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                    <h2 className="text-lg font-semibold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        Available Plans
                    </h2>
                    
                    {/* Annual/Monthly Toggle */}
                    <div className="flex items-center gap-3 bg-slate-100 rounded-lg p-1" data-testid="billing-cycle-toggle">
                        <button
                            onClick={() => setIsAnnual(false)}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                                !isAnnual 
                                    ? 'bg-white text-slate-900 shadow-sm' 
                                    : 'text-slate-500 hover:text-slate-700'
                            }`}
                            data-testid="monthly-toggle-btn"
                        >
                            Monthly
                        </button>
                        <button
                            onClick={() => setIsAnnual(true)}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
                                isAnnual 
                                    ? 'bg-white text-slate-900 shadow-sm' 
                                    : 'text-slate-500 hover:text-slate-700'
                            }`}
                            data-testid="annual-toggle-btn"
                        >
                            Annual
                            <span className="bg-emerald-100 text-emerald-700 text-xs font-semibold px-2 py-0.5 rounded-full">
                                Save 17%
                            </span>
                        </button>
                    </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {plans && Object.entries(plans).map(([key, plan]) => (
                        <PlanCard
                            key={key}
                            planKey={key}
                            plan={plan}
                            isCurrentPlan={subscription?.plan === key}
                            subscription={subscription}
                            onSelect={handlePlanChange}
                            loading={changingPlan && selectedPlan === key}
                            isAnnual={isAnnual}
                        />
                    ))}
                </div>
            </div>

            {/* Billing History Placeholder */}
            <div className="bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                    <Receipt className="w-5 h-5 text-slate-400" />
                    Billing History
                </h2>
                
                <div className="text-center py-8 text-slate-500">
                    <Calendar className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                    <p className="text-sm">No billing history yet</p>
                    <p className="text-xs text-slate-400 mt-1">
                        Invoices will appear here once you subscribe to a paid plan
                    </p>
                </div>
            </div>

            {/* Payment Method */}
            <div className="mt-6 bg-white rounded-xl border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                    <CreditCard className="w-5 h-5 text-slate-400" />
                    Payment Method
                </h2>
                
                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-7 bg-gradient-to-r from-indigo-500 to-purple-500 rounded flex items-center justify-center">
                            <CreditCard className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <span className="text-sm font-medium text-slate-700">Secure Stripe Checkout</span>
                            <p className="text-xs text-slate-500">Payment info collected securely at checkout</p>
                        </div>
                    </div>
                </div>
                <p className="text-xs text-slate-400 mt-3">
                    When you subscribe, you'll be redirected to Stripe's secure checkout to enter your payment details.
                </p>
            </div>
        </div>
    );
}
