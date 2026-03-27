"""
Constants and configuration for Staylet.
"""
import os

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'staylet-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# UK-specific constants
UK_NATIONS = ["England", "Scotland", "Wales", "Northern Ireland"]
PROPERTY_TYPES = ["apartment", "house", "studio", "maisonette", "bungalow", "townhouse", "detached", "semi-detached", "terraced", "other"]
OWNERSHIP_TYPES = ["owned", "leased", "managed_for_owner", "rent_to_rent", "other"]

# Compliance categories
COMPLIANCE_CATEGORIES = ["gas_safety", "eicr", "epc", "insurance", "fire_risk_assessment", "pat_testing", "legionella", "smoke_co_alarms", "licence", "custom"]
COMPLIANCE_STATUS = ["compliant", "expiring_soon", "overdue", "missing"]
REMINDER_OPTIONS = ["none", "30_days", "60_days", "90_days"]

# Task constants
TASK_STATUSES = ["pending", "in_progress", "completed"]
TASK_PRIORITIES = ["low", "medium", "high", "urgent"]
TASK_CATEGORIES = ["general", "maintenance", "inspection", "renewal", "safety", "seasonal", "admin"]

# Notification constants
NOTIFICATION_TYPES = ["expiry_reminder", "overdue_alert", "task_due", "missing_record", "system"]
REMINDER_INTERVALS = [90, 60, 30, 7, 0]  # Days before expiry (0 = overdue)

# Subscription Plans
SUBSCRIPTION_PLANS = {
    "solo": {
        "name": "Solo",
        "price_monthly": 19,
        "price_yearly": 190,
        "property_limit": 1,
        "features": ["1 property", "Compliance tracking", "Document storage", "Email reminders", "Task management"]
    },
    "portfolio": {
        "name": "Portfolio",
        "price_monthly": 39,
        "price_yearly": 390,
        "property_limit": 5,
        "features": ["Up to 5 properties", "Everything in Solo", "Priority support", "Bulk compliance setup", "Advanced reports"]
    },
    "operator": {
        "name": "Operator",
        "price_monthly": 79,
        "price_yearly": 790,
        "property_limit": 15,
        "features": ["Up to 15 properties", "Everything in Portfolio", "API access", "Team members (coming soon)", "Custom integrations"]
    }
}
SUBSCRIPTION_STATUSES = ["trial", "active", "past_due", "cancelled", "expired"]
TRIAL_DAYS = 14

# Stripe Configuration
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')

# Category labels for display
CATEGORY_LABELS = {
    'gas_safety': 'Gas Safety Certificate',
    'eicr': 'EICR',
    'epc': 'EPC',
    'insurance': 'Insurance',
    'fire_risk_assessment': 'Fire Risk Assessment',
    'pat_testing': 'PAT Testing',
    'legionella': 'Legionella Risk Assessment',
    'smoke_co_alarms': 'Smoke/CO Alarms',
    'licence': 'Licence',
    'custom': 'Custom'
}
