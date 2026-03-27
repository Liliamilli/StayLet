import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { 
    HelpCircle,
    ChevronDown,
    ChevronUp,
    Building2,
    FileText,
    Bell,
    CreditCard,
    Shield,
    Clock,
    Upload,
    Search,
    Mail,
    ArrowRight,
    CheckCircle2,
    AlertCircle,
    Zap
} from 'lucide-react';

const gettingStarted = [
    {
        title: 'Add your properties',
        description: 'Go to Properties and click "Add Property". Enter your property name, address, postcode, and select the UK nation. This helps us track region-specific compliance requirements.',
        icon: Building2
    },
    {
        title: 'Upload your certificates',
        description: 'On each property page, click "Upload Document" to add your existing compliance certificates. Our AI will automatically extract key dates and set up reminders.',
        icon: Upload
    },
    {
        title: 'Track compliance status',
        description: 'Your dashboard shows which properties are compliant, expiring soon, or overdue. Click any item to see details or take action.',
        icon: Shield
    },
    {
        title: 'Get automatic reminders',
        description: 'We\'ll send you reminders before certificates expire - at 90, 60, 30, and 7 days by default. Customize these intervals in Settings.',
        icon: Bell
    }
];

const faqCategories = [
    {
        category: 'Using Staylet',
        icon: HelpCircle,
        questions: [
            {
                q: 'What compliance documents can I track?',
                a: 'Staylet tracks all common UK short-let compliance documents: Gas Safety Certificates (CP12), EICR electrical certificates, EPC ratings, PAT testing, fire safety equipment, smoke and CO alarms, legionella risk assessments, landlord insurance, and local authority licenses.'
            },
            {
                q: 'How does smart document extraction work?',
                a: 'When you upload a PDF or image of a certificate, our AI reads the document and extracts key information like document type, issue date, expiry date, and property address. You can review and edit these suggestions before saving.'
            },
            {
                q: 'Can I add multiple properties?',
                a: 'Yes! The number of properties you can add depends on your plan. Solo allows 1 property, Portfolio allows up to 5, and Operator allows up to 15 properties.'
            },
            {
                q: 'How do I export a compliance report?',
                a: 'On any property detail page, click the "Export Report" button. This generates a PDF containing all property details, compliance records, their statuses, upcoming tasks, and uploaded documents.'
            }
        ]
    },
    {
        category: 'Reminders & Notifications',
        icon: Bell,
        questions: [
            {
                q: 'When will I receive reminders?',
                a: 'By default, we send reminders at 90, 60, 30, and 7 days before a certificate expires. You can customize these intervals in Settings > Notification Preferences.'
            },
            {
                q: 'How do I turn off email reminders?',
                a: 'Go to Settings > Notification Preferences and toggle off "Email reminders". You\'ll still see alerts in the app, but won\'t receive emails.'
            },
            {
                q: 'What is the weekly digest?',
                a: 'The weekly digest is a summary email sent every Monday showing your compliance status across all properties, upcoming expiries, and outstanding tasks. You can turn this on/off in Settings.'
            }
        ]
    },
    {
        category: 'Billing & Subscription',
        icon: CreditCard,
        questions: [
            {
                q: 'How does the free trial work?',
                a: 'Every new account gets a 14-day free trial with full access to all features. No credit card is required to start. At the end of your trial, you can choose to subscribe or your account will be limited.'
            },
            {
                q: 'What\'s included in each plan?',
                a: 'Solo (£19/mo) includes 1 property with all features. Portfolio (£39/mo) includes up to 5 properties plus smart document extraction and priority support. Operator (£79/mo) includes up to 15 properties plus API access and dedicated support.'
            },
            {
                q: 'Can I change my plan?',
                a: 'Yes, you can upgrade or downgrade at any time from the Billing page. When upgrading, you\'ll pay the prorated difference. When downgrading, the change takes effect at the end of your billing cycle.'
            },
            {
                q: 'How do I cancel my subscription?',
                a: 'You can cancel anytime from the Billing page. Your access continues until the end of your current billing period. We don\'t offer refunds for partial months, but there are no cancellation fees.'
            },
            {
                q: 'Is annual billing available?',
                a: 'Yes! Toggle to "Annual" on the pricing page or Billing page to see annual prices. Annual billing saves you approximately 17% compared to monthly billing.'
            }
        ]
    },
    {
        category: 'Security & Data',
        icon: Shield,
        questions: [
            {
                q: 'Is my data secure?',
                a: 'Yes. We use bank-level encryption (AES-256) for all stored data and TLS 1.3 for data in transit. Your documents are stored securely in UK data centres and we\'re fully GDPR compliant.'
            },
            {
                q: 'Can I export my data?',
                a: 'Yes, you can export individual property compliance reports as PDFs. For a full data export, contact support and we\'ll provide your data within 48 hours.'
            },
            {
                q: 'What happens to my data if I cancel?',
                a: 'When you cancel, your data remains accessible for 30 days so you can export anything you need. After 30 days, your data is permanently deleted from our systems.'
            }
        ]
    }
];

export default function HelpPage() {
    const [openFaq, setOpenFaq] = useState({ category: 0, question: null });

    return (
        <div className="min-h-screen bg-slate-50" data-testid="help-page">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-12 px-4">
                <div className="max-w-4xl mx-auto text-center">
                    <HelpCircle className="w-12 h-12 mx-auto mb-4 opacity-80" />
                    <h1 className="text-3xl font-bold mb-3" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        Help Center
                    </h1>
                    <p className="text-blue-100 max-w-xl mx-auto">
                        Everything you need to know about using Staylet to manage your property compliance.
                    </p>
                </div>
            </div>

            <div className="max-w-4xl mx-auto px-4 py-8">
                {/* Getting Started Section */}
                <section className="mb-12">
                    <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        <Zap className="w-5 h-5 text-blue-600" />
                        Getting Started
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {gettingStarted.map((step, index) => {
                            const Icon = step.icon;
                            return (
                                <div 
                                    key={index}
                                    className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow"
                                >
                                    <div className="flex items-start gap-4">
                                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                            <Icon className="w-5 h-5 text-blue-600" />
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-sm font-bold text-blue-600">{index + 1}</span>
                                                <h3 className="font-semibold text-slate-900">{step.title}</h3>
                                            </div>
                                            <p className="text-sm text-slate-600">{step.description}</p>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </section>

                {/* FAQ Section */}
                <section className="mb-12">
                    <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        <HelpCircle className="w-5 h-5 text-blue-600" />
                        Frequently Asked Questions
                    </h2>
                    
                    <div className="space-y-6">
                        {faqCategories.map((category, catIndex) => {
                            const CatIcon = category.icon;
                            return (
                                <div key={catIndex} className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                                    <div className="px-5 py-4 bg-slate-50 border-b border-slate-200 flex items-center gap-2">
                                        <CatIcon className="w-5 h-5 text-slate-600" />
                                        <h3 className="font-semibold text-slate-900">{category.category}</h3>
                                    </div>
                                    <div className="divide-y divide-slate-100">
                                        {category.questions.map((faq, qIndex) => {
                                            const isOpen = openFaq.category === catIndex && openFaq.question === qIndex;
                                            return (
                                                <div key={qIndex}>
                                                    <button
                                                        className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-slate-50 transition-colors"
                                                        onClick={() => setOpenFaq(
                                                            isOpen 
                                                                ? { category: catIndex, question: null }
                                                                : { category: catIndex, question: qIndex }
                                                        )}
                                                    >
                                                        <span className="font-medium text-slate-900 pr-4">{faq.q}</span>
                                                        {isOpen ? (
                                                            <ChevronUp className="w-5 h-5 text-slate-400 flex-shrink-0" />
                                                        ) : (
                                                            <ChevronDown className="w-5 h-5 text-slate-400 flex-shrink-0" />
                                                        )}
                                                    </button>
                                                    {isOpen && (
                                                        <div className="px-5 pb-4 text-slate-600">
                                                            {faq.a}
                                                        </div>
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </section>

                {/* Contact Section */}
                <section className="bg-white rounded-xl border border-slate-200 p-6">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                                <Mail className="w-6 h-6 text-blue-600" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                    Still need help?
                                </h3>
                                <p className="text-sm text-slate-600">
                                    Contact our support team and we'll get back to you within 24 hours.
                                </p>
                            </div>
                        </div>
                        <Link to="/app/settings">
                            <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                                Contact Support
                                <ArrowRight className="w-4 h-4 ml-2" />
                            </Button>
                        </Link>
                    </div>
                </section>
            </div>
        </div>
    );
}
