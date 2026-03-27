import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import DashboardCard from '../components/shared/DashboardCard';
import { 
    Building2, 
    Clock, 
    AlertCircle, 
    FileX, 
    ListTodo,
    Plus,
    ArrowRight
} from 'lucide-react';
import { Button } from '../components/ui/button';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function DashboardPage() {
    const navigate = useNavigate();
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await axios.get(`${API_URL}/api/dashboard/stats`);
                setStats(response.data);
            } catch (error) {
                console.error('Failed to fetch dashboard stats:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

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

    const hasProperties = stats?.total_properties > 0;

    return (
        <div data-testid="dashboard-page">
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-8">
                <DashboardCard
                    title="Total Properties"
                    value={stats?.total_properties || 0}
                    icon={Building2}
                    status="neutral"
                    onClick={() => navigate('/app/properties')}
                />
                <DashboardCard
                    title="Expiring Soon"
                    value={stats?.upcoming_expiries || 0}
                    icon={Clock}
                    status={stats?.upcoming_expiries > 0 ? 'warning' : 'success'}
                    onClick={() => navigate('/app/compliance')}
                />
                <DashboardCard
                    title="Overdue"
                    value={stats?.overdue_items || 0}
                    icon={AlertCircle}
                    status={stats?.overdue_items > 0 ? 'error' : 'success'}
                    onClick={() => navigate('/app/compliance')}
                />
                <DashboardCard
                    title="Missing Records"
                    value={stats?.missing_records || 0}
                    icon={FileX}
                    status={stats?.missing_records > 0 ? 'warning' : 'success'}
                    onClick={() => navigate('/app/compliance')}
                />
                <DashboardCard
                    title="Tasks Due"
                    value={stats?.tasks_due || 0}
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
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Quick Actions */}
                    <div className="bg-white rounded-lg border border-slate-200 p-6">
                        <h2 
                            className="text-lg font-semibold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Quick Actions
                        </h2>
                        <div className="space-y-3">
                            <Button 
                                variant="outline" 
                                className="w-full justify-between"
                                onClick={() => navigate('/app/properties')}
                                data-testid="quick-action-add-property"
                            >
                                <span className="flex items-center gap-2">
                                    <Plus className="w-4 h-4" />
                                    Add New Property
                                </span>
                                <ArrowRight className="w-4 h-4" />
                            </Button>
                            <Button 
                                variant="outline" 
                                className="w-full justify-between"
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
                                className="w-full justify-between"
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

                    {/* Alerts Summary */}
                    <div className="bg-white rounded-lg border border-slate-200 p-6">
                        <h2 
                            className="text-lg font-semibold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Compliance Alerts
                        </h2>
                        
                        {stats?.overdue_items > 0 || stats?.upcoming_expiries > 0 || stats?.missing_records > 0 ? (
                            <div className="space-y-3">
                                {stats?.overdue_items > 0 && (
                                    <div className="flex items-center justify-between p-3 bg-red-50 border border-red-100 rounded-lg">
                                        <div className="flex items-center gap-3">
                                            <AlertCircle className="w-5 h-5 text-red-600" />
                                            <div>
                                                <p className="font-medium text-red-800">{stats.overdue_items} Overdue</p>
                                                <p className="text-xs text-red-600">Requires immediate attention</p>
                                            </div>
                                        </div>
                                        <Button 
                                            size="sm" 
                                            variant="outline"
                                            className="border-red-200 text-red-700 hover:bg-red-100"
                                            onClick={() => navigate('/app/compliance')}
                                        >
                                            View
                                        </Button>
                                    </div>
                                )}
                                
                                {stats?.upcoming_expiries > 0 && (
                                    <div className="flex items-center justify-between p-3 bg-amber-50 border border-amber-100 rounded-lg">
                                        <div className="flex items-center gap-3">
                                            <Clock className="w-5 h-5 text-amber-600" />
                                            <div>
                                                <p className="font-medium text-amber-800">{stats.upcoming_expiries} Expiring Soon</p>
                                                <p className="text-xs text-amber-600">Within 30 days</p>
                                            </div>
                                        </div>
                                        <Button 
                                            size="sm" 
                                            variant="outline"
                                            className="border-amber-200 text-amber-700 hover:bg-amber-100"
                                            onClick={() => navigate('/app/compliance')}
                                        >
                                            View
                                        </Button>
                                    </div>
                                )}
                                
                                {stats?.missing_records > 0 && (
                                    <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg">
                                        <div className="flex items-center gap-3">
                                            <FileX className="w-5 h-5 text-slate-500" />
                                            <div>
                                                <p className="font-medium text-slate-800">{stats.missing_records} Missing</p>
                                                <p className="text-xs text-slate-500">Records not uploaded</p>
                                            </div>
                                        </div>
                                        <Button 
                                            size="sm" 
                                            variant="outline"
                                            onClick={() => navigate('/app/compliance')}
                                        >
                                            View
                                        </Button>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="flex items-center justify-center py-8 text-center">
                                <div>
                                    <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                        <svg className="w-6 h-6 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                        </svg>
                                    </div>
                                    <p className="text-sm font-medium text-emerald-700">All caught up!</p>
                                    <p className="text-xs text-slate-500 mt-1">No urgent compliance issues</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
