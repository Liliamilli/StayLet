import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Shield, Loader2, Eye, EyeOff, CheckCircle2, Building2, Bell, FileText } from 'lucide-react';

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

    if (!fullName.trim()) {
      setError('Please enter your name');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      await signup(email.trim(), password, fullName.trim());
      navigate('/app');
    } catch (err) {
      console.error('Signup error:', err);
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const benefits = [
    {
      icon: Building2,
      text: 'Add your first property in minutes'
    },
    {
      icon: FileText,
      text: 'Track documents and compliance records in one place'
    },
    {
      icon: Bell,
      text: 'Stay ahead of upcoming deadlines'
    },
    {
      icon: CheckCircle2,
      text: '14-day free trial with no credit card required'
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <div className="flex-1 flex items-center justify-center p-6 sm:p-8">
        <div className="w-full max-w-md">
          <Link to="/" className="flex items-center gap-2 mb-10" data-testid="auth-logo">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <span
              className="text-2xl font-semibold text-slate-900"
              style={{ fontFamily: 'Outfit, sans-serif' }}
            >
              Staylet
            </span>
          </Link>

          <div className="mb-8">
            <h1
              className="text-2xl font-bold text-slate-900 mb-2"
              style={{ fontFamily: 'Outfit, sans-serif' }}
              data-testid="signup-title"
            >
              Start your free trial
            </h1>
            <p className="text-slate-600">
              Create your account and start tracking landlord compliance in one place.
            </p>
          </div>

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
                autoComplete="name"
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
                autoComplete="email"
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
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  data-testid="toggle-password"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
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

            <p className="text-xs text-slate-500 text-center leading-relaxed">
              By creating an account, you agree to our{' '}
              <Link to="/terms" className="text-blue-600 hover:underline">
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link to="/privacy" className="text-blue-600 hover:underline">
                Privacy Policy
              </Link>
              .
            </p>
          </form>

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

      <div className="hidden lg:flex lg:w-1/2 bg-white border-l border-slate-200 items-center justify-center p-12">
        <div className="max-w-md">
          <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <Shield className="w-4 h-4" />
            <span>Simple setup</span>
          </div>

          <h2
            className="text-3xl font-bold text-slate-900 mb-6"
            style={{ fontFamily: 'Outfit, sans-serif' }}
          >
            Start with the essentials
          </h2>

          <p className="text-slate-600 mb-8">
            Staylet is built to help you keep properties, documents, and deadlines organised
            without making setup feel heavy.
          </p>

          <ul className="space-y-4">
            {benefits.map((benefit, index) => {
              const Icon = benefit.icon;
              return (
                <li key={index} className="flex items-start gap-3 text-slate-700">
                  <div className="w-9 h-9 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                    <Icon className="w-5 h-5 text-blue-600" />
                  </div>
                  <span className="pt-1">{benefit.text}</span>
                </li>
              );
            })}
          </ul>

          <div className="mt-10 p-5 rounded-xl bg-slate-50 border border-slate-200">
            <p className="text-sm font-medium text-slate-900 mb-1">What happens next?</p>
            <p className="text-sm text-slate-600">
              After signup, you will be guided into the app so you can add your first property and
              start tracking compliance right away.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
