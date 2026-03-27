import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
    Sparkles, 
    AlertTriangle, 
    Clock, 
    FileX,
    CheckCircle2,
    Loader2,
    ChevronDown,
    ChevronUp,
    ArrowRight,
    ListTodo,
    Shield
} from 'lucide-react';
import { Button } from '../ui/button';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PropertyAssistant({ propertyId, onAddCompliance, onViewRecord }) {
    const [insights, setInsights] = useState(null);
    const [loading, setLoading] = useState(true);
    const [expanded, setExpanded] = useState(true);

    useEffect(() => {
        if (propertyId) {
            fetchInsights();
        }
    }, [propertyId]);

    const fetchInsights = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`${API_URL}/api/assistant/property/${propertyId}`);
            setInsights(response.data);
        } catch (error) {
            console.error('Failed to fetch property insights:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl border border-slate-200 p-4">
                <div className="flex items-center justify-center py-4">
                    <Loader2 className="w-5 h-5 animate-spin text-slate-400" />
                </div>
            </div>
        );
    }

    if (!insights) {
        return null;
    }

    const hasIssues = insights.overdue_records?.length > 0 || 
                      insights.missing_records?.length > 0 || 
                      insights.expiring_soon_records?.length > 0;

    const getScoreColor = (score) => {
        if (score >= 80) return 'text-emerald-600';
        if (score >= 60) return 'text-amber-600';
        return 'text-red-600';
    };

    const getScoreBg = (score) => {
        if (score >= 80) return 'bg-emerald-50 border-emerald-200';
        if (score >= 60) return 'bg-amber-50 border-amber-200';
        return 'bg-red-50 border-red-200';
    };

    return (
        <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl border border-slate-200 overflow-hidden" data-testid="property-assistant">
            {/* Header */}
            <button 
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-100/50 transition-colors"
                onClick={() => setExpanded(!expanded)}
            >
                <div className="flex items-center gap-2">
                    <div className="w-7 h-7 bg-blue-100 rounded-lg flex items-center justify-center">
                        <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                    </div>
                    <span className="font-medium text-slate-900 text-sm" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        AI Summary
                    </span>
                </div>
                <div className="flex items-center gap-3">
                    {/* Compliance Score */}
                    <div className={`px-2.5 py-1 rounded-full border ${getScoreBg(insights.compliance_score)}`}>
                        <span className={`text-xs font-semibold ${getScoreColor(insights.compliance_score)}`}>
                            {insights.compliance_score}% compliant
                        </span>
                    </div>
                    {expanded ? (
                        <ChevronUp className="w-4 h-4 text-slate-400" />
                    ) : (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                    )}
                </div>
            </button>

            {/* Content */}
            {expanded && (
                <div className="px-4 pb-4 space-y-3">
                    {/* Quick Stats */}
                    <div className="grid grid-cols-4 gap-2">
                        <div className="text-center p-2 bg-white rounded-lg border border-slate-200">
                            <p className="text-lg font-bold text-emerald-600">{insights.summary?.compliant || 0}</p>
                            <p className="text-xs text-slate-500">Compliant</p>
                        </div>
                        <div className="text-center p-2 bg-white rounded-lg border border-slate-200">
                            <p className="text-lg font-bold text-amber-600">{insights.summary?.expiring_soon || 0}</p>
                            <p className="text-xs text-slate-500">Expiring</p>
                        </div>
                        <div className="text-center p-2 bg-white rounded-lg border border-slate-200">
                            <p className="text-lg font-bold text-red-600">{insights.summary?.overdue || 0}</p>
                            <p className="text-xs text-slate-500">Overdue</p>
                        </div>
                        <div className="text-center p-2 bg-white rounded-lg border border-slate-200">
                            <p className="text-lg font-bold text-slate-600">{insights.summary?.missing || 0}</p>
                            <p className="text-xs text-slate-500">Missing</p>
                        </div>
                    </div>

                    {/* Recommended Actions */}
                    {insights.recommended_actions && insights.recommended_actions.length > 0 && (
                        <div className="space-y-2">
                            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                                Recommended Actions
                            </p>
                            <div className="space-y-1.5">
                                {insights.recommended_actions.map((action, idx) => (
                                    <div 
                                        key={idx}
                                        className={`flex items-start gap-2 p-2.5 rounded-lg cursor-pointer transition-colors ${
                                            action.priority === 'critical' 
                                                ? 'bg-red-50 hover:bg-red-100 border border-red-200' 
                                                : action.priority === 'high'
                                                    ? 'bg-amber-50 hover:bg-amber-100 border border-amber-200'
                                                    : 'bg-white hover:bg-slate-50 border border-slate-200'
                                        }`}
                                        onClick={() => {
                                            if (action.record_id && onViewRecord) {
                                                onViewRecord(action.record_id);
                                            } else if (action.category && onAddCompliance) {
                                                onAddCompliance(action.category);
                                            }
                                        }}
                                        data-testid={`action-${idx}`}
                                    >
                                        <div className={`w-5 h-5 rounded flex items-center justify-center flex-shrink-0 ${
                                            action.priority === 'critical' 
                                                ? 'bg-red-100' 
                                                : action.priority === 'high'
                                                    ? 'bg-amber-100'
                                                    : 'bg-slate-100'
                                        }`}>
                                            {action.priority === 'critical' ? (
                                                <AlertTriangle className="w-3 h-3 text-red-600" />
                                            ) : action.priority === 'high' ? (
                                                <FileX className="w-3 h-3 text-amber-600" />
                                            ) : (
                                                <Clock className="w-3 h-3 text-slate-600" />
                                            )}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className={`text-sm font-medium ${
                                                action.priority === 'critical' 
                                                    ? 'text-red-800' 
                                                    : action.priority === 'high'
                                                        ? 'text-amber-800'
                                                        : 'text-slate-800'
                                            }`}>
                                                {action.action}
                                            </p>
                                            <p className="text-xs text-slate-500 truncate">{action.detail}</p>
                                        </div>
                                        <ArrowRight className="w-4 h-4 text-slate-400 flex-shrink-0" />
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Pending Tasks */}
                    {insights.pending_tasks && insights.pending_tasks.length > 0 && (
                        <div className="space-y-2">
                            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                                Pending Tasks
                            </p>
                            <div className="bg-white rounded-lg border border-slate-200 divide-y divide-slate-100">
                                {insights.pending_tasks.slice(0, 3).map((task, idx) => (
                                    <div key={idx} className="flex items-center gap-2 p-2.5">
                                        <ListTodo className="w-4 h-4 text-slate-400 flex-shrink-0" />
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm text-slate-700 truncate">{task.title}</p>
                                        </div>
                                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                                            task.days_until < 0 
                                                ? 'bg-red-100 text-red-700'
                                                : task.days_until <= 7
                                                    ? 'bg-amber-100 text-amber-700'
                                                    : 'bg-slate-100 text-slate-600'
                                        }`}>
                                            {task.days_until < 0 
                                                ? `${Math.abs(task.days_until)}d overdue`
                                                : task.days_until === 0 
                                                    ? 'Today'
                                                    : `${task.days_until}d`
                                            }
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* All Clear State */}
                    {!hasIssues && insights.summary?.total_records > 0 && (
                        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-center">
                            <Shield className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
                            <p className="text-sm font-medium text-emerald-800">Property fully compliant</p>
                            <p className="text-xs text-emerald-600 mt-1">All required records are up to date</p>
                        </div>
                    )}

                    {/* No Records State */}
                    {insights.summary?.total_records === 0 && (
                        <div className="bg-slate-100 border border-slate-200 rounded-lg p-4 text-center">
                            <FileX className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                            <p className="text-sm font-medium text-slate-700">No compliance records yet</p>
                            <p className="text-xs text-slate-500 mt-1">Add your first certificate to get started</p>
                            <Button 
                                size="sm" 
                                className="mt-3 bg-blue-600 hover:bg-blue-700 text-white"
                                onClick={() => onAddCompliance?.()}
                            >
                                Add Compliance Record
                            </Button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
