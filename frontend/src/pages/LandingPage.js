import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import {
  Shield,
  CheckCircle2,
  AlertTriangle,
  Calendar,
  FileText,
  Building2,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  Menu,
  X,
  Bell,
  Upload,
  ClipboardList,
  Loader2,
  Lock,
  HelpCircle
} from 'lucide-react';

const painPoints = [
  {
    icon: AlertTriangle,
    title: 'Deadlines are easy to miss',
    description:
      'Gas safety, EICR, EPC, alarms, deposit records. One missed date can turn into stress fast.'
  },
  {
    icon: FileText,
    title: 'Documents end up scattered',
    description:
      'Emails, folders, downloads, screenshots. Finding the right certificate should not take 20 minutes.'
  },
  {
    icon: Calendar,
    title: 'Spreadsheets are not enough',
    description:
      'A spreadsheet can store dates, but it does not keep the whole compliance picture clear.'
  },
  {
    icon: ClipboardList,
    title: 'No clear view across properties',
    description:
      'You should be able to see what is due, overdue, missing, and complete in one place.'
  }
];

const howItWorks = [
  {
    step: '01',
    title: 'Add your property',
    description:
      'Create a property record and start tracking its compliance items in one place.',
    icon: Building2
  },
  {
    step: '02',
    title: 'Upload documents or add due dates',
    description:
      'Store certificates, set expiry dates, and keep notes linked to the right property.',
    icon: Upload
  },
  {
    step: '03',
    title: 'Stay ahead of deadlines',
    description:
      'See what is due soon, what is overdue, and what needs attention from your dashboard.',
    icon: Bell
  }
];

const trackedItems = [
  'Gas Safety Certificate',
  'EICR',
  'EPC',
  'Smoke / CO alarm checks',
  'Deposit protection',
  'Licensing',
  'Right to Rent evidence',
  'Custom compliance items'
];

const coreBenefits = [
  {
    icon: Bell,
    title: 'Never miss a renewal',
    description:
      'Keep due dates visible and stay on top of upcoming compliance deadlines.'
  },
  {
    icon: FileText,
    title: 'Keep documents in one place',
    description:
      'Store certificates and evidence against each property and compliance item.'
  },
  {
    icon: Shield,
    title: 'Be ready when you need proof',
    description:
      'Find the right document quickly without digging through folders and email.'
  },
  {
    icon: Building2,
    title: 'See your portfolio clearly',
    description:
      'Know which properties are compliant, due soon, overdue, or missing information.'
  }
];

const pricingPlans = [
  {
    name: 'Solo',
    monthlyPrice: 12,
    yearlyPrice: 120,
    description: 'For landlords with a small setup',
    features: [
      'Up to 3 properties',
      'Compliance tracking',
      'Document storage',
      'Reminder tracking',
      'Dashboard overview'
    ],
    cta: 'Start Free',
    popular: false
  },
  {
    name: 'Growth',
    monthlyPrice: 24,
    yearlyPrice: 240,
    description: 'For growing portfolios',
    features: [
      'Up to 10 properties',
      'Everything in Solo',
      'Faster setup tools',
      'Better portfolio visibility',
      'Priority support'
    ],
    cta: 'Start Free',
    popular: true
  },
  {
    name: 'Portfolio',
    monthlyPrice: 49,
    yearlyPrice: 490,
    description: 'For larger independent landlords',
    features: [
      'Up to 25 properties',
      'Everything in Growth',
      'More portfolio capacity',
      'Stronger oversight',
      'Priority support'
    ],
    cta: 'Start Free',
    popular: false
  }
];

const faqs = [
  {
    question: 'Who is Staylet for?',
    answer:
      'Staylet is for independent landlords who want a simpler way to track compliance records, deadlines, and documents across one or more properties.'
  },
  {
    question: 'What does Staylet track?',
    answer:
      'You can track common landlord compliance items such as gas safety, EICR, EPC, alarms, deposit records, licensing, and custom items you want to manage yourself.'
  },
  {
    question: 'Can I upload my existing documents?',
    answer:
      'Yes. You can attach documents to the relevant property and compliance item so everything stays organised in one place.'
  },
  {
    question: 'Do I need a credit card to get started?',
    answer:
      'No. You can start with a free trial and explore the product before deciding on a paid plan.'
  },
  {
    question: 'Can I cancel anytime?',
    answer:
      'Yes. You can cancel your subscription from billing settings at any time.'
  },
  {
    question: 'Is this legal advice?',
    answer:
      'No. Staylet is a tracking and organisation tool. It helps you manage deadlines and records, but it does not replace legal or professional advice.'
  }
];

const trustSignals = [
  { label: 'Built for landlords', icon: Building2 },
  { label: 'Simple document tracking', icon: FileText },
  { label: 'Reminder-led workflow', icon: Bell },
  { label: 'Secure account access', icon: Lock }
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
      <nav className="fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-md border-b border-slate-100 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2" data-testid="logo">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <span
                className="text-xl font-semibold text-slate-900"
                style={{ fontFamily: 'Outfit, sans-serif' }}
              >
                Staylet
              </span>
            </Link>

            <div className="hidden md:flex items-center gap-8">
              <a
                href="#how-it-works"
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
              >
                How it Works
              </a>
              <a
                href="#what-it-tracks"
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
              >
                What it Tracks
              </a>
              <a
                href="#pricing"
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
              >
                Pricing
              </a>
              <a
                href="#faq"
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors"
              >
                FAQ
              </a>
            </div>

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
                Start Free
              </Button>
            </div>

            <button
              className="md:hidden p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              data-testid="mobile-nav-btn"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-slate-100 py-4 px-4">
            <div className="flex flex-col gap-4">
              <a
                href="#how-it-works"
                className="text-sm font-medium text-slate-600"
                onClick={() => setMobileMenuOpen(false)}
              >
                How it Works
              </a>
              <a
                href="#what-it-tracks"
                className="text-sm font-medium text-slate-600"
                onClick={() => setMobileMenuOpen(false)}
              >
                What it Tracks
              </a>
              <a
                href="#pricing"
                className="text-sm font-medium text-slate-600"
                onClick={() => setMobileMenuOpen(false)}
              >
                Pricing
              </a>
              <a
                href="#faq"
                className="text-sm font-medium text-slate-600"
                onClick={() => setMobileMenuOpen(false)}
              >
                FAQ
              </a>
              <hr className="border-slate-200" />
              <Button variant="outline" className="w-full" onClick={() => navigate('/login')}>
                Sign in
              </Button>
              <Button
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                onClick={() => navigate('/signup')}
              >
                Start Free
              </Button>
            </div>
          </div>
        )}
      </nav>

      <section className="pt-28 pb-16 md:pt-36 md:pb-24 bg-gradient-to-b from-slate-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
              <Shield className="w-4 h-4" />
              <span>Built for independent landlords</span>
            </div>

            <h1
              className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 mb-6 tracking-tight leading-tight"
              style={{ fontFamily: 'Outfit, sans-serif' }}
              data-testid="hero-headline"
            >
              Never miss a landlord
              <br />
              <span className="text-blue-600">compliance deadline again.</span>
            </h1>

            <p
              className="text-lg md:text-xl text-slate-600 mb-8 max-w-2xl mx-auto leading-relaxed"
              data-testid="hero-subheadline"
            >
              Track certificates, expiry dates, reminders, and property compliance documents in
              one place.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-6">
              <Button
                size="lg"
                className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-base font-semibold shadow-lg shadow-blue-600/20"
                onClick={() => navigate('/signup')}
                data-testid="hero-cta-trial"
              >
                Start Free
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
                  <HelpCircle className="w-5 h-5 mr-2 text-blue-600" />
                )}
                {demoLoading ? 'Loading Demo...' : 'See Demo'}
              </Button>
            </div>

            <p className="text-sm text-slate-500 mb-12">
              14-day free trial • No credit card required
            </p>

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

      <section className="py-16 md:py-24 bg-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2
              className="text-3xl sm:text-4xl font-bold mb-4"
              style={{ fontFamily: 'Outfit, sans-serif' }}
            >
              Landlord compliance gets messy fast
            </h2>
            <p className="text-lg text-slate-400">
              Staylet helps you keep records, deadlines, and documents organised without the chaos.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {painPoints.map((point, index) => {
              const Icon = point.icon;
              return (
                <div key={index} className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Icon className="w-5 h-5 text-red-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white mb-1">{point.title}</h3>
                      <p className="text-slate-400 text-sm">{point.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

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
              Clear in three steps
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Add a property, track the right items, and stay ahead of what is due.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {howItWorks.map((step, index) => {
              const Icon = step.icon;
              return (
                <div key={index} className="relative">
                  {index < howItWorks.length - 1 && (
                    <div
                      className="hidden md:block absolute top-12 left-full w-full h-0.5 bg-slate-200 -translate-y-1/2 z-0"
                      style={{ width: 'calc(100% - 2rem)' }}
                    />
                  )}

                  <div className="relative z-10 text-center">
                    <div className="inline-flex items-center justify-center w-24 h-24 bg-blue-50 rounded-2xl mb-6">
                      <Icon className="w-10 h-10 text-blue-600" />
                    </div>
                    <div className="text-sm font-bold text-blue-600 mb-2">{step.step}</div>
                    <h3
                      className="text-xl font-semibold text-slate-900 mb-3"
                      style={{ fontFamily: 'Outfit, sans-serif' }}
                    >
                      {step.title}
                    </h3>
                    <p className="text-slate-600">{step.description}</p>
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
              Get Started
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </section>

      <section id="what-it-tracks" className="py-16 md:py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <span className="inline-block px-4 py-1.5 bg-emerald-100 text-emerald-700 rounded-full text-sm font-medium mb-4">
              What it Tracks
            </span>
            <h2
              className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4"
              style={{ fontFamily: 'Outfit, sans-serif' }}
            >
              Built around real landlord records
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Start with the core compliance items most landlords already need to manage.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto mb-16">
            {trackedItems.map((item, index) => (
              <div
                key={index}
                className="bg-white rounded-xl border border-slate-200 px-5 py-4 flex items-center gap-3"
              >
                <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                <span className="text-sm font-medium text-slate-700">{item}</span>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {coreBenefits.map((benefit, index) => {
              const Icon = benefit.icon;
              return (
                <div
                  key={index}
                  className="bg-white rounded-2xl p-8 border border-slate-200 hover:shadow-lg transition-all"
                >
                  <div className="flex items-start gap-5">
                    <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <Icon className="w-7 h-7 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <h3
                        className="text-xl font-semibold text-slate-900 mb-2"
                        style={{ fontFamily: 'Outfit, sans-serif' }}
                      >
                        {benefit.title}
                      </h3>
                      <p className="text-slate-600">{benefit.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

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
              Simple plans for independent landlords
            </h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-8">
              Start free. Upgrade when you need more properties.
            </p>

            <div
              className="flex items-center justify-center gap-3 bg-slate-100 rounded-full p-1.5 w-fit mx-auto"
              data-testid="landing-billing-toggle"
            >
              <button
                onClick={() => setIsAnnual(false)}
                className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
                  !isAnnual ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                }`}
                data-testid="landing-monthly-toggle"
              >
                Monthly
              </button>
              <button
                onClick={() => setIsAnnual(true)}
                className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
                  isAnnual ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'
                }`}
                data-testid="landing-annual-toggle"
              >
                Annual
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {pricingPlans.map((plan, index) => {
              const displayPrice = isAnnual ? Math.round(plan.yearlyPrice / 12) : plan.monthlyPrice;

              return (
                <div
                  key={index}
                  className={`relative bg-white rounded-2xl p-8 transition-all ${
                    plan.popular
                      ? 'border-2 border-blue-600 shadow-xl shadow-blue-600/10 scale-105 z-10'
                      : 'border border-slate-200 hover:border-slate-300 hover:shadow-lg'
                  }`}
                  data-testid={`pricing-${plan.name.toLowerCase()}`}
                >
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                      <span className="bg-blue-600 text-white text-xs font-semibold px-4 py-1.5 rounded-full">
                        Most Popular
                      </span>
                    </div>
                  )}

                  <h3
                    className="text-2xl font-bold text-slate-900 mb-1"
                    style={{ fontFamily: 'Outfit, sans-serif' }}
                  >
                    {plan.name}
                  </h3>
                  <p className="text-sm text-slate-500 mb-6">{plan.description}</p>

                  <div className="mb-2">
                    <span
                      className="text-4xl font-bold text-slate-900"
                      style={{ fontFamily: 'Outfit, sans-serif' }}
                    >
                      £{displayPrice}
                    </span>
                    <span className="text-slate-500">/month</span>
                  </div>
                  <p className="text-sm text-slate-400 mb-6">
                    {isAnnual ? `£${plan.yearlyPrice}/year` : 'Billed monthly'}
                  </p>

                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, fIndex) => (
                      <li key={fIndex} className="flex items-start gap-3 text-sm text-slate-600">
                        <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-emerald-500" />
                        {feature}
                      </li>
                    ))}
                  </ul>

                  <Button
                    className={`w-full h-12 font-semibold ${
                      plan.popular
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
            All plans include a free trial. Cancel anytime.
          </p>
        </div>
      </section>

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
              A simple product should have simple answers.
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
                {openFaq === index && <div className="px-6 pb-5 text-slate-600">{faq.answer}</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 md:py-24 bg-slate-900">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2
            className="text-3xl sm:text-4xl font-bold text-white mb-4"
            style={{ fontFamily: 'Outfit, sans-serif' }}
          >
            Keep landlord compliance simple
          </h2>
          <p className="text-lg text-slate-400 mb-8 max-w-2xl mx-auto">
            Track records, store documents, and stay on top of deadlines without the spreadsheet
            chaos.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
            <Button
              size="lg"
              className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white px-8 py-6 text-base font-semibold"
              onClick={() => navigate('/signup')}
              data-testid="final-cta-trial"
            >
              Start Free
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="w-full sm:w-auto px-8 py-6 text-base font-medium border-slate-600 text-white hover:bg-slate-800"
              onClick={handleStartDemo}
              disabled={demoLoading}
            >
              {demoLoading ? 'Loading...' : 'See Demo'}
            </Button>
          </div>

          <p className="text-sm text-slate-500">Free trial • No credit card required</p>
        </div>
      </section>

      <footer className="bg-slate-950 py-12 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <span
                className="text-xl font-semibold text-white"
                style={{ fontFamily: 'Outfit, sans-serif' }}
              >
                Staylet
              </span>
            </div>

            <div className="flex items-center gap-6 text-sm text-slate-400">
              <a href="/privacy" className="hover:text-white transition-colors">
                Privacy
              </a>
              <a href="/terms" className="hover:text-white transition-colors">
                Terms
              </a>
              <a href="/contact" className="hover:text-white transition-colors">
                Contact
              </a>
            </div>

            <p className="text-sm text-slate-500">© 2026 Staylet</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
