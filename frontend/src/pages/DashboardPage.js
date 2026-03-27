import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import DashboardCard from '../components/shared/DashboardCard';
import { 
    Building2, 
    Clock, 
    AlertCircle, 
    FileX, 
    ListTodo,
    Plus,
    ArrowRight,
    Calendar,
    ChevronRight,
    CheckCircle2,
    AlertTriangle,
    Sparkles,
    Crown
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
    const { subscription } = useAuth();
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                // Generate notifications and fetch dashboard data
                await axios.get(`${API_URL}/api/notifications/generate`);
                const response = await axios.get(`${API_URL}/api/dashboard/data`);
                setDashboardData(response.data);
            } catch (error) {
                console.error('Failed to fetch dashboard data:', error);
                // Fallback to basic stats if extended endpoint fails
                try {
                    const statsResponse = await axios.get(`${API_URL}/api/dashboard/stats`);
                    setDashboardData({ stats: statsResponse.data, upcoming_expiries: [], overdue_records: [], tasks_due_this_month: [] });
                } catch (e) {
                    console.error('Failed to fetch basic stats:', e);
                }
            } finally {
                setLoading(false);
            }
        };

        fetchDashboard();
    }, []);

    const formatDate = (dateStr) => {
        if (!dateStr) return '—';
        return new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
    };

    const getDaysText = (days) => {
        if (days === 0) return 'Today';
        if (days === 1) return 'Tomorrow';
        return `${days} days`;
    };

    if (loading) {
        return (
            <div className="animate-pulse space-y-6">
                <div className="h-8 bg-slate-200 rounded w-48" />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
                    {[...Array(5)].map((_, i) => (
                        <div key={i} className="h-32 bg-slate-200 rounded-lg" />
                    ))}
                </div>
            </div>
        );
    }

    const stats = dashboardData?.stats || {};
    const hasProperties = stats.total_properties > 0;
    const upcomingExpiries = dashboardData?.upcoming_expiries || [];
    const overdueRecords = dashboardData?.overdue_records || [];
    const tasksDueThisMonth = dashboardData?.tasks_due_this_month || [];

    const isTrialActive = subscription?.status === 'trial' && subscription?.trial_days_remaining > 0;
    const isTrialExpired = subscription?.status === 'expired';

    return (
        <div data-testid="dashboard-page">
            {/* Trial Banner */}
            {isTrialActive && (
                <div className="mb-6 p-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl text-white">
                    <div className="flex items-center justify-between flex-wrap gap-4">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-white/20 rounded-lg">
                                <Sparkles className="w-5 h-5" />
                            </div>
                            <div>
                                <p className="font-semibold">Free Trial - {subscription.trial_days_remaining} days remaining</p>
                                <p className="text-sm text-blue-100">
                                    You're on the {subscription.plan_name} plan • {subscription.property_count}/{subscription.property_limit} properties used
                                </p>
                            </div>
                        </div>
                        <Button 
                            onClick={() => navigate('/app/billing')}
                            className="bg-white text-blue-600 hover:bg-blue-50"
                            size="sm"
                        >
                            <Crown className="w-4 h-4 mr-2" />
                            Upgrade Now
                        </Button>
                    </div>
                </div>
            )}

            {/* Trial Expired Banner */}
            {isTrialExpired && (
                <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl">
                    <div className="flex items-center justify-between flex-wrap gap-4">
                        <div className="flex items-center gap-3">
                            <AlertTriangle className="w-5 h-5 text-amber-600" />
                            <div>
                                <p className="font-semibold text-amber-900">Your trial has expired</p>
                                <p className="text-sm text-amber-700">
                                    Subscribe to a plan to continue using Staylet.
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

            {/* Page header */}
            <div className="mb-8">
                <h1 
                    className="text-2xl font-bold text-slate-900 mb-1"
                    style={{ fontFamily: 'Outfit, sans-serif' }}
                >
                    Dashboard
                </h1>
                <p className="text-slate-500">
                    Overview of your property compliance status
                </p>
            </div>

            {/* Stats cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-8">
                <DashboardCard
                    title="Properties"
                    value={stats.total_properties || 0}
                    icon={Building2}
                    status="neutral"
                    onClick={() => navigate('/app/properties')}
                />
                <DashboardCard
                    title="Expiring Soon"
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
                <DashboardCard
                    title="Tasks Due"
                    value={stats.tasks_due || 0}
                    icon={ListTodo}
                    status="neutral"
                    onClick={() => navigate('/app/tasks')}
                />
            </div>

            {/* Main content area */}
            {!hasProperties ? (
                <div className="bg-white rounded-lg border border-slate-200 p-8">
                    <div className="flex flex-col items-center justify-center py-8 text-center">
                        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6">
                            <Building2 className="w-8 h-8 text-blue-600" />
                        </div>
                        <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                            Welcome to Staylet!
                        </h3>
                        <p className="text-sm text-slate-500 max-w-sm mb-6">
                            Get started by adding your first property. We'll help you track all compliance documents and deadlines.
                        </p>
                        <Button 
                            onClick={() => navigate('/app/properties')}
                            className="bg-blue-600 hover:bg-blue-700 text-white"
                            data-testid="add-first-property-btn"
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            Add Your First Property
                        </Button>
                    </div>
                </div>
            ) : (
                <div className="space-y-6">
                    {/* Overdue Alert Section - Most prominent if there are overdue items */}
                    {overdueRecords.length > 0 && (
                        <div className="bg-red-50 border border-red-200 rounded-lg overflow-hidden">
                            <div className="px-5 py-4 flex items-center justify-between border-b border-red-200 bg-red-100">
                                <div className="flex items-center gap-3">
                                    <AlertTriangle className="w-5 h-5 text-red-600" />
                                    <h2 className="font-semibold text-red-800" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                        {overdueRecords.length} Overdue Item{overdueRecords.length !== 1 ? 's' : ''} - Needs Immediate Attention
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
                                {overdueRecords.slice(0, 3).map((record) => (
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
                        {/* Upcoming Expiries */}
                        <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                            <div className="px-5 py-4 flex items-center justify-between border-b border-slate-100">
                                <h2 className="font-semibold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                    Next 5 Expiries
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
                                <div className="py-8 text-center">
                                    <Calendar className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                                    <p className="text-sm text-slate-500">No upcoming expiries</p>
                                </div>
                            ) : (
                                <div className="divide-y divide-slate-100">
                                    {upcomingExpiries.map((item) => {
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
                                                    <p className={`text-sm font-medium ${isUrgent ? 'text-amber-600' : 'text-slate-600'}`}>
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

                        {/* Tasks Due This Month */}
                        <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
                            <div className="px-5 py-4 flex items-center justify-between border-b border-slate-100">
                                <h2 className="font-semibold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                    Tasks Due This Month
                                </h2>
                                <Button 
                                    size="sm"
                                    variant="ghost"
                                    className="text-blue-600 hover:text-blue-700"
                                    onClick={() => navigate('/app/tasks')}
                                >
                                    View All <ChevronRight className="w-4 h-4 ml-1" />
                                </Button>
                            </div>
                            
                            {tasksDueThisMonth.length === 0 ? (
                                <div className="py-8 text-center">
                                    <CheckCircle2 className="w-10 h-10 text-emerald-300 mx-auto mb-3" />
                                    <p className="text-sm text-slate-500">No tasks due this month</p>
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        className="mt-3"
                                        onClick={() => navigate('/app/tasks')}
                                    >
                                        <Plus className="w-4 h-4 mr-1" />
                                        Create Task
                                    </Button>
                                </div>
                            ) : (
                                <div className="divide-y divide-slate-100">
                                    {tasksDueThisMonth.slice(0, 5).map((task) => (
                                        <div 
                                            key={task.id}
                                            className="px-5 py-3 flex items-center justify-between hover:bg-slate-50 cursor-pointer transition-colors"
                                            onClick={() => navigate('/app/tasks')}
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className={`p-2 rounded-lg ${task.is_overdue ? 'bg-red-100' : 'bg-blue-100'}`}>
                                                    <ListTodo className={`w-4 h-4 ${task.is_overdue ? 'text-red-600' : 'text-blue-600'}`} />
                                                </div>
                                                <div>
                                                    <p className={`font-medium ${task.is_overdue ? 'text-red-900' : 'text-slate-900'}`}>
                                                        {task.title}
                                                    </p>
                                                    <p className="text-sm text-slate-500">
                                                        {task.property_name || 'No property'} • {task.priority}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                {task.is_overdue ? (
                                                    <span className="text-xs font-medium px-2 py-1 bg-red-100 text-red-700 rounded-full">
                                                        Overdue
                                                    </span>
                                                ) : task.due_date ? (
                                                    <p className="text-sm text-slate-600">{formatDate(task.due_date)}</p>
                                                ) : (
                                                    <p className="text-sm text-slate-400">No date</p>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="bg-white rounded-lg border border-slate-200 p-6">
                        <h2 
                            className="text-lg font-semibold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Quick Actions
                        </h2>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                            <Button 
                                variant="outline" 
                                className="justify-between h-auto py-3"
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
                                className="justify-between h-auto py-3"
                                onClick={() => navigate('/app/properties')}
                                data-testid="quick-action-add-compliance"
                            >
                                <span className="flex items-center gap-2">
                                    <Plus className="w-4 h-4" />
                                    Add Compliance Record
                                </span>
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                            <Button 
                                variant="outline" 
                                className="justify-between h-auto py-3"
                                onClick={() => navigate('/app/tasks')}
                                data-testid="quick-action-add-task"
                            >
                                <span className="flex items-center gap-2">
                                    <Plus className="w-4 h-4" />
                                    Create Task
                                </span>
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
