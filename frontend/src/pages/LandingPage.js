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
        name: 'Solo',
        monthlyPrice: 19,
        yearlyPrice: 190,
        description: 'Perfect for single property hosts',
        features: [
            '1 property',
            'Full compliance tracking',
            'Document storage',
            'Email reminders',
            'Task management',
            'Mobile access'
        ],
        cta: 'Start Free Trial',
        popular: false,
        icon: Building2
    },
    {
        name: 'Portfolio',
        monthlyPrice: 39,
        yearlyPrice: 390,
        description: 'For hosts with multiple properties',
        features: [
            'Up to 5 properties',
            'Everything in Solo',
            'Priority support',
            'Bulk compliance setup',
            'Advanced reports',
            'Smart document extraction'
        ],
        cta: 'Start Free Trial',
        popular: true,
        icon: Shield
    },
    {
        name: 'Operator',
        monthlyPrice: 79,
        yearlyPrice: 790,
        description: 'For professional property managers',
        features: [
            'Up to 15 properties',
            'Everything in Portfolio',
            'API access',
            'Team members (coming soon)',
            'Custom integrations',
            'Dedicated support'
        ],
        cta: 'Start Free Trial',
        popular: false,
        icon: Clock
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
    const [isAnnual, setIsAnnual] = useState(false);

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
                    <div className="text-center mb-12">
                        <span className="inline-block px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4">
                            Pricing
                        </span>
                        <h2 
                            className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Simple, transparent pricing
                        </h2>
                        <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-8">
                            14-day free trial on all plans. No credit card required.
                        </p>
                        
                        {/* Annual/Monthly Toggle */}
                        <div className="flex items-center justify-center gap-3 bg-slate-100 rounded-lg p-1 w-fit mx-auto" data-testid="landing-billing-toggle">
                            <button
                                onClick={() => setIsAnnual(false)}
                                className={`px-5 py-2.5 rounded-md text-sm font-medium transition-all ${
                                    !isAnnual 
                                        ? 'bg-white text-slate-900 shadow-sm' 
                                        : 'text-slate-500 hover:text-slate-700'
                                }`}
                                data-testid="landing-monthly-toggle"
                            >
                                Monthly
                            </button>
                            <button
                                onClick={() => setIsAnnual(true)}
                                className={`px-5 py-2.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
                                    isAnnual 
                                        ? 'bg-white text-slate-900 shadow-sm' 
                                        : 'text-slate-500 hover:text-slate-700'
                                }`}
                                data-testid="landing-annual-toggle"
                            >
                                Annual
                                <span className="bg-emerald-100 text-emerald-700 text-xs font-semibold px-2 py-0.5 rounded-full">
                                    Save 17%
                                </span>
                            </button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                        {pricingPlans.map((plan, index) => {
                            const Icon = plan.icon;
                            const displayPrice = isAnnual ? Math.round(plan.yearlyPrice / 12) : plan.monthlyPrice;
                            const savings = (plan.monthlyPrice * 12) - plan.yearlyPrice;
                            
                            return (
                                <div 
                                    key={index}
                                    className={`
                                        relative bg-white rounded-2xl p-8 border-2 transition-all
                                        ${plan.popular 
                                            ? 'border-blue-600 ring-4 ring-blue-100 shadow-xl scale-105 z-10' 
                                            : 'border-slate-200 hover:border-blue-300 hover:shadow-lg'
                                        }
                                    `}
                                    data-testid={`pricing-${plan.name.toLowerCase()}`}
                                >
                                    {plan.popular && (
                                        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                                            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-xs font-semibold px-4 py-1.5 rounded-full shadow-lg">
                                                Most Popular
                                            </span>
                                        </div>
                                    )}
                                    
                                    {isAnnual && (
                                        <div className="absolute -top-3 right-4">
                                            <span className="bg-emerald-500 text-white text-xs font-semibold px-2 py-1 rounded-full">
                                                Save £{savings}/yr
                                            </span>
                                        </div>
                                    )}

                                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${
                                        plan.popular ? 'bg-blue-100' : 'bg-slate-100'
                                    }`}>
                                        <Icon className={`w-6 h-6 ${plan.popular ? 'text-blue-600' : 'text-slate-600'}`} />
                                    </div>

                                    <h3 className="text-xl font-bold text-slate-900 mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                        {plan.name}
                                    </h3>
                                    <p className="text-sm text-slate-500 mb-4">{plan.description}</p>
                                    
                                    <div className="mb-2">
                                        <span className="text-4xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                            £{displayPrice}
                                        </span>
                                        <span className="text-slate-500">/month</span>
                                    </div>
                                    <p className="text-sm text-slate-400 mb-6">
                                        {isAnnual ? (
                                            <>£{plan.yearlyPrice} billed annually</>
                                        ) : (
                                            <>or £{plan.yearlyPrice}/year <span className="text-emerald-600">(save 17%)</span></>
                                        )}
                                    </p>

                                    <ul className="space-y-3 mb-8">
                                        {plan.features.map((feature, fIndex) => (
                                            <li key={fIndex} className="flex items-start gap-3 text-sm text-slate-600">
                                                <CheckCircle2 className={`w-5 h-5 flex-shrink-0 ${plan.popular ? 'text-blue-500' : 'text-emerald-500'}`} />
                                                {feature}
                                            </li>
                                        ))}
                                    </ul>

                                    <Button 
                                        className={`w-full h-12 font-semibold ${plan.popular 
                                            ? 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg' 
                                            : 'border-2 border-slate-200 hover:border-blue-300 hover:bg-blue-50'
                                        }`}
                                        variant={plan.popular ? 'default' : 'outline'}
                                        onClick={() => navigate('/signup')}
                                        data-testid={`pricing-cta-${plan.name.toLowerCase()}`}
                                    >
                                        {plan.cta}
                                        {plan.popular && <ArrowRight className="w-4 h-4 ml-2" />}
                                    </Button>
                                </div>
                            );
                        })}
                    </div>

                    <p className="text-center text-sm text-slate-500 mt-8">
                        All plans include a 14-day free trial. Cancel anytime.
                    </p>
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
