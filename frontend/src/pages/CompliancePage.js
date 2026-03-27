import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import EmptyState from '../components/shared/EmptyState';
import { 
    ClipboardCheck, 
    AlertCircle, 
    Clock, 
    CheckCircle2, 
    FileX,
    Calendar,
    Building2,
    Filter
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const statusConfig = {
    compliant: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', icon: CheckCircle2, label: 'Compliant' },
    expiring_soon: { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', icon: Clock, label: 'Expiring Soon' },
    overdue: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', icon: AlertCircle, label: 'Overdue' },
    missing: { bg: 'bg-slate-50', text: 'text-slate-600', border: 'border-slate-200', icon: FileX, label: 'Missing' }
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

function ComplianceRow({ record, properties, onClick }) {
    const status = statusConfig[record.compliance_status] || statusConfig.compliant;
    const StatusIcon = status.icon;
    const property = properties.find(p => p.id === record.property_id);
    
    const formatDate = (dateStr) => {
        if (!dateStr) return '—';
        return new Date(dateStr).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
    };

    return (
        <tr 
            className="border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors"
            onClick={onClick}
            data-testid={`compliance-row-${record.id}`}
        >
            <td className="py-4 px-4">
                <div className="flex items-center gap-3">
                    <div className={`p-1.5 rounded ${status.bg}`}>
                        <StatusIcon className={`w-4 h-4 ${status.text}`} />
                    </div>
                    <div>
                        <p className="font-medium text-slate-900">{record.title}</p>
                        <p className="text-xs text-slate-500">{categoryLabels[record.category] || record.category}</p>
                    </div>
                </div>
            </td>
            <td className="py-4 px-4">
                <div className="flex items-center gap-2 text-sm text-slate-600">
                    <Building2 className="w-4 h-4 text-slate-400" />
                    {property?.name || 'Unknown Property'}
                </div>
            </td>
            <td className="py-4 px-4">
                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${status.bg} ${status.text}`}>
                    {status.label}
                </span>
            </td>
            <td className="py-4 px-4">
                <div className="flex items-center gap-2 text-sm text-slate-600">
                    <Calendar className="w-4 h-4 text-slate-400" />
                    {formatDate(record.expiry_date)}
                </div>
            </td>
        </tr>
    );
}

export default function CompliancePage() {
    const navigate = useNavigate();
    const [records, setRecords] = useState([]);
    const [properties, setProperties] = useState([]);
    const [loading, setLoading] = useState(true);
    const [statusFilter, setStatusFilter] = useState('all');
    const [categoryFilter, setCategoryFilter] = useState('all');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [recordsRes, propsRes] = await Promise.all([
                    axios.get(`${API_URL}/api/compliance-records`),
                    axios.get(`${API_URL}/api/properties`)
                ]);
                setRecords(recordsRes.data);
                setProperties(propsRes.data);
            } catch (error) {
                console.error('Failed to fetch compliance records:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const filteredRecords = records.filter(record => {
        if (statusFilter !== 'all' && record.compliance_status !== statusFilter) return false;
        if (categoryFilter !== 'all' && record.category !== categoryFilter) return false;
        return true;
    });

    // Sort by status priority: overdue > expiring_soon > missing > compliant
    const sortedRecords = [...filteredRecords].sort((a, b) => {
        const priority = { overdue: 0, expiring_soon: 1, missing: 2, compliant: 3 };
        return (priority[a.compliance_status] || 4) - (priority[b.compliance_status] || 4);
    });

    const handleRowClick = (record) => {
        navigate(`/app/properties/${record.property_id}`);
    };

    if (loading) {
        return (
            <div className="animate-pulse space-y-6">
                <div className="h-8 bg-slate-200 rounded w-48" />
                <div className="h-64 bg-slate-200 rounded-lg" />
            </div>
        );
    }

    return (
        <div data-testid="compliance-page">
            {/* Page header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        Compliance
                    </h1>
                    <p className="text-slate-500">Track certificates, documents, and renewal dates</p>
                </div>
            </div>

            {records.length === 0 ? (
                <EmptyState
                    icon={ClipboardCheck}
                    title="All your certificates in one place"
                    description="Start by adding a property, then upload your compliance documents—gas certs, EICRs, EPCs, and more. We'll track expiry dates and remind you before anything lapses."
                    actionLabel="Add a Property First"
                    onAction={() => navigate('/app/properties')}
                    tip="Our smart document extraction can read certificate PDFs and fill in the details automatically."
                    variant="featured"
                />
            ) : (
                <>
                    {/* Filters */}
                    <div className="flex flex-wrap items-center gap-3 mb-6">
                        <div className="flex items-center gap-2">
                            <Filter className="w-4 h-4 text-slate-400" />
                            <span className="text-sm text-slate-500">Filter:</span>
                        </div>
                        <Select value={statusFilter} onValueChange={setStatusFilter}>
                            <SelectTrigger className="w-40" data-testid="status-filter">
                                <SelectValue placeholder="Status" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Status</SelectItem>
                                <SelectItem value="compliant">Compliant</SelectItem>
                                <SelectItem value="expiring_soon">Expiring Soon</SelectItem>
                                <SelectItem value="overdue">Overdue</SelectItem>
                                <SelectItem value="missing">Missing</SelectItem>
                            </SelectContent>
                        </Select>
                        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                            <SelectTrigger className="w-40" data-testid="category-filter">
                                <SelectValue placeholder="Category" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="all">All Categories</SelectItem>
                                {Object.entries(categoryLabels).map(([key, label]) => (
                                    <SelectItem key={key} value={key}>{label}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <span className="text-sm text-slate-400">
                            {sortedRecords.length} record{sortedRecords.length !== 1 ? 's' : ''}
                        </span>
                    </div>

                    {/* Table */}
                    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden overflow-x-auto">
                        <table className="w-full min-w-[640px]">
                            <thead className="bg-slate-50">
                                <tr>
                                    <th className="text-left py-3 px-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                                        Record
                                    </th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                                        Property
                                    </th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                                        Status
                                    </th>
                                    <th className="text-left py-3 px-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
                                        Expiry Date
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {sortedRecords.map((record) => (
                                    <ComplianceRow
                                        key={record.id}
                                        record={record}
                                        properties={properties}
                                        onClick={() => handleRowClick(record)}
                                    />
                                ))}
                            </tbody>
                        </table>
                        
                        {sortedRecords.length === 0 && (
                            <div className="py-12 text-center text-sm text-slate-500">
                                No records match the current filters
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
