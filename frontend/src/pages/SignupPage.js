import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Shield, Loader2, Eye, EyeOff, CheckCircle2 } from 'lucide-react';

export default function SignupPage() {
    const navigate = useNavigate();
    const { signup } = useAuth();
    
    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (password.length < 8) {
            setError('Password must be at least 8 characters');
            return;
        }

        setLoading(true);

        try {
            await signup(email, password, fullName);
            navigate('/app');
        } catch (err) {
            console.error('Signup error:', err);
            setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const benefits = [
        'Track all compliance documents in one place',
        'Never miss a renewal deadline',
        '14-day free trial, no credit card required',
        'Cancel anytime'
    ];

    return (
        <div className="min-h-screen bg-slate-50 flex">
            {/* Left side - Form */}
            <div className="flex-1 flex items-center justify-center p-8">
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

                    {/* Header */}
                    <div className="mb-8">
                        <h1 
                            className="text-2xl font-bold text-slate-900 mb-2"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                            data-testid="signup-title"
                        >
                            Start your free trial
                        </h1>
                        <p className="text-slate-600">
                            Create your account to get started
                        </p>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-5">
                        {error && (
                            <div 
                                className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm"
                                data-testid="signup-error"
                            >
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <Label htmlFor="fullName">Full name</Label>
                            <Input
                                id="fullName"
                                type="text"
                                placeholder="John Smith"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                required
                                className="h-11"
                                data-testid="signup-name"
                            />
                        </div>

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
                                data-testid="signup-email"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <div className="relative">
                                <Input
                                    id="password"
                                    type={showPassword ? 'text' : 'password'}
                                    placeholder="Minimum 8 characters"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                    minLength={8}
                                    className="h-11 pr-10"
                                    data-testid="signup-password"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                                    data-testid="toggle-password"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                        </div>

                        <Button
                            type="submit"
                            className="w-full h-11 bg-blue-600 hover:bg-blue-700 text-white"
                            disabled={loading}
                            data-testid="signup-submit"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Creating account...
                                </>
                            ) : (
                                'Create account'
                            )}
                        </Button>

                        <p className="text-xs text-slate-500 text-center">
                            By creating an account, you agree to our{' '}
                            <a href="#" className="text-blue-600 hover:underline">Terms of Service</a>
                            {' '}and{' '}
                            <a href="#" className="text-blue-600 hover:underline">Privacy Policy</a>
                        </p>
                    </form>

                    {/* Sign in link */}
                    <p className="mt-8 text-center text-sm text-slate-600">
                        Already have an account?{' '}
                        <Link 
                            to="/login"
                            className="text-blue-600 hover:text-blue-700 font-medium transition-colors"
                            data-testid="login-link"
                        >
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>

            {/* Right side - Benefits */}
            <div className="hidden lg:flex lg:w-1/2 bg-blue-600 items-center justify-center p-12">
                <div className="max-w-md">
                    <h2 
                        className="text-3xl font-bold text-white mb-8"
                        style={{ fontFamily: 'Outfit, sans-serif' }}
                    >
                        Compliance peace of mind starts here
                    </h2>
                    
                    <ul className="space-y-4">
                        {benefits.map((benefit, index) => (
                            <li key={index} className="flex items-start gap-3 text-white/90">
                                <CheckCircle2 className="w-5 h-5 text-white flex-shrink-0 mt-0.5" />
                                {benefit}
                            </li>
                        ))}
                    </ul>

                    <div className="mt-12 p-6 bg-white/10 rounded-xl backdrop-blur-sm">
                        <p className="text-white/90 text-sm mb-4">
                            "I manage 8 properties and Staylet keeps everything organised. The reminders alone have saved me from costly lapses."
                        </p>
                        <p className="text-white/70 text-sm">
                            — James T., Manchester
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
