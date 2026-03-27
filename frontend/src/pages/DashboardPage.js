import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import DashboardCard from '../components/shared/DashboardCard';
import EmptyState from '../components/shared/EmptyState';
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

    const hasAnyData = stats && (
        stats.total_properties > 0 ||
        stats.upcoming_expiries > 0 ||
        stats.overdue_items > 0 ||
        stats.missing_documents > 0 ||
        stats.tasks_due > 0
    );

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
                    title="Upcoming Expiries"
                    value={stats?.upcoming_expiries || 0}
                    icon={Clock}
                    status={stats?.upcoming_expiries > 0 ? 'warning' : 'neutral'}
                    onClick={() => navigate('/app/compliance')}
                />
                <DashboardCard
                    title="Overdue Items"
                    value={stats?.overdue_items || 0}
                    icon={AlertCircle}
                    status={stats?.overdue_items > 0 ? 'error' : 'success'}
                    onClick={() => navigate('/app/compliance')}
                />
                <DashboardCard
                    title="Missing Documents"
                    value={stats?.missing_documents || 0}
                    icon={FileX}
                    status={stats?.missing_documents > 0 ? 'warning' : 'neutral'}
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
            {!hasAnyData ? (
                <div className="bg-white rounded-lg border border-slate-200 p-8">
                    <EmptyState
                        icon={Building2}
                        title="Welcome to Staylet!"
                        description="Get started by adding your first property. We'll help you track all compliance documents and deadlines."
                        actionLabel="Add Your First Property"
                        onAction={() => navigate('/app/properties')}
                        secondaryActionLabel="Learn More"
                        onSecondaryAction={() => {}}
                    />
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
                                onClick={() => navigate('/app/compliance')}
                                data-testid="quick-action-upload-doc"
                            >
                                <span className="flex items-center gap-2">
                                    <Plus className="w-4 h-4" />
                                    Upload Document
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

                    {/* Recent Activity Placeholder */}
                    <div className="bg-white rounded-lg border border-slate-200 p-6">
                        <h2 
                            className="text-lg font-semibold text-slate-900 mb-4"
                            style={{ fontFamily: 'Outfit, sans-serif' }}
                        >
                            Recent Activity
                        </h2>
                        <div className="text-center py-8">
                            <p className="text-sm text-slate-500">
                                Your recent activity will appear here
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
