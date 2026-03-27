import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { 
    Shield, 
    CheckCircle2, 
    Clock, 
    FileText, 
    Bell, 
    Building2,
    ChevronDown,
    ChevronUp,
    ArrowRight,
    Menu,
    X
} from 'lucide-react';

const benefits = [
    {
        icon: Clock,
        title: 'Never Miss a Renewal',
        description: 'Automatic reminders for gas certificates, EPC ratings, and insurance renewals before they expire.'
    },
    {
        icon: FileText,
        title: 'All Documents in One Place',
        description: 'Store and access every certificate, license, and compliance document instantly.'
    },
    {
        icon: Bell,
        title: 'Smart Alerts',
        description: 'Get notified about upcoming deadlines, missing documents, and regulatory changes.'
    },
    {
        icon: Building2,
        title: 'Multi-Property Dashboard',
        description: 'See compliance status across all your properties at a glance. No more spreadsheets.'
    }
];

const pricingPlans = [
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
        cta: 'Start Free Trial',
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
        cta: 'Start Free Trial',
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
        cta: 'Contact Sales',
        popular: false
    }
];

const faqs = [
    {
        question: 'What compliance documents does Staylet track?',
        answer: 'Staylet tracks all key short-let compliance documents including Gas Safety Certificates (CP12), EPC ratings, EICR electrical certificates, PAT testing, fire safety equipment, landlord insurance, and local authority licenses where required.'
    },
    {
        question: 'How do the automatic reminders work?',
        answer: 'You\'ll receive email reminders at 90, 60, 30, and 7 days before any document expires. You can customise these intervals in your settings. Never miss a renewal deadline again.'
    },
    {
        question: 'Can I upload existing documents?',
        answer: 'Yes! You can upload PDFs, images, and other files for all your existing certificates and documents. Staylet will extract key dates and set up automatic tracking.'
    },
    {
        question: 'Is my data secure?',
        answer: 'Absolutely. All data is encrypted at rest and in transit. We use bank-level security standards and are GDPR compliant. Your documents are stored securely in UK data centres.'
    },
    {
        question: 'Can I cancel anytime?',
        answer: 'Yes, you can cancel your subscription at any time. There are no long-term contracts. Your data remains accessible for 30 days after cancellation.'
    }
];

export default function LandingPage() {
    const navigate = useNavigate();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [openFaq, setOpenFaq] = useState(null);

    return (
        <div className="min-h-screen bg-white">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 bg-white/90 backdrop-blur-md border-b border-slate-100 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* Logo */}
                        <Link to="/" className="flex items-center gap-2" data-testid="logo">
                            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                                <Shield className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-semibold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                Staylet
                            </span>
                        </Link>

                        {/* Desktop nav */}
                        <div className="hidden md:flex items-center gap-8">
                            <a href="#benefits" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
                                Benefits
                            </a>
                            <a href="#pricing" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
                                Pricing
                            </a>
                            <a href="#faq" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
                                FAQ
                            </a>
                        </div>

                        {/* Desktop CTA */}
                        <div className="hidden md:flex items-center gap-3">
                            <Button 
                                variant="ghost" 
                                onClick={() => navigate('/login')}
                                data-testid="nav-login-btn"
                            >
                                Sign in
                            </Button>
                            <Button 
                                className="bg-blue-600 hover:bg-blue-700 text-white"
                                onClick={() => navigate('/signup')}
                                data-testid="nav-signup-btn"
                            >
                                Start Free Trial
                            </Button>
                        </div>

                        {/* Mobile menu button */}
                        <button 
                            className="md:hidden p-2"
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            data-testid="mobile-nav-btn"
                        >
                            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                        </button>
                    </div>
                </div>

                {/* Mobile menu */}
                {mobileMenuOpen && (
                    <div className="md:hidden bg-white border-t border-slate-100 py-4 px-4">
                        <div className="flex flex-col gap-4">
                            <a href="#benefits" className="text-sm font-medium text-slate-600" onClick={() => setMobileMenuOpen(false)}>
                                Benefits
                            </a>
                            <a href="#pricing" className="text-sm font-medium text-slate-600" onClick={() => setMobileMenuOpen(false)}>
                                Pricing
                            </a>
                            <a href="#faq" className="text-sm font-medium text-slate-600" onClick={() => setMobileMenuOpen(false)}>
                                FAQ
                            </a>
                            <hr className="border-slate-200" />
                            <Button 
                                variant="outline" 
                                className="w-full"
                                onClick={() => navigate('/login')}
                            >
                                Sign in
                            </Button>
                            <Button 
                                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                                onClick={() => navigate('/signup')}
                            >
                                Start Free Trial
                            </Button>
                        </div>
                    </div>
                )}
            </nav>

            {/* Hero Section */}
            <section className="pt-32 pb-20 md:pt-40 md:pb-32 hero-pattern">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="max-w-3xl mx-auto text-center">
                        <h1 
                            className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 mb-6 tracking-tight"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                            data-testid="hero-headline"
                        >
                            Short-let compliance,{' '}
                            <span className="text-blue-600">handled.</span>
                        </h1>
                        
                        <p 
                            className="text-lg text-slate-600 mb-10 max-w-2xl mx-auto"
                            data-testid="hero-subheadline"
                        >
                            Track every certificate, document, and deadline across your properties without spreadsheets or missed renewals.
                        </p>

                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Button 
                                size="lg"
                                className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-base"
                                onClick={() => navigate('/signup')}
                                data-testid="hero-cta-trial"
                            >
                                Start Free Trial
                                <ArrowRight className="w-4 h-4 ml-2" />
                            </Button>
                            <Button 
                                size="lg"
                                variant="outline"
                                className="w-full sm:w-auto px-8 py-3 text-base"
                                data-testid="hero-cta-demo"
                            >
                                See Demo
                            </Button>
                        </div>

                        <p className="mt-6 text-sm text-slate-500">
                            No credit card required • 14-day free trial • Cancel anytime
                        </p>
                    </div>
                </div>
            </section>

            {/* Benefits Section */}
            <section id="benefits" className="py-20 md:py-28 bg-slate-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 
                            className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Everything you need for compliance peace of mind
                        </h2>
                        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                            Built specifically for UK short-term let hosts managing 1-15 properties.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {benefits.map((benefit, index) => {
                            const Icon = benefit.icon;
                            return (
                                <div 
                                    key={index}
                                    className="bg-white rounded-xl p-8 border border-slate-200 hover:shadow-lg hover:border-slate-300 transition-all"
                                    data-testid={`benefit-${index}`}
                                >
                                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-5">
                                        <Icon className="w-6 h-6 text-blue-600" />
                                    </div>
                                    <h3 className="text-xl font-semibold text-slate-900 mb-3" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                        {benefit.title}
                                    </h3>
                                    <p className="text-slate-600">
                                        {benefit.description}
                                    </p>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </section>

            {/* Pricing Section */}
            <section id="pricing" className="py-20 md:py-28">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 
                            className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Simple, transparent pricing
                        </h2>
                        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                            Start free, upgrade when you're ready. No hidden fees.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        {pricingPlans.map((plan, index) => (
                            <div 
                                key={index}
                                className={`
                                    relative bg-white rounded-xl p-8 border
                                    ${plan.popular 
                                        ? 'border-blue-600 ring-2 ring-blue-600 shadow-lg' 
                                        : 'border-slate-200 hover:border-slate-300'
                                    }
                                    transition-all
                                `}
                                data-testid={`pricing-${plan.name.toLowerCase()}`}
                            >
                                {plan.popular && (
                                    <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                                        <span className="bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
                                            Most Popular
                                        </span>
                                    </div>
                                )}

                                <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                    {plan.name}
                                </h3>
                                <p className="text-sm text-slate-500 mb-4">{plan.description}</p>
                                
                                <div className="mb-6">
                                    <span className="text-4xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                        {plan.price}
                                    </span>
                                    <span className="text-slate-500">{plan.period}</span>
                                </div>

                                <ul className="space-y-3 mb-8">
                                    {plan.features.map((feature, fIndex) => (
                                        <li key={fIndex} className="flex items-start gap-3 text-sm text-slate-600">
                                            <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                                            {feature}
                                        </li>
                                    ))}
                                </ul>

                                <Button 
                                    className={`w-full ${plan.popular ? 'bg-blue-600 hover:bg-blue-700 text-white' : ''}`}
                                    variant={plan.popular ? 'default' : 'outline'}
                                    onClick={() => navigate('/signup')}
                                    data-testid={`pricing-cta-${plan.name.toLowerCase()}`}
                                >
                                    {plan.cta}
                                </Button>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* FAQ Section */}
            <section id="faq" className="py-20 md:py-28 bg-slate-50">
                <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <h2 
                            className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Frequently asked questions
                        </h2>
                        <p className="text-lg text-slate-600">
                            Got questions? We've got answers.
                        </p>
                    </div>

                    <div className="space-y-4">
                        {faqs.map((faq, index) => (
                            <div 
                                key={index}
                                className="bg-white rounded-lg border border-slate-200 overflow-hidden"
                                data-testid={`faq-${index}`}
                            >
                                <button
                                    className="w-full flex items-center justify-between p-5 text-left"
                                    onClick={() => setOpenFaq(openFaq === index ? null : index)}
                                >
                                    <span className="font-medium text-slate-900">{faq.question}</span>
                                    {openFaq === index 
                                        ? <ChevronUp className="w-5 h-5 text-slate-400" />
                                        : <ChevronDown className="w-5 h-5 text-slate-400" />
                                    }
                                </button>
                                {openFaq === index && (
                                    <div className="px-5 pb-5">
                                        <p className="text-slate-600">{faq.answer}</p>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Final CTA Section */}
            <section className="py-20 md:py-28">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <h2 
                        className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4"
                        style={{ fontFamily: 'Outfit, sans-serif' }}
                    >
                        Ready to simplify your compliance?
                    </h2>
                    <p className="text-lg text-slate-600 mb-10 max-w-2xl mx-auto">
                        Join hundreds of UK short-let hosts who trust Staylet to keep their properties compliant.
                    </p>
                    
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Button 
                            size="lg"
                            className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-base"
                            onClick={() => navigate('/signup')}
                            data-testid="final-cta-trial"
                        >
                            Start Your Free Trial
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                        <Button 
                            size="lg"
                            variant="outline"
                            className="w-full sm:w-auto px-8 py-3 text-base"
                            data-testid="final-cta-demo"
                        >
                            Book a Demo
                        </Button>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-slate-900 py-12">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                                <Shield className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-lg font-semibold text-white" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                Staylet
                            </span>
                        </div>
                        
                        <p className="text-sm text-slate-400">
                            © 2025 Staylet. All rights reserved.
                        </p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
