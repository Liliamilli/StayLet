import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import EmptyState from '../components/shared/EmptyState';
import TaskModal from '../components/tasks/TaskModal';
import { 
    ListTodo, 
    Plus, 
    Filter,
    Calendar,
    Building2,
    CheckCircle2,
    Clock,
    AlertTriangle,
    MoreVertical,
    Pencil,
    Trash2,
    RefreshCw,
    Zap
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const priorityConfig = {
    low: { bg: 'bg-slate-100', text: 'text-slate-600', label: 'Low' },
    medium: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Medium' },
    high: { bg: 'bg-amber-100', text: 'text-amber-700', label: 'High' },
    urgent: { bg: 'bg-red-100', text: 'text-red-700', label: 'Urgent' }
};

const statusConfig = {
    pending: { bg: 'bg-slate-100', text: 'text-slate-600', label: 'Pending', icon: Clock },
    in_progress: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'In Progress', icon: RefreshCw },
    completed: { bg: 'bg-emerald-100', text: 'text-emerald-700', label: 'Completed', icon: CheckCircle2 }
};

const categoryLabels = {
    general: 'General',
    maintenance: 'Maintenance',
    inspection: 'Inspection',
    renewal: 'Renewal',
    safety: 'Safety',
    seasonal: 'Seasonal',
    admin: 'Admin'
};

function TaskCard({ task, properties, onEdit, onDelete, onStatusChange }) {
    const [menuOpen, setMenuOpen] = useState(false);
    const priority = priorityConfig[task.priority] || priorityConfig.medium;
    const status = statusConfig[task.task_status] || statusConfig.pending;
    const StatusIcon = status.icon;
    const property = properties.find(p => p.id === task.property_id);
    
    const formatDate = (dateStr) => {
        if (!dateStr) return null;
        return new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    };

    const isOverdue = () => {
        if (!task.due_date || task.task_status === 'completed') return false;
        return new Date(task.due_date) < new Date();
    };

    const getDaysUntilDue = () => {
        if (!task.due_date) return null;
        const days = Math.ceil((new Date(task.due_date) - new Date()) / (1000 * 60 * 60 * 24));
        return days;
    };

    const daysUntil = getDaysUntilDue();

    return (
        <div 
            className={`bg-white border rounded-lg p-4 hover:shadow-md transition-all ${
                isOverdue() ? 'border-red-200 bg-red-50/30' : 'border-slate-200'
            }`}
            data-testid={`task-card-${task.id}`}
        >
            <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                    {/* Header row */}
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${priority.bg} ${priority.text}`}>
                            {priority.label}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${status.bg} ${status.text} flex items-center gap-1`}>
                            <StatusIcon className="w-3 h-3" />
                            {status.label}
                        </span>
                        {task.is_recurring && (
                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-700 flex items-center gap-1">
                                <RefreshCw className="w-3 h-3" />
                                Recurring
                            </span>
                        )}
                    </div>

                    {/* Title */}
                    <h3 className={`font-semibold mb-1 ${task.task_status === 'completed' ? 'text-slate-400 line-through' : 'text-slate-900'}`}>
                        {task.title}
                    </h3>

                    {/* Description */}
                    {task.description && (
                        <p className="text-sm text-slate-500 mb-2 line-clamp-2">{task.description}</p>
                    )}

                    {/* Meta row */}
                    <div className="flex items-center gap-4 text-sm text-slate-500 flex-wrap">
                        {property && (
                            <span className="flex items-center gap-1">
                                <Building2 className="w-3.5 h-3.5" />
                                {property.name}
                            </span>
                        )}
                        {task.due_date && (
                            <span className={`flex items-center gap-1 ${isOverdue() ? 'text-red-600 font-medium' : ''}`}>
                                <Calendar className="w-3.5 h-3.5" />
                                {formatDate(task.due_date)}
                                {isOverdue() && <AlertTriangle className="w-3.5 h-3.5" />}
                                {!isOverdue() && daysUntil !== null && daysUntil <= 7 && daysUntil >= 0 && (
                                    <span className="text-amber-600">({daysUntil === 0 ? 'Today' : daysUntil === 1 ? 'Tomorrow' : `${daysUntil}d`})</span>
                                )}
                            </span>
                        )}
                        <span className="text-slate-400">{categoryLabels[task.category] || task.category}</span>
                    </div>
                </div>

                {/* Actions */}
                <div className="relative" onClick={e => e.stopPropagation()}>
                    <button 
                        onClick={() => setMenuOpen(!menuOpen)}
                        className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
                        data-testid={`task-menu-${task.id}`}
                    >
                        <MoreVertical className="w-4 h-4 text-slate-400" />
                    </button>
                    {menuOpen && (
                        <div className="absolute right-0 mt-1 w-44 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-10">
                            {task.task_status !== 'completed' && (
                                <>
                                    {task.task_status === 'pending' && (
                                        <button 
                                            onClick={() => { onStatusChange(task.id, 'in_progress'); setMenuOpen(false); }}
                                            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                                        >
                                            <RefreshCw className="w-4 h-4" /> Start Task
                                        </button>
                                    )}
                                    <button 
                                        onClick={() => { onStatusChange(task.id, 'completed'); setMenuOpen(false); }}
                                        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-emerald-600 hover:bg-emerald-50"
                                    >
                                        <CheckCircle2 className="w-4 h-4" /> Mark Complete
                                    </button>
                                </>
                            )}
                            {task.task_status === 'completed' && (
                                <button 
                                    onClick={() => { onStatusChange(task.id, 'pending'); setMenuOpen(false); }}
                                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                                >
                                    <Clock className="w-4 h-4" /> Reopen Task
                                </button>
                            )}
                            <button 
                                onClick={() => { onEdit(task); setMenuOpen(false); }}
                                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                            >
                                <Pencil className="w-4 h-4" /> Edit
                            </button>
                            <button 
                                onClick={() => { onDelete(task.id); setMenuOpen(false); }}
                                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                            >
                                <Trash2 className="w-4 h-4" /> Delete
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default function TasksPage() {
    const navigate = useNavigate();
    const [tasks, setTasks] = useState([]);
    const [properties, setProperties] = useState([]);
    const [templates, setTemplates] = useState([]);
    const [loading, setLoading] = useState(true);
    const [modalOpen, setModalOpen] = useState(false);
    const [editingTask, setEditingTask] = useState(null);
    const [statusFilter, setStatusFilter] = useState('active'); // active, completed, all
    const [priorityFilter, setPriorityFilter] = useState('all');
    const [propertyFilter, setPropertyFilter] = useState('all');

    const fetchData = async () => {
        try {
            const [tasksRes, propsRes, templatesRes] = await Promise.all([
                axios.get(`${API_URL}/api/tasks`),
                axios.get(`${API_URL}/api/properties`),
                axios.get(`${API_URL}/api/tasks/templates`)
            ]);
            setTasks(tasksRes.data);
            setProperties(propsRes.data);
            setTemplates(templatesRes.data);
        } catch (error) {
            console.error('Failed to fetch tasks:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleCreateTask = () => {
        setEditingTask(null);
        setModalOpen(true);
    };

    const handleEditTask = (task) => {
        setEditingTask(task);
        setModalOpen(true);
    };

    const handleSaveTask = async (taskData) => {
        try {
            if (editingTask) {
                const response = await axios.put(`${API_URL}/api/tasks/${editingTask.id}`, taskData);
                setTasks(tasks.map(t => t.id === editingTask.id ? response.data : t));
            } else {
                const response = await axios.post(`${API_URL}/api/tasks`, taskData);
                setTasks([...tasks, response.data]);
            }
            setModalOpen(false);
            setEditingTask(null);
        } catch (error) {
            console.error('Failed to save task:', error);
            throw error;
        }
    };

    const handleDeleteTask = async (taskId) => {
        if (!window.confirm('Are you sure you want to delete this task?')) return;
        try {
            await axios.delete(`${API_URL}/api/tasks/${taskId}`);
            setTasks(tasks.filter(t => t.id !== taskId));
        } catch (error) {
            console.error('Failed to delete task:', error);
        }
    };

    const handleStatusChange = async (taskId, newStatus) => {
        try {
            const response = await axios.put(`${API_URL}/api/tasks/${taskId}`, { task_status: newStatus });
            setTasks(tasks.map(t => t.id === taskId ? response.data : t));
            // Refresh to get any new recurring tasks
            if (newStatus === 'completed') {
                setTimeout(fetchData, 500);
            }
        } catch (error) {
            console.error('Failed to update task status:', error);
        }
    };

    const handleCreateFromTemplate = (template) => {
        setEditingTask(null);
        setModalOpen(true);
        // Pre-fill will happen through modal's default state
    };

    // Filter tasks
    const filteredTasks = tasks.filter(task => {
        if (statusFilter === 'active' && task.task_status === 'completed') return false;
        if (statusFilter === 'completed' && task.task_status !== 'completed') return false;
        if (priorityFilter !== 'all' && task.priority !== priorityFilter) return false;
        if (propertyFilter !== 'all' && task.property_id !== propertyFilter) return false;
        return true;
    });

    // Sort tasks: overdue first, then by priority, then by due date
    const sortedTasks = [...filteredTasks].sort((a, b) => {
        // Completed tasks last
        if (a.task_status === 'completed' && b.task_status !== 'completed') return 1;
        if (a.task_status !== 'completed' && b.task_status === 'completed') return -1;
        
        // Overdue first
        const aOverdue = a.due_date && new Date(a.due_date) < new Date() && a.task_status !== 'completed';
        const bOverdue = b.due_date && new Date(b.due_date) < new Date() && b.task_status !== 'completed';
        if (aOverdue && !bOverdue) return -1;
        if (!aOverdue && bOverdue) return 1;
        
        // Then by priority
        const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 };
        const priorityDiff = (priorityOrder[a.priority] || 2) - (priorityOrder[b.priority] || 2);
        if (priorityDiff !== 0) return priorityDiff;
        
        // Then by due date
        if (a.due_date && b.due_date) {
            return new Date(a.due_date) - new Date(b.due_date);
        }
        if (a.due_date) return -1;
        if (b.due_date) return 1;
        return 0;
    });

    // Stats
    const overdueCount = tasks.filter(t => t.due_date && new Date(t.due_date) < new Date() && t.task_status !== 'completed').length;
    const dueSoonCount = tasks.filter(t => {
        if (!t.due_date || t.task_status === 'completed') return false;
        const days = Math.ceil((new Date(t.due_date) - new Date()) / (1000 * 60 * 60 * 24));
        return days >= 0 && days <= 7;
    }).length;
    const completedCount = tasks.filter(t => t.task_status === 'completed').length;

    if (loading) {
        return (
            <div className="animate-pulse space-y-6">
                <div className="h-8 bg-slate-200 rounded w-48" />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="h-32 bg-slate-200 rounded-lg" />
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div data-testid="tasks-page">
            {/* Page header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        Tasks
                    </h1>
                    <p className="text-slate-500">Manage your property tasks and to-dos</p>
                </div>
                <Button 
                    onClick={handleCreateTask}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                    data-testid="add-task-btn"
                >
                    <Plus className="w-4 h-4 mr-2" />
                    Create Task
                </Button>
            </div>

            {/* Stats summary */}
            {tasks.length > 0 && (
                <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className={`p-4 rounded-lg ${overdueCount > 0 ? 'bg-red-50 border border-red-100' : 'bg-slate-50'}`}>
                        <p className={`text-2xl font-bold ${overdueCount > 0 ? 'text-red-700' : 'text-slate-400'}`}>
                            {overdueCount}
                        </p>
                        <p className="text-sm text-slate-500">Overdue</p>
                    </div>
                    <div className={`p-4 rounded-lg ${dueSoonCount > 0 ? 'bg-amber-50 border border-amber-100' : 'bg-slate-50'}`}>
                        <p className={`text-2xl font-bold ${dueSoonCount > 0 ? 'text-amber-700' : 'text-slate-400'}`}>
                            {dueSoonCount}
                        </p>
                        <p className="text-sm text-slate-500">Due Soon</p>
                    </div>
                    <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-100">
                        <p className="text-2xl font-bold text-emerald-700">{completedCount}</p>
                        <p className="text-sm text-slate-500">Completed</p>
                    </div>
                </div>
            )}

            {tasks.length === 0 ? (
                <div className="bg-white rounded-lg border border-slate-200">
                    <EmptyState
                        icon={ListTodo}
                        title="No tasks yet"
                        description="Create tasks to track maintenance, inspections, and other property-related activities."
                        actionLabel="Create Task"
                        onAction={handleCreateTask}
                    />
                    
                    {/* Quick templates */}
                    <div className="border-t border-slate-200 p-6">
                        <h3 className="text-sm font-medium text-slate-900 mb-3 flex items-center gap-2">
                            <Zap className="w-4 h-4 text-blue-600" />
                            Quick Add from Templates
                        </h3>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {templates.slice(0, 4).map((template, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => handleCreateFromTemplate(template)}
                                    className="text-left p-3 border border-slate-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
                                >
                                    <p className="font-medium text-slate-900 text-sm">{template.title}</p>
                                    <p className="text-xs text-slate-500 mt-0.5">{template.description}</p>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            ) : (
                <>
                    {/* Filters */}
                    <div className="flex flex-wrap items-center gap-3 mb-6">
                        <div className="flex items-center gap-2">
                            <Filter className="w-4 h-4 text-slate-400" />
                            <span className="text-sm text-slate-500">Filter:</span>
                        </div>
                        <Select value={statusFilter} onValueChange={setStatusFilter}>
                            <SelectTrigger className="w-32" data-testid="status-filter">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="active">Active</SelectItem>
                                <SelectItem value="completed">Completed</SelectItem>
                                <SelectItem value="all">All</SelectItem>
                            </SelectContent>
                        </Select>
                        <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                            <SelectTrigger className="w-32" data-testid="priority-filter">
                                <SelectValue placeholder="Priority" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Priorities</SelectItem>
                                <SelectItem value="urgent">Urgent</SelectItem>
                                <SelectItem value="high">High</SelectItem>
                                <SelectItem value="medium">Medium</SelectItem>
                                <SelectItem value="low">Low</SelectItem>
                            </SelectContent>
                        </Select>
                        {properties.length > 0 && (
                            <Select value={propertyFilter} onValueChange={setPropertyFilter}>
                                <SelectTrigger className="w-40" data-testid="property-filter">
                                    <SelectValue placeholder="Property" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Properties</SelectItem>
                                    {properties.map(prop => (
                                        <SelectItem key={prop.id} value={prop.id}>{prop.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        )}
                        <span className="text-sm text-slate-400">
                            {sortedTasks.length} task{sortedTasks.length !== 1 ? 's' : ''}
                        </span>
                    </div>

                    {/* Task list */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        {sortedTasks.map((task) => (
                            <TaskCard
                                key={task.id}
                                task={task}
                                properties={properties}
                                onEdit={handleEditTask}
                                onDelete={handleDeleteTask}
                                onStatusChange={handleStatusChange}
                            />
                        ))}
                    </div>

                    {sortedTasks.length === 0 && (
                        <div className="bg-white rounded-lg border border-slate-200 py-12 text-center">
                            <p className="text-sm text-slate-500">No tasks match the current filters</p>
                        </div>
                    )}
                </>
            )}

            <TaskModal
                isOpen={modalOpen}
                onClose={() => { setModalOpen(false); setEditingTask(null); }}
                onSave={handleSaveTask}
                task={editingTask}
                properties={properties}
            />
        </div>
    );
}
