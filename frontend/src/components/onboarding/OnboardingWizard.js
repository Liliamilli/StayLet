import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../ui/button';
import { 
    Building2, 
    FileText, 
    LayoutDashboard, 
    Bell, 
    CheckCircle2,
    ArrowRight,
    X,
    Sparkles,
    ChevronRight
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const onboardingSteps = [
    {
        id: 1,
        key: 'add_property',
        title: 'Add your first property',
        description: 'Start by adding a property you want to track compliance for.',
        icon: Building2,
        action: 'Add Property',
        path: '/app/properties'
    },
    {
        id: 2,
        key: 'add_compliance',
        title: 'Add a compliance record',
        description: 'Upload or create your first certificate - like a Gas Safety or EICR.',
        icon: FileText,
        action: 'Add Record',
        path: '/app/properties'
    },
    {
        id: 3,
        key: 'view_dashboard',
        title: 'See your dashboard',
        description: 'View your compliance overview and upcoming deadlines at a glance.',
        icon: LayoutDashboard,
        action: 'View Dashboard',
        path: '/app'
    }
];

export default function OnboardingWizard({ onComplete, onDismiss }) {
    const navigate = useNavigate();
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [currentStep, setCurrentStep] = useState(1);

    useEffect(() => {
        fetchOnboardingStatus();
    }, []);

    const fetchOnboardingStatus = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/user/onboarding`);
            setStatus(response.data);
            setCurrentStep(response.data.current_step || 1);
            
            if (response.data.completed) {
                onComplete?.();
            }
        } catch (error) {
            console.error('Failed to fetch onboarding status:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleStepAction = (step) => {
        navigate(step.path);
        if (step.key === 'view_dashboard') {
            completeOnboarding();
        }
    };

    const completeOnboarding = async () => {
        try {
            await axios.post(`${API_URL}/api/user/onboarding/complete`);
            onComplete?.();
        } catch (error) {
            console.error('Failed to complete onboarding:', error);
        }
    };

    const handleSkip = () => {
        completeOnboarding();
        onDismiss?.();
    };

    if (loading) {
        return null;
    }

    if (status?.completed) {
        return null;
    }

    const completedSteps = status?.steps_completed || [];
    const progressPercent = (completedSteps.length / onboardingSteps.length) * 100;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" data-testid="onboarding-wizard">
            <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 text-white">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2">
                            <Sparkles className="w-5 h-5" />
                            <span className="font-medium">Getting Started</span>
                        </div>
                        <button 
                            onClick={handleSkip}
                            className="p-1 hover:bg-white/20 rounded transition-colors"
                            data-testid="skip-onboarding-btn"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                    <h2 className="text-2xl font-bold mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        Welcome to Staylet!
                    </h2>
                    <p className="text-blue-100">
                        Let's set up your compliance tracking in 3 simple steps.
                    </p>
                    
                    {/* Progress bar */}
                    <div className="mt-4">
                        <div className="flex items-center justify-between text-sm text-blue-100 mb-2">
                            <span>{completedSteps.length} of {onboardingSteps.length} complete</span>
                            <span>{Math.round(progressPercent)}%</span>
                        </div>
                        <div className="h-2 bg-white/20 rounded-full overflow-hidden">
                            <div 
                                className="h-full bg-white rounded-full transition-all duration-500"
                                style={{ width: `${progressPercent}%` }}
                            />
                        </div>
                    </div>
                </div>

                {/* Steps */}
                <div className="p-6 space-y-4">
                    {onboardingSteps.map((step, index) => {
                        const isCompleted = completedSteps.includes(step.key);
                        const isCurrent = step.id === currentStep;
                        const Icon = step.icon;
                        
                        return (
                            <div 
                                key={step.id}
                                className={`
                                    flex items-start gap-4 p-4 rounded-xl border-2 transition-all
                                    ${isCompleted 
                                        ? 'border-emerald-200 bg-emerald-50' 
                                        : isCurrent 
                                            ? 'border-blue-200 bg-blue-50' 
                                            : 'border-slate-100 bg-slate-50 opacity-60'
                                    }
                                `}
                                data-testid={`onboarding-step-${step.id}`}
                            >
                                <div className={`
                                    w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0
                                    ${isCompleted 
                                        ? 'bg-emerald-500 text-white' 
                                        : isCurrent 
                                            ? 'bg-blue-600 text-white' 
                                            : 'bg-slate-200 text-slate-400'
                                    }
                                `}>
                                    {isCompleted ? (
                                        <CheckCircle2 className="w-5 h-5" />
                                    ) : (
                                        <Icon className="w-5 h-5" />
                                    )}
                                </div>
                                
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center justify-between gap-2">
                                        <h3 className={`font-semibold ${isCompleted ? 'text-emerald-700' : 'text-slate-900'}`}>
                                            {step.title}
                                        </h3>
                                        {isCompleted && (
                                            <span className="text-xs font-medium text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded-full">
                                                Done
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm text-slate-500 mt-1">
                                        {step.description}
                                    </p>
                                    
                                    {isCurrent && !isCompleted && (
                                        <Button 
                                            onClick={() => handleStepAction(step)}
                                            className="mt-3 bg-blue-600 hover:bg-blue-700 text-white"
                                            size="sm"
                                            data-testid={`onboarding-action-${step.id}`}
                                        >
                                            {step.action}
                                            <ChevronRight className="w-4 h-4 ml-1" />
                                        </Button>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Footer */}
                <div className="px-6 pb-6 flex items-center justify-between">
                    <button 
                        onClick={handleSkip}
                        className="text-sm text-slate-500 hover:text-slate-700"
                    >
                        Skip for now
                    </button>
                    
                    {completedSteps.length === onboardingSteps.length && (
                        <Button 
                            onClick={completeOnboarding}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white"
                            data-testid="complete-onboarding-btn"
                        >
                            Get Started
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                    )}
                </div>
            </div>
        </div>
    );
}
