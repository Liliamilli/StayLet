import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
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
    X,
    AlertTriangle,
    Calendar,
    Upload,
    Search,
    Zap,
    Users,
    Lock,
    Star,
    FileCheck,
    ClipboardList,
    Sparkles,
    Loader2
} from 'lucide-react';

// Problem points that resonate with hosts
const painPoints = [
    {
        icon: AlertTriangle,
        title: 'Expired certificates you forgot about',
        description: 'That gas safety cert from 18 months ago? Council fines start at £5,000.'
    },
    {
        icon: FileText,
        title: 'Scattered documents everywhere',
        description: 'Emails, folders, filing cabinets. Finding that EICR takes 20 minutes.'
    },
    {
        icon: Calendar,
        title: 'Manual calendar reminders',
        description: 'Sticky notes and spreadsheets are not a compliance system.'
    },
    {
        icon: ClipboardList,
        title: 'No clear view across properties',
        description: 'Which property needs what? You shouldn\'t have to guess.'
    }
];

// How it works steps
const howItWorks = [
    {
        step: '01',
        title: 'Add your properties',
        description: 'Enter your property details in under 2 minutes. We\'ll set up tracking for all required UK compliance certificates automatically.',
        icon: Building2
    },
    {
        step: '02',
        title: 'Upload or scan documents',
        description: 'Drop in your existing certificates. Our AI reads the dates and sets up reminders. No manual data entry needed.',
        icon: Upload
    },
    {
        step: '03',
        title: 'Stay ahead of deadlines',
        description: 'Get alerts before anything expires. See what\'s missing, what\'s due, and what\'s sorted—across every property.',
        icon: Bell
    }
];

// Core benefits
const benefits = [
    {
        icon: Clock,
        title: 'Never miss a renewal',
        description: 'Automatic alerts at 90, 60, 30, and 7 days before expiry. Customise the schedule to fit how you work.',
        stat: '90 days',
        statLabel: 'advance warning'
    },
    {
        icon: FileCheck,
        title: 'One place for everything',
        description: 'Gas certs, EICRs, EPCs, insurance, licenses—all stored securely and instantly searchable.',
        stat: '100%',
        statLabel: 'document coverage'
    },
    {
        icon: Shield,
        title: 'Always audit-ready',
        description: 'Council inspection? Guest complaint? Pull up any certificate in seconds, not hours.',
        stat: '<30 sec',
        statLabel: 'to find any document'
    },
    {
        icon: Building2,
        title: 'See all properties at once',
        description: 'Dashboard shows compliance status across your entire portfolio. Red flags stand out immediately.',
        stat: '1-15',
        statLabel: 'properties supported'
    }
];

// Feature highlights
const features = [
    {
        title: 'Smart document extraction',
        description: 'Upload a certificate and we\'ll automatically read the dates, document type, and set up tracking.',
        icon: Sparkles
    },
    {
        title: 'UK compliance built-in',
        description: 'Gas Safety (CP12), EICR, EPC, PAT, Fire Safety, Legionella, Insurance, HMO licenses—all covered.',
        icon: FileText
    },
    {
        title: 'Task management',
        description: 'Create to-dos linked to properties. Recurring tasks for regular inspections. Nothing falls through.',
        icon: ClipboardList
    },
    {
        title: 'Secure cloud storage',
        description: 'Bank-level encryption. UK data centres. GDPR compliant. Your documents are safer than in a filing cabinet.',
        icon: Lock
    },
    {
        title: 'Works on any device',
        description: 'Check compliance status from your phone, tablet, or laptop. Access documents anywhere.',
        icon: Search
    },
    {
        title: 'No learning curve',
        description: 'If you can use email, you can use Staylet. Most hosts are fully set up in under 15 minutes.',
        icon: Zap
    }
];

// Testimonials (placeholder)
const testimonials = [
    {
        quote: "I used to spend Sunday evenings updating spreadsheets. Now I just check Staylet once a week. It's completely changed how I manage my properties.",
        name: 'Sarah M.',
        role: '4 properties, Manchester',
        avatar: 'SM'
    },
    {
        quote: "Got a council inspection last month. Pulled up every certificate in about 30 seconds. The inspector was impressed. I was relieved.",
        name: 'James T.',
        role: '7 properties, London',
        avatar: 'JT'
    },
    {
        quote: "Missed a gas cert renewal last year and it cost me £1,200 in emergency fees. That won't happen again with Staylet.",
        name: 'Priya K.',
        role: '2 properties, Bristol',
        avatar: 'PK'
    }
];

// Pricing plans
const pricingPlans = [
    {
        name: 'Solo',
        monthlyPrice: 19,
        yearlyPrice: 190,
        description: 'For hosts with a single property',
        features: [
            '1 property',
            'All compliance tracking',
            'Unlimited document storage',
            'Email reminders',
            'Task management',
            'Mobile access'
        ],
        cta: 'Start Free Trial',
        popular: false,
        highlight: 'Perfect for starting out'
    },
    {
        name: 'Portfolio',
        monthlyPrice: 39,
        yearlyPrice: 390,
        description: 'For growing property portfolios',
        features: [
            'Up to 5 properties',
            'Everything in Solo',
            'Smart document extraction',
            'Bulk compliance setup',
            'Priority support',
            'Advanced reports'
        ],
        cta: 'Start Free Trial',
        popular: true,
        highlight: 'Most popular'
    },
    {
        name: 'Operator',
        monthlyPrice: 79,
        yearlyPrice: 790,
        description: 'For professional managers',
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
        highlight: 'For serious operators'
    }
];

// FAQ
const faqs = [
    {
        question: 'What compliance documents does Staylet track?',
        answer: 'All the essential UK short-let certificates: Gas Safety (CP12), EICR electrical certificates, EPC ratings, PAT testing, fire safety equipment, smoke and CO alarms, legionella risk assessments, landlord insurance, and local authority licenses (like Airbnb registration in Edinburgh or selective licensing in certain areas).'
    },
    {
        question: 'How do the automatic reminders work?',
        answer: 'When you add a document with an expiry date, we automatically schedule email reminders at 90, 60, 30, and 7 days before it expires. You can adjust these intervals or add custom reminder dates in your settings. No more relying on memory or calendar apps.'
    },
    {
        question: 'Can I upload my existing documents?',
        answer: 'Yes—that\'s the quickest way to get started. Upload PDFs or photos of your certificates. Our AI will read the key information (dates, document type, address) and set up tracking automatically. You can review and adjust anything before saving.'
    },
    {
        question: 'Is my data secure?',
        answer: 'Absolutely. We use bank-level encryption (AES-256) for all stored data and TLS 1.3 for data in transit. Documents are stored in UK data centres. We\'re fully GDPR compliant. Your documents are more secure with us than in a filing cabinet.'
    },
    {
        question: 'What if I manage properties in different UK nations?',
        answer: 'Staylet handles the different requirements across England, Scotland, Wales, and Northern Ireland. We track nation-specific requirements like Scotland\'s short-term let licensing and different EPC rules. Just tell us where each property is located.'
    },
    {
        question: 'Can I try it before paying?',
        answer: 'Yes. Every plan includes a 14-day free trial with full access to all features. No credit card required to start. If Staylet isn\'t right for you, just don\'t subscribe—no questions asked.'
    },
    {
        question: 'How long does setup take?',
        answer: 'Most hosts add their first property and upload existing documents in under 15 minutes. If you\'re using our "Quick Setup" feature, we\'ll create tracking for all standard UK compliance requirements automatically—you just upload the certificates you have.'
    },
    {
        question: 'Can I cancel anytime?',
        answer: 'Yes. No long-term contracts or cancellation fees. Cancel from your account settings whenever you want. Your data remains accessible for 30 days after cancellation so you can export anything you need.'
    }
];

// Trust signals
const trustSignals = [
    { label: 'UK-based', icon: Shield },
    { label: 'GDPR Compliant', icon: Lock },
    { label: 'Encrypted Storage', icon: FileCheck },
    { label: '99.9% Uptime', icon: Zap }
];

export default function LandingPage() {
    const navigate = useNavigate();
    const { startDemo } = useAuth();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [openFaq, setOpenFaq] = useState(null);
    const [isAnnual, setIsAnnual] = useState(false);
    const [demoLoading, setDemoLoading] = useState(false);

    const handleStartDemo = async () => {
        setDemoLoading(true);
        try {
            await startDemo();
            navigate('/app');
        } catch (error) {
            console.error('Failed to start demo:', error);
            alert('Failed to start demo. Please try again.');
        } finally {
            setDemoLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-white">
            {/* Navigation */}
            <nav className="fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-md border-b border-slate-100 z-50">
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
                            <a href="#how-it-works" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
                                How it Works
                            </a>
                            <a href="#features" className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
                                Features
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
                            <a href="#how-it-works" className="text-sm font-medium text-slate-600" onClick={() => setMobileMenuOpen(false)}>
                                How it Works
                            </a>
                            <a href="#features" className="text-sm font-medium text-slate-600" onClick={() => setMobileMenuOpen(false)}>
                                Features
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

            {/* ============ HERO SECTION ============ */}
            <section className="pt-28 pb-16 md:pt-36 md:pb-24 bg-gradient-to-b from-slate-50 to-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="max-w-4xl mx-auto text-center">
                        {/* Trust badge */}
                        <div className="inline-flex items-center gap-2 bg-emerald-50 text-emerald-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
                            <Shield className="w-4 h-4" />
                            <span>Built for UK short-let hosts</span>
                        </div>

                        <h1 
                            className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 mb-6 tracking-tight leading-tight"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                            data-testid="hero-headline"
                        >
                            Stop chasing certificates.
                            <br />
                            <span className="text-blue-600">Start staying compliant.</span>
                        </h1>
                        
                        <p 
                            className="text-lg md:text-xl text-slate-600 mb-8 max-w-2xl mx-auto leading-relaxed"
                            data-testid="hero-subheadline"
                        >
                            Track gas certs, EICRs, insurance, and every compliance deadline across all your properties. 
                            No spreadsheets. No missed renewals. No more stress.
                        </p>

                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-6">
                            <Button 
                                size="lg"
                                className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-base font-semibold shadow-lg shadow-blue-600/20"
                                onClick={() => navigate('/signup')}
                                data-testid="hero-cta-trial"
                            >
                                Start Your Free Trial
                                <ArrowRight className="w-5 h-5 ml-2" />
                            </Button>
                            <Button 
                                size="lg"
                                variant="outline"
                                className="w-full sm:w-auto px-8 py-6 text-base font-medium border-2"
                                onClick={handleStartDemo}
                                disabled={demoLoading}
                                data-testid="hero-cta-demo"
                            >
                                {demoLoading ? (
                                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                                ) : (
                                    <Sparkles className="w-5 h-5 mr-2 text-blue-600" />
                                )}
                                {demoLoading ? 'Loading Demo...' : 'Try Demo Mode'}
                            </Button>
                        </div>

                        <p className="text-sm text-slate-500 mb-12">
                            14-day free trial • No credit card required • Set up in 15 minutes
                        </p>

                        {/* Trust signals row */}
                        <div className="flex flex-wrap items-center justify-center gap-6 pt-8 border-t border-slate-200">
                            {trustSignals.map((signal, index) => {
                                const Icon = signal.icon;
                                return (
                                    <div key={index} className="flex items-center gap-2 text-slate-500">
                                        <Icon className="w-4 h-4" />
                                        <span className="text-sm font-medium">{signal.label}</span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            </section>

            {/* ============ PROBLEM SECTION ============ */}
            <section className="py-16 md:py-24 bg-slate-900 text-white">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="max-w-3xl mx-auto text-center mb-12">
                        <h2 
                            className="text-3xl sm:text-4xl font-bold mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Sound familiar?
                        </h2>
                        <p className="text-lg text-slate-400">
                            You got into property to build income, not to become a document administrator.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                        {painPoints.map((point, index) => {
                            const Icon = point.icon;
                            return (
                                <div 
                                    key={index}
                                    className="bg-slate-800/50 rounded-xl p-6 border border-slate-700"
                                >
                                    <div className="flex items-start gap-4">
                                        <div className="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                                            <Icon className="w-5 h-5 text-red-400" />
                                        </div>
                                        <div>
                                            <h3 className="font-semibold text-white mb-1">
                                                {point.title}
                                            </h3>
                                            <p className="text-slate-400 text-sm">
                                                {point.description}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div className="text-center mt-12">
                        <p className="text-slate-400 mb-6">There's a better way.</p>
                        <a href="#how-it-works" className="inline-flex items-center gap-2 text-blue-400 font-medium hover:text-blue-300 transition-colors">
                            See how Staylet helps
                            <ArrowRight className="w-4 h-4" />
                        </a>
                    </div>
                </div>
            </section>

            {/* ============ HOW IT WORKS ============ */}
            <section id="how-it-works" className="py-16 md:py-24">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <span className="inline-block px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4">
                            How it Works
                        </span>
                        <h2 
                            className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            From chaos to clarity in three steps
                        </h2>
                        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                            Most hosts are fully set up and tracking compliance within 15 minutes.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        {howItWorks.map((step, index) => {
                            const Icon = step.icon;
                            return (
                                <div key={index} className="relative">
                                    {/* Connector line */}
                                    {index < howItWorks.length - 1 && (
                                        <div className="hidden md:block absolute top-12 left-full w-full h-0.5 bg-slate-200 -translate-y-1/2 z-0" style={{ width: 'calc(100% - 2rem)' }} />
                                    )}
                                    
                                    <div className="relative z-10 text-center">
                                        <div className="inline-flex items-center justify-center w-24 h-24 bg-blue-50 rounded-2xl mb-6">
                                            <Icon className="w-10 h-10 text-blue-600" />
                                        </div>
                                        <div className="text-sm font-bold text-blue-600 mb-2">{step.step}</div>
                                        <h3 className="text-xl font-semibold text-slate-900 mb-3" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                            {step.title}
                                        </h3>
                                        <p className="text-slate-600">
                                            {step.description}
                                        </p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div className="text-center mt-12">
                        <Button 
                            size="lg"
                            className="bg-blue-600 hover:bg-blue-700 text-white"
                            onClick={() => navigate('/signup')}
                        >
                            Get Started Free
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                    </div>
                </div>
            </section>

            {/* ============ BENEFITS SECTION ============ */}
            <section id="benefits" className="py-16 md:py-24 bg-slate-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <span className="inline-block px-4 py-1.5 bg-emerald-100 text-emerald-700 rounded-full text-sm font-medium mb-4">
                            Benefits
                        </span>
                        <h2 
                            className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            What you actually get
                        </h2>
                        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                            Less admin. More peace of mind. Full visibility across your portfolio.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {benefits.map((benefit, index) => {
                            const Icon = benefit.icon;
                            return (
                                <div 
                                    key={index}
                                    className="bg-white rounded-2xl p-8 border border-slate-200 hover:shadow-xl hover:border-slate-300 transition-all group"
                                    data-testid={`benefit-${index}`}
                                >
                                    <div className="flex items-start gap-5">
                                        <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:bg-blue-600 transition-colors">
                                            <Icon className="w-7 h-7 text-blue-600 group-hover:text-white transition-colors" />
                                        </div>
                                        <div className="flex-1">
                                            <h3 className="text-xl font-semibold text-slate-900 mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                                {benefit.title}
                                            </h3>
                                            <p className="text-slate-600 mb-4">
                                                {benefit.description}
                                            </p>
                                            <div className="flex items-baseline gap-2">
                                                <span className="text-2xl font-bold text-blue-600">{benefit.stat}</span>
                                                <span className="text-sm text-slate-500">{benefit.statLabel}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </section>

            {/* ============ FEATURES SECTION ============ */}
            <section id="features" className="py-16 md:py-24">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-16">
                        <span className="inline-block px-4 py-1.5 bg-purple-100 text-purple-700 rounded-full text-sm font-medium mb-4">
                            Features
                        </span>
                        <h2 
                            className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Everything you need, nothing you don't
                        </h2>
                        <p className="text-lg text-slate-600 max-w-2xl mx-auto">
                            Built specifically for UK short-let hosts. No bloat, no complexity.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {features.map((feature, index) => {
                            const Icon = feature.icon;
                            return (
                                <div 
                                    key={index}
                                    className="bg-white rounded-xl p-6 border border-slate-200 hover:border-blue-200 hover:shadow-md transition-all"
                                >
                                    <div className="w-12 h-12 bg-slate-100 rounded-lg flex items-center justify-center mb-4">
                                        <Icon className="w-6 h-6 text-slate-700" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                        {feature.title}
                                    </h3>
                                    <p className="text-slate-600 text-sm">
                                        {feature.description}
                                    </p>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </section>

            {/* ============ TESTIMONIALS SECTION ============ */}
            <section className="py-16 md:py-24 bg-blue-600">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-12">
                        <h2 
                            className="text-3xl sm:text-4xl font-bold text-white mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Trusted by UK hosts
                        </h2>
                        <p className="text-lg text-blue-100">
                            See why property operators choose Staylet
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {testimonials.map((testimonial, index) => (
                            <div 
                                key={index}
                                className="bg-white rounded-2xl p-6 shadow-lg"
                            >
                                <div className="flex gap-1 mb-4">
                                    {[...Array(5)].map((_, i) => (
                                        <Star key={i} className="w-5 h-5 fill-amber-400 text-amber-400" />
                                    ))}
                                </div>
                                <p className="text-slate-700 mb-6 italic">
                                    "{testimonial.quote}"
                                </p>
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                                        <span className="text-sm font-semibold text-blue-600">{testimonial.avatar}</span>
                                    </div>
                                    <div>
                                        <div className="font-semibold text-slate-900">{testimonial.name}</div>
                                        <div className="text-sm text-slate-500">{testimonial.role}</div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ============ PRICING SECTION ============ */}
            <section id="pricing" className="py-16 md:py-24">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-12">
                        <span className="inline-block px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4">
                            Pricing
                        </span>
                        <h2 
                            className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Simple pricing that scales with you
                        </h2>
                        <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-8">
                            Start free for 14 days. No credit card needed. Upgrade when you're ready.
                        </p>
                        
                        {/* Annual/Monthly Toggle */}
                        <div className="flex items-center justify-center gap-3 bg-slate-100 rounded-full p-1.5 w-fit mx-auto" data-testid="landing-billing-toggle">
                            <button
                                onClick={() => setIsAnnual(false)}
                                className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
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
                                className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${
                                    isAnnual 
                                        ? 'bg-white text-slate-900 shadow-sm' 
                                        : 'text-slate-500 hover:text-slate-700'
                                }`}
                                data-testid="landing-annual-toggle"
                            >
                                Annual
                                <span className="bg-emerald-500 text-white text-xs font-semibold px-2 py-0.5 rounded-full">
                                    2 months free
                                </span>
                            </button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                        {pricingPlans.map((plan, index) => {
                            const displayPrice = isAnnual ? Math.round(plan.yearlyPrice / 12) : plan.monthlyPrice;
                            const savings = (plan.monthlyPrice * 12) - plan.yearlyPrice;
                            
                            return (
                                <div 
                                    key={index}
                                    className={`
                                        relative bg-white rounded-2xl p-8 transition-all
                                        ${plan.popular 
                                            ? 'border-2 border-blue-600 shadow-xl shadow-blue-600/10 scale-105 z-10' 
                                            : 'border border-slate-200 hover:border-slate-300 hover:shadow-lg'
                                        }
                                    `}
                                    data-testid={`pricing-${plan.name.toLowerCase()}`}
                                >
                                    {plan.popular && (
                                        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                                            <span className="bg-blue-600 text-white text-xs font-semibold px-4 py-1.5 rounded-full">
                                                Most Popular
                                            </span>
                                        </div>
                                    )}

                                    <div className="text-sm font-medium text-blue-600 mb-2">{plan.highlight}</div>
                                    <h3 className="text-2xl font-bold text-slate-900 mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                        {plan.name}
                                    </h3>
                                    <p className="text-sm text-slate-500 mb-6">{plan.description}</p>
                                    
                                    <div className="mb-2">
                                        <span className="text-4xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                            £{displayPrice}
                                        </span>
                                        <span className="text-slate-500">/month</span>
                                    </div>
                                    <p className="text-sm text-slate-400 mb-6">
                                        {isAnnual ? (
                                            <span className="text-emerald-600">£{plan.yearlyPrice}/year (save £{savings})</span>
                                        ) : (
                                            <>Billed monthly</>
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
                                            ? 'bg-blue-600 hover:bg-blue-700 text-white' 
                                            : 'border-2 border-slate-200 hover:border-blue-600 hover:text-blue-600'
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
                        All plans include a 14-day free trial. Cancel anytime—no questions asked.
                    </p>
                </div>
            </section>

            {/* ============ FAQ SECTION ============ */}
            <section id="faq" className="py-16 md:py-24 bg-slate-50">
                <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="text-center mb-12">
                        <span className="inline-block px-4 py-1.5 bg-slate-200 text-slate-700 rounded-full text-sm font-medium mb-4">
                            FAQ
                        </span>
                        <h2 
                            className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Common questions
                        </h2>
                        <p className="text-lg text-slate-600">
                            Everything you need to know before getting started
                        </p>
                    </div>

                    <div className="space-y-4">
                        {faqs.map((faq, index) => (
                            <div 
                                key={index}
                                className="bg-white rounded-xl border border-slate-200 overflow-hidden"
                                data-testid={`faq-${index}`}
                            >
                                <button
                                    className="w-full px-6 py-5 flex items-center justify-between text-left"
                                    onClick={() => setOpenFaq(openFaq === index ? null : index)}
                                >
                                    <span className="font-semibold text-slate-900 pr-4">{faq.question}</span>
                                    {openFaq === index ? (
                                        <ChevronUp className="w-5 h-5 text-slate-400 flex-shrink-0" />
                                    ) : (
                                        <ChevronDown className="w-5 h-5 text-slate-400 flex-shrink-0" />
                                    )}
                                </button>
                                {openFaq === index && (
                                    <div className="px-6 pb-5 text-slate-600">
                                        {faq.answer}
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ============ FINAL CTA SECTION ============ */}
            <section className="py-16 md:py-24 bg-slate-900">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <h2 
                        className="text-3xl sm:text-4xl font-bold text-white mb-4"
                        style={{ fontFamily: 'Outfit, sans-serif' }}
                    >
                        Ready to stop worrying about compliance?
                    </h2>
                    <p className="text-lg text-slate-400 mb-8 max-w-2xl mx-auto">
                        Join hundreds of UK hosts who've ditched the spreadsheets. 
                        Start your free trial today—no credit card required.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
                        <Button 
                            size="lg"
                            className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-base font-semibold"
                            onClick={() => navigate('/signup')}
                            data-testid="final-cta-trial"
                        >
                            Start Your Free Trial
                            <ArrowRight className="w-5 h-5 ml-2" />
                        </Button>
                        <Button 
                            size="lg"
                            variant="outline"
                            className="w-full sm:w-auto px-8 py-6 text-base font-medium border-slate-600 text-white hover:bg-slate-800"
                            onClick={handleStartDemo}
                            disabled={demoLoading}
                        >
                            {demoLoading ? 'Loading...' : 'Try Demo Mode'}
                        </Button>
                    </div>

                    <p className="text-sm text-slate-500">
                        14-day free trial • No credit card • Cancel anytime
                    </p>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-slate-950 py-12 border-t border-slate-800">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                                <Shield className="w-5 h-5 text-white" />
                            </div>
                            <span className="text-xl font-semibold text-white" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                Staylet
                            </span>
                        </div>
                        
                        <div className="flex items-center gap-6 text-sm text-slate-400">
                            <a href="#" className="hover:text-white transition-colors">Privacy</a>
                            <a href="#" className="hover:text-white transition-colors">Terms</a>
                            <a href="#" className="hover:text-white transition-colors">Contact</a>
                        </div>
                        
                        <p className="text-sm text-slate-500">
                            © 2026 Staylet. Built for UK hosts.
                        </p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
