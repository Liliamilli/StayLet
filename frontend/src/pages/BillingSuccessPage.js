import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { CheckCircle2, Loader2, XCircle, ArrowRight } from 'lucide-react';
import { Button } from '../components/ui/button';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function BillingSuccessPage() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const { refreshSubscription } = useAuth();
    
    const [status, setStatus] = useState('checking'); // checking, success, error
    const [message, setMessage] = useState('Verifying your payment...');
    const [planInfo, setPlanInfo] = useState(null);
    const [attempts, setAttempts] = useState(0);
    const maxAttempts = 10;
    const pollInterval = 2000;

    useEffect(() => {
        const sessionId = searchParams.get('session_id');
        if (sessionId) {
            checkPaymentStatus(sessionId);
        } else {
            setStatus('error');
            setMessage('No payment session found. Please try again.');
        }
    }, [searchParams]);

    const checkPaymentStatus = async (sessionId, attemptCount = 0) => {
        try {
            const response = await axios.get(`${API_URL}/api/payments/status/${sessionId}`);
            const data = response.data;

            if (data.payment_status === 'paid' && data.success) {
                setStatus('success');
                setMessage(data.message || 'Payment successful!');
                setPlanInfo({
                    plan: data.plan,
                    billing_cycle: data.billing_cycle
                });
                // Refresh subscription data in context
                await refreshSubscription();
            } else if (data.status === 'expired') {
                setStatus('error');
                setMessage('Payment session expired. Please try again.');
            } else if (attemptCount < maxAttempts) {
                // Keep polling
                setAttempts(attemptCount + 1);
                setTimeout(() => {
                    checkPaymentStatus(sessionId, attemptCount + 1);
                }, pollInterval);
            } else {
                setStatus('error');
                setMessage('Payment verification timed out. If you were charged, please contact support.');
            }
        } catch (error) {
            console.error('Payment status check error:', error);
            // If session not found (404), show error immediately
            if (error.response?.status === 404) {
                setStatus('error');
                setMessage('Payment session not found. Please try again or contact support.');
                return;
            }
            // For other errors, keep polling up to max attempts
            if (attemptCount < maxAttempts) {
                setAttempts(attemptCount + 1);
                setTimeout(() => {
                    checkPaymentStatus(sessionId, attemptCount + 1);
                }, pollInterval);
            } else {
                setStatus('error');
                setMessage('Unable to verify payment status. Please contact support if you were charged.');
            }
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6" data-testid="billing-success-page">
            <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
                {status === 'checking' && (
                    <>
                        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                        </div>
                        <h1 className="text-2xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                            Processing Payment
                        </h1>
                        <p className="text-slate-600 mb-6">{message}</p>
                        <div className="flex items-center justify-center gap-2 text-sm text-slate-500">
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span>Please wait...</span>
                        </div>
                    </>
                )}

                {status === 'success' && (
                    <>
                        <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <CheckCircle2 className="w-8 h-8 text-emerald-600" />
                        </div>
                        <h1 className="text-2xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                            Payment Successful!
                        </h1>
                        <p className="text-slate-600 mb-6">{message}</p>
                        
                        {planInfo && (
                            <div className="bg-slate-50 rounded-lg p-4 mb-6">
                                <p className="text-sm text-slate-500 mb-1">Your new plan</p>
                                <p className="text-lg font-semibold text-slate-900 capitalize">
                                    {planInfo.plan} ({planInfo.billing_cycle})
                                </p>
                            </div>
                        )}

                        <Button
                            onClick={() => navigate('/app')}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                            data-testid="go-to-dashboard-btn"
                        >
                            Go to Dashboard
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                    </>
                )}

                {status === 'error' && (
                    <>
                        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <XCircle className="w-8 h-8 text-red-600" />
                        </div>
                        <h1 className="text-2xl font-bold text-slate-900 mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                            Payment Issue
                        </h1>
                        <p className="text-slate-600 mb-6">{message}</p>
                        
                        <div className="space-y-3">
                            <Button
                                onClick={() => navigate('/app/billing')}
                                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                                data-testid="try-again-btn"
                            >
                                Try Again
                            </Button>
                            <Button
                                variant="outline"
                                onClick={() => navigate('/app')}
                                className="w-full"
                            >
                                Back to Dashboard
                            </Button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
