import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import DashboardCard from '../components/shared/DashboardCard';
import OnboardingWizard from '../components/onboarding/OnboardingWizard';
import EmptyState from '../components/shared/EmptyState';
import {
  Building2,
  Clock,
  AlertCircle,
  FileX,
  Plus,
  ArrowRight,
  Calendar,
  ChevronRight,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Crown,
  Rocket,
  Eye,
  FileText
} from 'lucide-react';
import { Button } from '../components/ui/button';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const statusConfig = {
  compliant: { bg: 'bg-emerald-50', text: 'text-emerald-700', icon: CheckCircle2 },
  expiring_soon: { bg: 'bg-amber-50', text: 'text-amber-700', icon: Clock },
  overdue: { bg: 'bg-red-50', text: 'text-red-700', icon: AlertCircle }
};

const categoryLabels = {
  gas_safety: 'Gas Safety',
  eicr: 'EICR',
  epc: 'EPC',
  insurance: 'Insurance',
  fire_risk_assessment: 'Fire Risk',
  pat_testing: 'PAT Testing',
  legionella: 'Legionella',
  smoke_co_alarms: 'Smoke/CO',
  licence: 'Licence',
  custom: 'Custom'
};

export default function DashboardPage() {
  const navigate = useNavigate();
  const { subscription, isDemo, onboardingStatus, completeOnboarding } = useAuth();

  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        await axios.get(`${API_URL}/api/notifications/generate`);
        const response = await axios.get(`${API_URL}/api/dashboard/data`);
        setDashboardData(response.data);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        try {
          const statsResponse = await axios.get(`${API_URL}/api/dashboard/stats`);
          setDashboardData({
            stats: statsResponse.data,
            upcoming_expiries: [],
            overdue_records: []
          });
        } catch (fallbackError) {
          console.error('Failed to fetch basic stats:', fallbackError);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  useEffect(() => {
    if (!loading && onboardingStatus && !onboardingStatus.completed && !isDemo) {
      setShowOnboarding(true);
    }
  }, [loading, onboardingStatus, isDemo]);

  const handleOnboardingComplete = () => {
    setShowOnboarding(false);
    completeOnboarding();
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short'
    });
  };

  const getDaysText = (days) => {
    if (days === 0) return 'Today';
    if (days === 1) return 'Tomorrow';
    if (days < 0) return 'Overdue';
    return `${days} days`;
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-slate-200 rounded w-48" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-slate-200 rounded-lg" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-80 bg-slate-200 rounded-lg" />
          <div className="h-80 bg-slate-200 rounded-lg" />
        </div>
      </div>
    );
  }

  const stats = dashboardData?.stats || {};
  const hasProperties = (stats.total_properties || 0) > 0;
  const upcomingExpiries = dashboardData?.upcoming_expiries || [];
  const overdueRecords = dashboardData?.overdue_records || [];

  const isTrialActive = subscription?.status === 'trial' && subscription?.trial_days_remaining > 0;
  const isTrialExpired = subscription?.status === 'expired';

  return (
    <div data-testid="dashboard-page">
      {showOnboarding && (
        <OnboardingWizard
          onComplete={handleOnboardingComplete}
          onDismiss={() => setShowOnboarding(false)}
        />
      )}

      {isDemo && (
        <div className="mb-6 p-4 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl text-white">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-lg">
                <Eye className="w-5 h-5" />
              </div>
              <div>
                <p className="font-semibold">You're exploring demo mode</p>
                <p className="text-sm text-purple-100">
                  This uses sample data. Create an account to manage your own properties.
                </p>
              </div>
            </div>
            <Button
              onClick={() => navigate('/signup')}
              className="bg-white text-purple-600 hover:bg-purple-50"
              size="sm"
            >
              <Rocket className="w-4 h-4 mr-2" />
              Start Free
            </Button>
          </div>
        </div>
      )}

      {isTrialActive && !isDemo && (
        <div className="mb-6 p-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl text-white">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-lg">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <p className="font-semibold">
                  Free trial — {subscription.trial_days_remaining} days remaining
                </p>
                <p className="text-sm text-blue-100">
                  {subscription.plan_name} plan • {subscription.property_count}/
                  {subscription.property_limit} properties used
                </p>
              </div>
            </div>
            <Button
              onClick={() => navigate('/app/billing')}
              className="bg-white text-blue-600 hover:bg-blue-50"
              size="sm"
            >
              <Crown className="w-4 h-4 mr-2" />
              View Plans
            </Button>
          </div>
        </div>
      )}

      {isTrialExpired && (
        <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600" />
              <div>
                <p className="font-semibold text-amber-900">Your trial has expired</p>
                <p className="text-sm text-amber-700">
                  Choose a plan to continue using Staylet.
                </p>
              </div>
            </div>
            <Button
              onClick={() => navigate('/app/billing')}
              className="bg-amber-600 hover:bg-amber-700 text-white"
              size="sm"
            >
              Choose Plan
            </Button>
          </div>
        </div>
      )}

      <div className="mb-8">
        <h1
          className="text-2xl font-bold text-slate-900 mb-1"
          style={{ fontFamily: 'Outfit, sans-serif' }}
        >
          Dashboard
        </h1>
        <p className="text-slate-500">
          See what is due, overdue, missing, and ready across your properties.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <DashboardCard
          title="Properties"
          value={stats.total_properties || 0}
          icon={Building2}
          status="neutral"
          onClick={() => navigate('/app/properties')}
        />
        <DashboardCard
          title="Due Soon"
          value={stats.upcoming_expiries || 0}
          icon={Clock}
          status={stats.upcoming_expiries > 0 ? 'warning' : 'success'}
          onClick={() => navigate('/app/compliance')}
        />
        <DashboardCard
          title="Overdue"
          value={stats.overdue_items || 0}
          icon={AlertCircle}
          status={stats.overdue_items > 0 ? 'error' : 'success'}
          onClick={() => navigate('/app/compliance')}
        />
        <DashboardCard
          title="Missing"
          value={stats.missing_records || 0}
          icon={FileX}
          status={stats.missing_records > 0 ? 'warning' : 'success'}
          onClick={() => navigate('/app/compliance')}
        />
      </div>

      {!hasProperties ? (
        <EmptyState
          icon={Building2}
          title="Add your first property"
          description="Start by creating a property record so you can track compliance items, store documents, and stay on top of deadlines."
          actionLabel="Add Property"
          onAction={() => navigate('/app/properties')}
          tip="Most users start by adding one property and then logging their first compliance item."
          variant="featured"
        />
      ) : (
        <div className="space-y-6">
          {overdueRecords.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-lg overflow-hidden">
              <div className="px-5 py-4 flex items-center justify-between border-b border-red-200 bg-red-100">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                  <h2
                    className="font-semibold text-red-800"
                    style={{ fontFamily: 'Outfit, sans-serif' }}
                  >
                    Overdue items needing attention
                  </h2>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  className="border-red-300 text-red-700 hover:bg-red-100"
                  onClick={() => navigate('/app/compliance')}
                >
                  View All
                </Button>
              </div>

              <div className="divide-y divide-red-100">
                {overdueRecords.slice(0, 5).map((record) => (
                  <div
                    key={record.id}
                    className="px-5 py-3 flex items-center justify-between hover:bg-red-100/50 cursor-pointer transition-colors"
                    onClick={() => navigate(`/app/properties/${record.property_id}`)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-red-100 rounded-lg">
                        <AlertCircle className="w-4 h-4 text-red-600" />
                      </div>
                      <div>
                        <p className="font-medium text-red-900">{record.title}</p>
                        <p className="text-sm text-red-600">
                          {record.property_name} • Expired {formatDate(record.expiry_date)}
                        </p>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-red-400" />
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
              <div className="px-5 py-4 flex items-center justify-between border-b border-slate-100">
                <h2
                  className="font-semibold text-slate-900"
                  style={{ fontFamily: 'Outfit, sans-serif' }}
                >
                  Due soon
                </h2>
                <Button
                  size="sm"
                  variant="ghost"
                  className="text-blue-600 hover:text-blue-700"
                  onClick={() => navigate('/app/compliance')}
                >
                  View All <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>

              {upcomingExpiries.length === 0 ? (
                <div className="py-10 text-center px-6">
                  <Calendar className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                  <p className="text-sm font-medium text-slate-700 mb-1">No upcoming expiries</p>
                  <p className="text-sm text-slate-500">
                    You do not have any compliance items coming up soon right now.
                  </p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {upcomingExpiries.slice(0, 6).map((item) => {
                    const config = statusConfig[item.compliance_status] || statusConfig.compliant;
                    const StatusIcon = config.icon;
                    const isUrgent = item.days_until_expiry <= 7;

                    return (
                      <div
                        key={item.id}
                        className="px-5 py-3 flex items-center justify-between hover:bg-slate-50 cursor-pointer transition-colors"
                        onClick={() => navigate(`/app/properties/${item.property_id}`)}
                      >
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-lg ${config.bg}`}>
                            <StatusIcon className={`w-4 h-4 ${config.text}`} />
                          </div>
                          <div>
                            <p className="font-medium text-slate-900">{item.title}</p>
                            <p className="text-sm text-slate-500">
                              {item.property_name} • {categoryLabels[item.category] || item.category}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p
                            className={`text-sm font-medium ${
                              isUrgent ? 'text-amber-600' : 'text-slate-600'
                            }`}
                          >
                            {getDaysText(item.days_until_expiry)}
                          </p>
                          <p className="text-xs text-slate-400">{formatDate(item.expiry_date)}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
              <div className="px-5 py-4 flex items-center justify-between border-b border-slate-100">
                <h2
                  className="font-semibold text-slate-900"
                  style={{ fontFamily: 'Outfit, sans-serif' }}
                >
                  Next recommended actions
                </h2>
              </div>

              <div className="p-5 space-y-3">
                <Button
                  variant="outline"
                  className="w-full justify-between h-auto py-3"
                  onClick={() => navigate('/app/properties')}
                  data-testid="quick-action-add-property"
                >
                  <span className="flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    Add Property
                  </span>
                  <ArrowRight className="w-4 h-4" />
                </Button>

                <Button
                  variant="outline"
                  className="w-full justify-between h-auto py-3"
                  onClick={() => navigate('/app/compliance')}
                  data-testid="quick-action-add-compliance"
                >
                  <span className="flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    Review Compliance Records
                  </span>
                  <ArrowRight className="w-4 h-4" />
                </Button>

                <Button
                  variant="outline"
                  className="w-full justify-between h-auto py-3"
                  onClick={() => navigate('/app/billing')}
                  data-testid="quick-action-billing"
                >
                  <span className="flex items-center gap-2">
                    <Crown className="w-4 h-4" />
                    View Plan and Billing
                  </span>
                  <ArrowRight className="w-4 h-4" />
                </Button>

                <div className="pt-3 border-t border-slate-100">
                  <p className="text-sm font-medium text-slate-900 mb-1">Keep this page simple</p>
                  <p className="text-sm text-slate-500">
                    The dashboard should help users see what needs attention fast, not make them
                    manage everything from one screen.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
