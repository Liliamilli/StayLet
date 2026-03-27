import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Shield, Loader2, ArrowLeft, CheckCircle2 } from 'lucide-react';

export default function ResetPasswordPage() {
    const { resetPassword } = useAuth();
    
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await resetPassword(email);
            setSubmitted(true);
        } catch (err) {
            console.error('Reset password error:', err);
            setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-8">
            <div className="w-full max-w-md">
                {/* Logo */}
                <Link to="/" className="flex items-center gap-2 mb-10" data-testid="auth-logo">
                    <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                        <Shield className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-2xl font-semibold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        Staylet
                    </span>
                </Link>

                {submitted ? (
                    /* Success state */
                    <div className="text-center">
                        <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <CheckCircle2 className="w-8 h-8 text-emerald-600" />
                        </div>
                        <h1 
                            className="text-2xl font-bold text-slate-900 mb-2"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                            data-testid="reset-success-title"
                        >
                            Check your email
                        </h1>
                        <p className="text-slate-600 mb-8">
                            If an account exists for <strong>{email}</strong>, you'll receive password reset instructions shortly.
                        </p>
                        <Link to="/login">
                            <Button 
                                variant="outline" 
                                className="w-full"
                                data-testid="back-to-login"
                            >
                                <ArrowLeft className="w-4 h-4 mr-2" />
                                Back to sign in
                            </Button>
                        </Link>
                    </div>
                ) : (
                    /* Form state */
                    <>
                        {/* Header */}
                        <div className="mb-8">
                            <h1 
                                className="text-2xl font-bold text-slate-900 mb-2"
                                style={{ fontFamily: 'Outfit, sans-serif' }}
                                data-testid="reset-title"
                            >
                                Reset your password
                            </h1>
                            <p className="text-slate-600">
                                Enter your email address and we'll send you instructions to reset your password.
                            </p>
                        </div>

                        {/* Form */}
                        <form onSubmit={handleSubmit} className="space-y-5">
                            {error && (
                                <div 
                                    className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm"
                                    data-testid="reset-error"
                                >
                                    {error}
                                </div>
                            )}

                            <div className="space-y-2">
                                <Label htmlFor="email">Email address</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    placeholder="you@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    className="h-11"
                                    data-testid="reset-email"
                                />
                            </div>

                            <Button
                                type="submit"
                                className="w-full h-11 bg-blue-600 hover:bg-blue-700 text-white"
                                disabled={loading}
                                data-testid="reset-submit"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Sending instructions...
                                    </>
                                ) : (
                                    'Send reset instructions'
                                )}
                            </Button>
                        </form>

                        {/* Back to login */}
                        <p className="mt-8 text-center text-sm text-slate-600">
                            <Link 
                                to="/login"
                                className="text-blue-600 hover:text-blue-700 font-medium transition-colors inline-flex items-center gap-1"
                                data-testid="back-to-login-link"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Back to sign in
                            </Link>
                        </p>
                    </>
                )}
            </div>
        </div>
    );
}
