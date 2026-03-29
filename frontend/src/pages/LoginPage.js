import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Shield, Loader2, Eye, EyeOff, CheckCircle2, FileText, Bell } from 'lucide-react';

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const from = location.state?.from?.pathname || '/app';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email.trim(), password);
      navigate(from, { replace: true });
    } catch (err) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const reminders = [
    'See what is overdue and due soon',
    'Open your property records quickly',
    'Get back to your compliance dashboard in seconds'
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
              data-testid="login-title"
            >
              Welcome back
            </h1>
            <p className="text-slate-600">
              Sign in to continue managing your landlord compliance records.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div
                className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm"
                data-testid="login-error"
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
                data-testid="login-email"
                autoComplete="email"
              />
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
              </div>

              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="h-11 pr-10"
                  data-testid="login-password"
                  autoComplete="current-password"
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
              data-testid="login-submit"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </Button>
          </form>

          <p className="mt-8 text-center text-sm text-slate-600">
            Don&apos;t have an account?{' '}
            <Link
              to="/signup"
              className="text-blue-600 hover:text-blue-700 font-medium transition-colors"
              data-testid="signup-link"
            >
              Start free
            </Link>
          </p>
        </div>
      </div>

      <div className="hidden lg:flex lg:w-1/2 bg-white border-l border-slate-200 items-center justify-center p-12">
        <div className="max-w-md">
          <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <Shield className="w-4 h-4" />
            <span>Simple login</span>
          </div>

          <h2
            className="text-3xl font-bold text-slate-900 mb-6"
            style={{ fontFamily: 'Outfit, sans-serif' }}
          >
            Pick up where you left off
          </h2>

          <p className="text-slate-600 mb-8">
            Staylet is built to help you get back to the important things quickly: your deadlines,
            documents, and property records.
          </p>

          <ul className="space-y-4">
            {reminders.map((item, index) => (
              <li key={index} className="flex items-start gap-3 text-slate-700">
                <div className="w-9 h-9 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                  {index === 0 && <Bell className="w-5 h-5 text-blue-600" />}
                  {index === 1 && <FileText className="w-5 h-5 text-blue-600" />}
                  {index === 2 && <CheckCircle2 className="w-5 h-5 text-blue-600" />}
                </div>
                <span className="pt-1">{item}</span>
              </li>
            ))}
          </ul>

          <div className="mt-10 p-5 rounded-xl bg-slate-50 border border-slate-200">
            <p className="text-sm font-medium text-slate-900 mb-1">Need help getting back in?</p>
            <p className="text-sm text-slate-600">
              Add a proper password reset flow later if it is not implemented yet. Until then, keep
              the login page clean and reliable.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
