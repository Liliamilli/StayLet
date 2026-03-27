import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { 
    ArrowLeft, 
    Building2, 
    MapPin, 
    Home,
    Pencil,
    Plus,
    AlertCircle,
    Clock,
    CheckCircle2,
    FileX,
    Calendar,
    Trash2,
    Zap,
    ListTodo,
    MoreVertical,
    RefreshCw,
    Upload,
    FileText,
    Sparkles
} from 'lucide-react';
import PropertyModal from '../components/properties/PropertyModal';
import ComplianceRecordModal from '../components/compliance/ComplianceRecordModal';
import BulkComplianceModal from '../components/compliance/BulkComplianceModal';
import TaskModal from '../components/tasks/TaskModal';
import UploadDocumentModal from '../components/documents/UploadDocumentModal';
import DocumentList from '../components/documents/DocumentList';
import EmptyState from '../components/shared/EmptyState';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const statusConfig = {
    compliant: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', icon: CheckCircle2, label: 'Compliant' },
    expiring_soon: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', icon: Clock, label: 'Expiring Soon' },
    overdue: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', icon: AlertCircle, label: 'Overdue' },
    missing: { bg: 'bg-slate-50', text: 'text-slate-600', border: 'border-slate-200', icon: FileX, label: 'Missing' }
};

const categoryLabels = {
    gas_safety: 'Gas Safety Certificate',
    eicr: 'EICR',
    epc: 'EPC',
    insurance: 'Insurance',
    fire_risk_assessment: 'Fire Risk Assessment',
    pat_testing: 'PAT Testing',
    legionella: 'Legionella Risk Assessment',
    smoke_co_alarms: 'Smoke/CO Alarms',
    licence: 'Licence/Registration',
    custom: 'Custom'
};

function ComplianceCard({ record, onEdit, onDelete }) {
    const status = statusConfig[record.compliance_status] || statusConfig.compliant;
    const StatusIcon = status.icon;
    
    const formatDate = (dateStr) => {
        if (!dateStr) return 'Not set';
        return new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    };

    return (
        <div 
            className={`bg-white border ${status.border} rounded-lg p-4 hover:shadow-md transition-all`}
            data-testid={`compliance-card-${record.id}`}
        >
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${status.bg} ${status.text}`}>
                        {categoryLabels[record.category] || record.category}
                    </span>
                </div>
                <div className="flex items-center gap-1">
                    <button 
                        onClick={() => onEdit(record)}
                        className="p-1.5 hover:bg-slate-100 rounded transition-colors"
                        data-testid={`edit-compliance-${record.id}`}
                    >
                        <Pencil className="w-3.5 h-3.5 text-slate-400" />
                    </button>
                    <button 
                        onClick={() => onDelete(record.id)}
                        className="p-1.5 hover:bg-red-50 rounded transition-colors"
                        data-testid={`delete-compliance-${record.id}`}
                    >
                        <Trash2 className="w-3.5 h-3.5 text-slate-400 hover:text-red-500" />
                    </button>
                </div>
            </div>
            
            <h4 className="font-medium text-slate-900 mb-2">{record.title}</h4>
            
            <div className="flex items-center gap-4 text-sm text-slate-500">
                <div className="flex items-center gap-1.5">
                    <StatusIcon className={`w-4 h-4 ${status.text}`} />
                    <span className={status.text}>{status.label}</span>
                </div>
                {record.expiry_date && (
                    <div className="flex items-center gap-1.5">
                        <Calendar className="w-4 h-4" />
                        <span>Expires: {formatDate(record.expiry_date)}</span>
                    </div>
                )}
            </div>
            
            {record.notes && (
                <p className="mt-2 text-sm text-slate-500 line-clamp-2">{record.notes}</p>
            )}
        </div>
    );
}

export default function PropertyDetailPage() {
    const { propertyId } = useParams();
    const navigate = useNavigate();
    const [property, setProperty] = useState(null);
    const [complianceRecords, setComplianceRecords] = useState([]);
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [propertyModalOpen, setPropertyModalOpen] = useState(false);
    const [complianceModalOpen, setComplianceModalOpen] = useState(false);
    const [bulkModalOpen, setBulkModalOpen] = useState(false);
    const [taskModalOpen, setTaskModalOpen] = useState(false);
    const [uploadModalOpen, setUploadModalOpen] = useState(false);
    const [editingRecord, setEditingRecord] = useState(null);

    const fetchData = async () => {
        try {
            const [propRes, compRes, taskRes] = await Promise.all([
                axios.get(`${API_URL}/api/properties/${propertyId}`),
                axios.get(`${API_URL}/api/compliance-records`, { params: { property_id: propertyId } }),
                axios.get(`${API_URL}/api/tasks`, { params: { property_id: propertyId } })
            ]);
            setProperty(propRes.data);
            setComplianceRecords(compRes.data);
            setTasks(taskRes.data);
        } catch (error) {
            console.error('Failed to fetch property data:', error);
            if (error.response?.status === 404) {
                navigate('/app/properties');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [propertyId]);

    const handleUpdateProperty = async (propertyData) => {
        try {
            const response = await axios.put(`${API_URL}/api/properties/${propertyId}`, propertyData);
            setProperty(response.data);
            setPropertyModalOpen(false);
        } catch (error) {
            console.error('Failed to update property:', error);
            throw error;
        }
    };

    const handleSaveComplianceRecord = async (recordData) => {
        try {
            if (editingRecord) {
                const response = await axios.put(`${API_URL}/api/compliance-records/${editingRecord.id}`, recordData);
                setComplianceRecords(complianceRecords.map(r => r.id === editingRecord.id ? response.data : r));
            } else {
                const response = await axios.post(`${API_URL}/api/compliance-records`, { ...recordData, property_id: propertyId });
                setComplianceRecords([...complianceRecords, response.data]);
            }
            setComplianceModalOpen(false);
            setEditingRecord(null);
            fetchData(); // Refresh to update summary
        } catch (error) {
            console.error('Failed to save compliance record:', error);
            throw error;
        }
    };

    const handleDeleteComplianceRecord = async (recordId) => {
        if (!window.confirm('Are you sure you want to delete this compliance record?')) return;
        try {
            await axios.delete(`${API_URL}/api/compliance-records/${recordId}`);
            setComplianceRecords(complianceRecords.filter(r => r.id !== recordId));
            fetchData(); // Refresh summary
        } catch (error) {
            console.error('Failed to delete compliance record:', error);
        }
    };

    const handleSaveTask = async (taskData) => {
        try {
            const response = await axios.post(`${API_URL}/api/tasks`, taskData);
            setTasks([...tasks, response.data]);
            setTaskModalOpen(false);
        } catch (error) {
            console.error('Failed to save task:', error);
            throw error;
        }
    };

    const handleToggleTaskStatus = async (taskId, newStatus) => {
        try {
            const response = await axios.put(`${API_URL}/api/tasks/${taskId}`, { task_status: newStatus });
            setTasks(tasks.map(t => t.id === taskId ? response.data : t));
            // Refresh to get any new recurring tasks
            if (newStatus === 'completed') {
                setTimeout(fetchData, 500);
            }
        } catch (error) {
            console.error('Failed to update task:', error);
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

    const formatLabel = (str) => str?.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') || '';

    if (loading) {
        return (
            <div className="animate-pulse space-y-6">
                <div className="h-8 bg-slate-200 rounded w-48" />
                <div className="h-40 bg-slate-200 rounded-lg" />
                <div className="h-64 bg-slate-200 rounded-lg" />
            </div>
        );
    }

    if (!property) {
        return <div>Property not found</div>;
    }

    const summary = property.compliance_summary || { total: 0, compliant: 0, expiring_soon: 0, overdue: 0, missing: 0 };

    return (
        <div data-testid="property-detail-page">
            {/* Back button */}
            <button 
                onClick={() => navigate('/app/properties')}
                className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 mb-4 transition-colors"
                data-testid="back-to-properties"
            >
                <ArrowLeft className="w-4 h-4" />
                Back to Properties
            </button>

            {/* Property header */}
            <div className="bg-white border border-slate-200 rounded-lg p-6 mb-6">
                <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
                    <div className="flex items-start gap-4">
                        <div className="p-3 bg-blue-100 rounded-lg">
                            <Building2 className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                {property.name}
                            </h1>
                            <div className="flex items-center gap-2 text-slate-500 mt-1">
                                <MapPin className="w-4 h-4" />
                                <span>{property.address}, {property.postcode}</span>
                            </div>
                            <div className="flex items-center gap-4 mt-2 text-sm text-slate-500">
                                <span className="flex items-center gap-1">
                                    <Home className="w-4 h-4" />
                                    {formatLabel(property.property_type)} • {property.bedrooms} bed
                                </span>
                                <span>{property.uk_nation}</span>
                                {property.is_in_london && (
                                    <span className="px-2 py-0.5 bg-slate-100 rounded text-xs">London</span>
                                )}
                            </div>
                        </div>
                    </div>
                    <Button 
                        variant="outline" 
                        onClick={() => setPropertyModalOpen(true)}
                        data-testid="edit-property-btn"
                    >
                        <Pencil className="w-4 h-4 mr-2" />
                        Edit Property
                    </Button>
                </div>

                {property.notes && (
                    <p className="mt-4 text-sm text-slate-600 bg-slate-50 p-3 rounded-lg">{property.notes}</p>
                )}

                {/* Status summary */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-6 pt-6 border-t border-slate-100">
                    <div className="text-center p-3 bg-slate-50 rounded-lg">
                        <p className="text-2xl font-bold text-slate-900">{summary.total}</p>
                        <p className="text-xs text-slate-500">Total Records</p>
                    </div>
                    <div className="text-center p-3 bg-emerald-50 rounded-lg">
                        <p className="text-2xl font-bold text-emerald-700">{summary.compliant}</p>
                        <p className="text-xs text-emerald-600">Compliant</p>
                    </div>
                    <div className="text-center p-3 bg-amber-50 rounded-lg">
                        <p className="text-2xl font-bold text-amber-700">{summary.expiring_soon}</p>
                        <p className="text-xs text-amber-600">Expiring Soon</p>
                    </div>
                    <div className="text-center p-3 bg-red-50 rounded-lg">
                        <p className="text-2xl font-bold text-red-700">{summary.overdue}</p>
                        <p className="text-xs text-red-600">Overdue</p>
                    </div>
                    <div className="text-center p-3 bg-slate-100 rounded-lg">
                        <p className="text-2xl font-bold text-slate-700">{summary.missing}</p>
                        <p className="text-xs text-slate-500">Missing</p>
                    </div>
                </div>
            </div>

            {/* Compliance records */}
            <div className="mb-6">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        Compliance Records
                    </h2>
                    <div className="flex items-center gap-2">
                        {complianceRecords.length === 0 && (
                            <Button 
                                variant="outline"
                                onClick={() => setBulkModalOpen(true)}
                                className="border-blue-200 text-blue-700 hover:bg-blue-50"
                                data-testid="quick-setup-btn"
                            >
                                <Zap className="w-4 h-4 mr-2" />
                                Quick Setup
                            </Button>
                        )}
                        <Button 
                            variant="outline"
                            onClick={() => setUploadModalOpen(true)}
                            className="border-purple-200 text-purple-700 hover:bg-purple-50"
                            data-testid="upload-document-btn"
                        >
                            <Sparkles className="w-4 h-4 mr-2" />
                            Upload Document
                        </Button>
                        <Button 
                            onClick={() => { setEditingRecord(null); setComplianceModalOpen(true); }}
                            className="bg-blue-600 hover:bg-blue-700 text-white"
                            data-testid="add-compliance-btn"
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            Add Record
                        </Button>
                    </div>
                </div>

                {complianceRecords.length === 0 ? (
                    <div className="bg-white rounded-lg border border-slate-200">
                        <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
                            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-6">
                                <Zap className="w-8 h-8 text-blue-600" />
                            </div>
                            <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                Set up compliance tracking
                            </h3>
                            <p className="text-sm text-slate-500 max-w-sm mb-6">
                                Use Quick Setup to add all required certificates at once, or add them one by one.
                            </p>
                            <div className="flex items-center gap-3">
                                <Button 
                                    onClick={() => setBulkModalOpen(true)}
                                    className="bg-blue-600 hover:bg-blue-700 text-white"
                                    data-testid="empty-quick-setup-btn"
                                >
                                    <Zap className="w-4 h-4 mr-2" />
                                    Quick Setup
                                </Button>
                                <Button 
                                    variant="outline"
                                    onClick={() => { setEditingRecord(null); setComplianceModalOpen(true); }}
                                >
                                    Add Single Record
                                </Button>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {complianceRecords.map((record) => (
                            <ComplianceCard
                                key={record.id}
                                record={record}
                                onEdit={(r) => { setEditingRecord(r); setComplianceModalOpen(true); }}
                                onDelete={handleDeleteComplianceRecord}
                            />
                        ))}
                    </div>
                )}
            </div>

            {/* Tasks section placeholder */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        Tasks
                    </h2>
                    <div className="flex items-center gap-2">
                        <Button 
                            onClick={() => setTaskModalOpen(true)}
                            className="bg-blue-600 hover:bg-blue-700 text-white"
                            data-testid="add-task-btn"
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            Add Task
                        </Button>
                    </div>
                </div>
                
                {tasks.length === 0 ? (
                    <div className="bg-white rounded-lg border border-slate-200 p-8 text-center">
                        <ListTodo className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                        <p className="text-sm text-slate-500 mb-4">No tasks for this property</p>
                        <Button 
                            variant="outline"
                            onClick={() => setTaskModalOpen(true)}
                        >
                            <Plus className="w-4 h-4 mr-2" />
                            Create Task
                        </Button>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {tasks.slice(0, 5).map((task) => {
                            const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.task_status !== 'completed';
                            const isCompleted = task.task_status === 'completed';
                            
                            return (
                                <div 
                                    key={task.id}
                                    className={`bg-white border rounded-lg p-4 ${isOverdue ? 'border-red-200 bg-red-50/30' : 'border-slate-200'}`}
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <button
                                                onClick={() => handleToggleTaskStatus(task.id, isCompleted ? 'pending' : 'completed')}
                                                className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${
                                                    isCompleted 
                                                        ? 'bg-emerald-500 border-emerald-500 text-white' 
                                                        : 'border-slate-300 hover:border-blue-400'
                                                }`}
                                            >
                                                {isCompleted && <CheckCircle2 className="w-3 h-3" />}
                                            </button>
                                            <div>
                                                <p className={`font-medium ${isCompleted ? 'text-slate-400 line-through' : 'text-slate-900'}`}>
                                                    {task.title}
                                                </p>
                                                <div className="flex items-center gap-2 mt-1">
                                                    {task.due_date && (
                                                        <span className={`text-xs flex items-center gap-1 ${isOverdue ? 'text-red-600' : 'text-slate-500'}`}>
                                                            <Calendar className="w-3 h-3" />
                                                            {new Date(task.due_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
                                                            {isOverdue && <AlertCircle className="w-3 h-3" />}
                                                        </span>
                                                    )}
                                                    {task.is_recurring && (
                                                        <span className="text-xs flex items-center gap-1 text-purple-600">
                                                            <RefreshCw className="w-3 h-3" />
                                                            {task.recurrence_pattern}
                                                        </span>
                                                    )}
                                                    <span className={`text-xs px-2 py-0.5 rounded ${
                                                        task.priority === 'urgent' ? 'bg-red-100 text-red-700' :
                                                        task.priority === 'high' ? 'bg-amber-100 text-amber-700' :
                                                        task.priority === 'medium' ? 'bg-blue-100 text-blue-700' :
                                                        'bg-slate-100 text-slate-600'
                                                    }`}>
                                                        {task.priority}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleDeleteTask(task.id)}
                                            className="p-1.5 hover:bg-slate-100 rounded text-slate-400 hover:text-red-500"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            );
                        })}
                        {tasks.length > 5 && (
                            <Button 
                                variant="ghost" 
                                className="w-full"
                                onClick={() => navigate('/app/tasks')}
                            >
                                View all {tasks.length} tasks
                            </Button>
                        )}
                    </div>
                )}
            </div>

            {/* Modals */}
            <PropertyModal
                isOpen={propertyModalOpen}
                onClose={() => setPropertyModalOpen(false)}
                onSave={handleUpdateProperty}
                property={property}
            />

            <ComplianceRecordModal
                isOpen={complianceModalOpen}
                onClose={() => { setComplianceModalOpen(false); setEditingRecord(null); }}
                onSave={handleSaveComplianceRecord}
                record={editingRecord}
                propertyId={propertyId}
            />

            <BulkComplianceModal
                isOpen={bulkModalOpen}
                onClose={() => setBulkModalOpen(false)}
                onComplete={fetchData}
                propertyId={propertyId}
                propertyName={property?.name}
            />

            <TaskModal
                isOpen={taskModalOpen}
                onClose={() => setTaskModalOpen(false)}
                onSave={handleSaveTask}
                propertyId={propertyId}
            />

            <UploadDocumentModal
                isOpen={uploadModalOpen}
                onClose={() => setUploadModalOpen(false)}
                propertyId={propertyId}
                mode="extract"
                onRecordCreated={(record) => {
                    setComplianceRecords([...complianceRecords, record]);
                    fetchData(); // Refresh to get updated summary
                }}
            />
        </div>
    );
}
