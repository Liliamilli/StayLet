import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { 
    Building2, 
    Plus, 
    Search,
    AlertCircle,
    Clock,
    CheckCircle2,
    FileX,
    MoreVertical,
    Pencil,
    Trash2
} from 'lucide-react';
import PropertyModal from '../components/properties/PropertyModal';
import UpgradePlanModal from '../components/billing/UpgradePlanModal';
import EmptyState from '../components/shared/EmptyState';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const statusColors = {
    compliant: { bg: 'bg-emerald-50', text: 'text-emerald-700', icon: CheckCircle2 },
    expiring_soon: { bg: 'bg-amber-50', text: 'text-amber-700', icon: Clock },
    overdue: { bg: 'bg-red-50', text: 'text-red-700', icon: AlertCircle },
    missing: { bg: 'bg-slate-50', text: 'text-slate-600', icon: FileX }
};

function PropertyCard({ property, onEdit, onDelete, onClick }) {
    const [menuOpen, setMenuOpen] = useState(false);
    const summary = property.compliance_summary || { total: 0, compliant: 0, expiring_soon: 0, overdue: 0, missing: 0 };
    
    const getOverallStatus = () => {
        if (summary.overdue > 0) return 'overdue';
        if (summary.expiring_soon > 0) return 'expiring_soon';
        if (summary.missing > 0) return 'missing';
        return 'compliant';
    };
    
    const status = getOverallStatus();
    const StatusIcon = statusColors[status]?.icon || CheckCircle2;

    return (
        <div 
            className="bg-white border border-slate-200 rounded-lg p-5 hover:shadow-md hover:border-slate-300 transition-all cursor-pointer relative"
            onClick={() => onClick(property.id)}
            data-testid={`property-card-${property.id}`}
        >
            {/* Menu button */}
            <div className="absolute top-4 right-4" onClick={e => e.stopPropagation()}>
                <button 
                    onClick={() => setMenuOpen(!menuOpen)}
                    className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
                    data-testid={`property-menu-${property.id}`}
                >
                    <MoreVertical className="w-4 h-4 text-slate-400" />
                </button>
                {menuOpen && (
                    <div className="absolute right-0 mt-1 w-36 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-10">
                        <button 
                            onClick={() => { onEdit(property); setMenuOpen(false); }}
                            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                            data-testid={`edit-property-${property.id}`}
                        >
                            <Pencil className="w-4 h-4" /> Edit
                        </button>
                        <button 
                            onClick={() => { onDelete(property.id); setMenuOpen(false); }}
                            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                            data-testid={`delete-property-${property.id}`}
                        >
                            <Trash2 className="w-4 h-4" /> Delete
                        </button>
                    </div>
                )}
            </div>

            {/* Property info */}
            <div className="flex items-start gap-4 mb-4">
                <div className={`p-2.5 rounded-lg ${statusColors[status]?.bg || 'bg-slate-100'}`}>
                    <Building2 className={`w-5 h-5 ${statusColors[status]?.text || 'text-slate-600'}`} />
                </div>
                <div className="flex-1 min-w-0 pr-8">
                    <h3 className="font-semibold text-slate-900 truncate" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        {property.name}
                    </h3>
                    <p className="text-sm text-slate-500 truncate">{property.address}</p>
                    <p className="text-xs text-slate-400 mt-1">{property.postcode} • {property.uk_nation}</p>
                </div>
            </div>

            {/* Status summary */}
            <div className="flex items-center gap-3 pt-3 border-t border-slate-100">
                <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full ${statusColors[status]?.bg}`}>
                    <StatusIcon className={`w-3.5 h-3.5 ${statusColors[status]?.text}`} />
                    <span className={`text-xs font-medium ${statusColors[status]?.text}`}>
                        {status === 'compliant' ? 'All compliant' : 
                         status === 'overdue' ? `${summary.overdue} overdue` :
                         status === 'expiring_soon' ? `${summary.expiring_soon} expiring` :
                         `${summary.missing} missing`}
                    </span>
                </div>
                <span className="text-xs text-slate-400">{summary.total} records</span>
            </div>
        </div>
    );
}

export default function PropertiesPage() {
    const navigate = useNavigate();
    const { subscription, refreshSubscription } = useAuth();
    const [properties, setProperties] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [modalOpen, setModalOpen] = useState(false);
    const [editingProperty, setEditingProperty] = useState(null);
    const [upgradeModalOpen, setUpgradeModalOpen] = useState(false);
    const [limitMessage, setLimitMessage] = useState('');

    const fetchProperties = async (searchQuery = '') => {
        try {
            const params = searchQuery ? { search: searchQuery } : {};
            const response = await axios.get(`${API_URL}/api/properties`, { params });
            setProperties(response.data);
        } catch (error) {
            console.error('Failed to fetch properties:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProperties();
    }, []);

    useEffect(() => {
        const timer = setTimeout(() => {
            fetchProperties(search);
        }, 300);
        return () => clearTimeout(timer);
    }, [search]);

    const handleCreateProperty = async () => {
        // Check plan limit before opening modal
        try {
            const response = await axios.get(`${API_URL}/api/subscription/check-limit`);
            if (!response.data.allowed) {
                setLimitMessage(response.data.message);
                setUpgradeModalOpen(true);
                return;
            }
        } catch (error) {
            console.error('Failed to check limit:', error);
        }
        
        setEditingProperty(null);
        setModalOpen(true);
    };

    const handleEditProperty = (property) => {
        setEditingProperty(property);
        setModalOpen(true);
    };

    const handleDeleteProperty = async (propertyId) => {
        if (!window.confirm('Are you sure you want to delete this property? This will also delete all associated compliance records and tasks.')) {
            return;
        }
        try {
            await axios.delete(`${API_URL}/api/properties/${propertyId}`);
            setProperties(properties.filter(p => p.id !== propertyId));
            // Refresh subscription to update property count
            refreshSubscription();
        } catch (error) {
            console.error('Failed to delete property:', error);
        }
    };

    const handleSaveProperty = async (propertyData) => {
        try {
            if (editingProperty) {
                const response = await axios.put(`${API_URL}/api/properties/${editingProperty.id}`, propertyData);
                setProperties(properties.map(p => p.id === editingProperty.id ? response.data : p));
            } else {
                const response = await axios.post(`${API_URL}/api/properties`, propertyData);
                setProperties([...properties, response.data]);
                // Refresh subscription to update property count
                refreshSubscription();
            }
            setModalOpen(false);
            setEditingProperty(null);
        } catch (error) {
            console.error('Failed to save property:', error);
            throw error;
        }
    };

    const handlePropertyClick = (propertyId) => {
        navigate(`/app/properties/${propertyId}`);
    };

    if (loading) {
        return (
            <div className="animate-pulse space-y-6">
                <div className="h-8 bg-slate-200 rounded w-48" />
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[...Array(3)].map((_, i) => (
                        <div key={i} className="h-40 bg-slate-200 rounded-lg" />
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div data-testid="properties-page">
            {/* Page header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        Properties
                    </h1>
                    <p className="text-slate-500">Manage your short-let properties</p>
                </div>
                <Button 
                    onClick={handleCreateProperty}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                    data-testid="add-property-btn"
                >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Property
                </Button>
            </div>

            {properties.length > 0 && (
                <div className="mb-6">
                    <div className="relative max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <Input
                            type="text"
                            placeholder="Search properties..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="pl-10"
                            data-testid="search-properties"
                        />
                    </div>
                </div>
            )}

            {properties.length === 0 ? (
                <div className="bg-white rounded-lg border border-slate-200">
                    <EmptyState
                        icon={Building2}
                        title="No properties yet"
                        description="Add your first property to start tracking compliance documents, certificates, and deadlines."
                        actionLabel="Add Property"
                        onAction={handleCreateProperty}
                    />
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {properties.map((property) => (
                        <PropertyCard
                            key={property.id}
                            property={property}
                            onEdit={handleEditProperty}
                            onDelete={handleDeleteProperty}
                            onClick={handlePropertyClick}
                        />
                    ))}
                </div>
            )}

            <PropertyModal
                isOpen={modalOpen}
                onClose={() => { setModalOpen(false); setEditingProperty(null); }}
                onSave={handleSaveProperty}
                property={editingProperty}
            />

            <UpgradePlanModal
                isOpen={upgradeModalOpen}
                onClose={() => setUpgradeModalOpen(false)}
                currentPlan={subscription?.plan || 'solo'}
                propertyCount={subscription?.property_count || properties.length}
                limitMessage={limitMessage}
            />
        </div>
    );
}
