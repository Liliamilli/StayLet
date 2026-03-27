import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
    Sparkles, 
    Send, 
    AlertTriangle, 
    Clock, 
    FileX,
    ChevronRight,
    Building2,
    Loader2,
    MessageSquare,
    X,
    CheckCircle2,
    AlertCircle,
    ListTodo
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SUGGESTED_QUESTIONS = [
    "What expires this month?",
    "Which properties have overdue items?",
    "What tasks need attention?",
    "What records are missing?",
    "Which property needs the most attention?"
];

export default function DashboardAssistant({ onNavigate }) {
    const [insights, setInsights] = useState(null);
    const [loading, setLoading] = useState(true);
    const [question, setQuestion] = useState('');
    const [askingQuestion, setAskingQuestion] = useState(false);
    const [chatResponse, setChatResponse] = useState(null);
    const [showChat, setShowChat] = useState(false);

    useEffect(() => {
        fetchInsights();
    }, []);

    const fetchInsights = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/assistant/insights`);
            setInsights(response.data);
        } catch (error) {
            console.error('Failed to fetch insights:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAskQuestion = async (q = question) => {
        if (!q.trim()) return;
        
        setAskingQuestion(true);
        setChatResponse(null);
        setShowChat(true);
        
        try {
            const response = await axios.post(`${API_URL}/api/assistant/ask`, { question: q });
            setChatResponse(response.data);
        } catch (error) {
            setChatResponse({ 
                answer: "Sorry, I couldn't process your question. Please try again.", 
                source: "error" 
            });
        } finally {
            setAskingQuestion(false);
            setQuestion('');
        }
    };

    const handleSuggestedQuestion = (q) => {
        setQuestion(q);
        handleAskQuestion(q);
    };

    if (loading) {
        return (
            <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-6 text-white">
                <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
                </div>
            </div>
        );
    }

    const hasData = insights && insights.summary && insights.summary.total_properties > 0;

    return (
        <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl overflow-hidden" data-testid="dashboard-assistant">
            {/* Header */}
            <div className="px-5 py-4 border-b border-slate-700/50">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
                            <Sparkles className="w-4 h-4 text-blue-400" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-white text-sm" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                Compliance Assistant
                            </h3>
                            <p className="text-xs text-slate-400">Ask anything about your properties</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Content */}
            <div className="p-5 space-y-4">
                {/* Chat Response */}
                {showChat && (
                    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
                        <div className="flex items-start justify-between gap-2 mb-2">
                            <div className="flex items-center gap-2">
                                <MessageSquare className="w-4 h-4 text-blue-400" />
                                <span className="text-xs text-slate-400">Assistant</span>
                            </div>
                            <button 
                                onClick={() => setShowChat(false)}
                                className="text-slate-500 hover:text-slate-300"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                        {askingQuestion ? (
                            <div className="flex items-center gap-2 text-slate-400 text-sm">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Analyzing your data...
                            </div>
                        ) : chatResponse ? (
                            <div className="text-sm text-slate-200 whitespace-pre-wrap">
                                {chatResponse.answer}
                            </div>
                        ) : null}
                    </div>
                )}

                {/* Priority Summary Cards */}
                {hasData && !showChat && (
                    <div className="space-y-3">
                        {/* Highest Risk Property */}
                        {insights.highest_risk_property && insights.highest_risk_property.risk_score > 0 && (
                            <div 
                                className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 cursor-pointer hover:bg-red-500/15 transition-colors"
                                onClick={() => onNavigate?.(`/app/properties/${insights.highest_risk_property.property_id}`)}
                                data-testid="highest-risk-card"
                            >
                                <div className="flex items-start gap-3">
                                    <div className="w-8 h-8 bg-red-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                                        <AlertTriangle className="w-4 h-4 text-red-400" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2">
                                            <span className="text-xs font-medium text-red-400 uppercase tracking-wide">Highest Risk</span>
                                        </div>
                                        <p className="text-sm font-medium text-white truncate">
                                            {insights.highest_risk_property.property_name}
                                        </p>
                                        <p className="text-xs text-slate-400 mt-0.5">
                                            {insights.highest_risk_property.risk_reasons.join(' • ')}
                                        </p>
                                    </div>
                                    <ChevronRight className="w-4 h-4 text-slate-500" />
                                </div>
                            </div>
                        )}

                        {/* Urgent Actions */}
                        {insights.urgent_actions && insights.urgent_actions.length > 0 && (
                            <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3" data-testid="urgent-actions-card">
                                <div className="flex items-center gap-2 mb-2">
                                    <Clock className="w-4 h-4 text-amber-400" />
                                    <span className="text-xs font-medium text-amber-400 uppercase tracking-wide">
                                        Next Urgent Actions
                                    </span>
                                </div>
                                <div className="space-y-2">
                                    {insights.urgent_actions.slice(0, 3).map((action, idx) => (
                                        <div 
                                            key={idx} 
                                            className="flex items-start gap-2 text-sm cursor-pointer hover:bg-amber-500/10 rounded p-1 -mx-1"
                                            onClick={() => action.property_id && onNavigate?.(`/app/properties/${action.property_id}`)}
                                        >
                                            <span className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${
                                                action.priority === 'critical' ? 'bg-red-400' : 'bg-amber-400'
                                            }`} />
                                            <div className="flex-1 min-w-0">
                                                <p className="text-slate-200 truncate">{action.action}</p>
                                                <p className="text-xs text-slate-400">{action.property_name}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Missing Compliance */}
                        {insights.missing_by_property && insights.missing_by_property.length > 0 && (
                            <div className="bg-slate-700/30 border border-slate-600/30 rounded-lg p-3" data-testid="missing-compliance-card">
                                <div className="flex items-center gap-2 mb-2">
                                    <FileX className="w-4 h-4 text-slate-400" />
                                    <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                                        Missing Records
                                    </span>
                                </div>
                                <div className="space-y-2">
                                    {insights.missing_by_property.slice(0, 3).map((prop, idx) => (
                                        <div 
                                            key={idx} 
                                            className="flex items-start gap-2 text-sm cursor-pointer hover:bg-slate-600/30 rounded p-1 -mx-1"
                                            onClick={() => onNavigate?.(`/app/properties/${prop.property_id}`)}
                                        >
                                            <Building2 className="w-3.5 h-3.5 text-slate-500 mt-0.5 flex-shrink-0" />
                                            <div className="flex-1 min-w-0">
                                                <p className="text-slate-200 truncate">{prop.property_name}</p>
                                                <p className="text-xs text-slate-400 truncate">{prop.missing.join(', ')}</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* All Clear State */}
                        {!insights.highest_risk_property?.risk_score && 
                         !insights.urgent_actions?.length && 
                         !insights.missing_by_property?.length && (
                            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-4 text-center">
                                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                                <p className="text-sm font-medium text-emerald-300">All clear!</p>
                                <p className="text-xs text-slate-400 mt-1">No urgent compliance issues</p>
                            </div>
                        )}
                    </div>
                )}

                {/* No Data State */}
                {!hasData && !showChat && (
                    <div className="text-center py-4">
                        <Building2 className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                        <p className="text-sm text-slate-400">Add properties to get AI insights</p>
                    </div>
                )}

                {/* Suggested Questions */}
                {hasData && (
                    <div className="space-y-2">
                        <p className="text-xs text-slate-500 uppercase tracking-wide">Quick questions</p>
                        <div className="flex flex-wrap gap-1.5">
                            {SUGGESTED_QUESTIONS.slice(0, 3).map((q, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => handleSuggestedQuestion(q)}
                                    disabled={askingQuestion}
                                    className="text-xs px-2.5 py-1.5 bg-slate-700/50 hover:bg-slate-700 text-slate-300 rounded-full transition-colors disabled:opacity-50"
                                >
                                    {q}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Question Input */}
                <div className="flex gap-2">
                    <Input
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAskQuestion()}
                        placeholder="Ask about your compliance..."
                        className="flex-1 bg-slate-800/50 border-slate-600/50 text-white placeholder:text-slate-500 text-sm"
                        disabled={askingQuestion}
                        data-testid="assistant-input"
                    />
                    <Button
                        onClick={() => handleAskQuestion()}
                        disabled={!question.trim() || askingQuestion}
                        size="sm"
                        className="bg-blue-600 hover:bg-blue-700 text-white px-3"
                        data-testid="assistant-send-btn"
                    >
                        {askingQuestion ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <Send className="w-4 h-4" />
                        )}
                    </Button>
                </div>
            </div>
        </div>
    );
}
