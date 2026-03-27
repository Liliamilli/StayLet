import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { 
    CreditCard, 
    CheckCircle2, 
    ArrowRight,
    Sparkles
} from 'lucide-react';

const plans = [
    {
        name: 'Starter',
        price: '£9',
        period: '/month',
        description: 'Perfect for hosts with 1-2 properties',
        features: [
            'Up to 2 properties',
            'All compliance tracking',
            'Email reminders',
            'Document storage (1GB)',
            'Basic support'
        ],
        current: false,
        popular: false
    },
    {
        name: 'Professional',
        price: '£29',
        period: '/month',
        description: 'For growing portfolios',
        features: [
            'Up to 10 properties',
            'Everything in Starter',
            'Priority reminders',
            'Document storage (10GB)',
            'Priority support',
            'Compliance reports'
        ],
        current: false,
        popular: true
    },
    {
        name: 'Business',
        price: '£79',
        period: '/month',
        description: 'For property managers',
        features: [
            'Unlimited properties',
            'Everything in Professional',
            'Team access',
            'Document storage (50GB)',
            'Dedicated support',
            'API access',
            'Custom branding'
        ],
        current: false,
        popular: false
    }
];

export default function BillingPage() {
    const navigate = useNavigate();

    return (
        <div data-testid="billing-page">
            {/* Page header */}
            <div className="mb-8">
                <h1 
                    className="text-2xl font-bold text-slate-900 mb-1"
                    style={{ fontFamily: 'Outfit, sans-serif' }}
                >
                    Billing
                </h1>
                <p className="text-slate-500">
                    Manage your subscription and payment methods
                </p>
            </div>

            {/* Current plan */}
            <div className="bg-white rounded-lg border border-slate-200 p-6 mb-8">
                <div className="flex items-start justify-between">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <h2 
                                className="text-lg font-semibold text-slate-900"
                                style={{ fontFamily: 'Outfit, sans-serif' }}
                            >
                                Current Plan
                            </h2>
                            <span className="badge-neutral">Free Trial</span>
                        </div>
                        <p className="text-sm text-slate-500">
                            You're currently on the free trial. Upgrade to unlock all features.
                        </p>
                    </div>
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <CreditCard className="w-6 h-6 text-blue-600" />
                    </div>
                </div>
            </div>

            {/* Available plans */}
            <h2 
                className="text-lg font-semibold text-slate-900 mb-4"
                style={{ fontFamily: 'Outfit, sans-serif' }}
            >
                Available Plans
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {plans.map((plan, index) => (
                    <div 
                        key={index}
                        className={`
                            relative bg-white rounded-lg p-6 border
                            ${plan.popular 
                                ? 'border-blue-600 ring-2 ring-blue-600' 
                                : 'border-slate-200'
                            }
                        `}
                        data-testid={`plan-${plan.name.toLowerCase()}`}
                    >
                        {plan.popular && (
                            <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                                <span className="bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-full inline-flex items-center gap-1">
                                    <Sparkles className="w-3 h-3" />
                                    Most Popular
                                </span>
                            </div>
                        )}

                        <h3 className="text-lg font-semibold text-slate-900 mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
                            {plan.name}
                        </h3>
                        <p className="text-sm text-slate-500 mb-4">{plan.description}</p>
                        
                        <div className="mb-6">
                            <span className="text-3xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                {plan.price}
                            </span>
                            <span className="text-slate-500">{plan.period}</span>
                        </div>

                        <ul className="space-y-2.5 mb-6">
                            {plan.features.map((feature, fIndex) => (
                                <li key={fIndex} className="flex items-start gap-2 text-sm text-slate-600">
                                    <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                                    {feature}
                                </li>
                            ))}
                        </ul>

                        <Button 
                            className={`w-full ${plan.popular ? 'bg-blue-600 hover:bg-blue-700 text-white' : ''}`}
                            variant={plan.popular ? 'default' : 'outline'}
                            data-testid={`upgrade-${plan.name.toLowerCase()}`}
                        >
                            {plan.name === 'Business' ? 'Contact Sales' : 'Upgrade'}
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                    </div>
                ))}
            </div>
        </div>
    );
}
