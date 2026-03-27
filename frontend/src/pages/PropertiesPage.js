import { useNavigate } from 'react-router-dom';
import EmptyState from '../components/shared/EmptyState';
import { Building2 } from 'lucide-react';

export default function PropertiesPage() {
    const navigate = useNavigate();

    return (
        <div data-testid="properties-page">
            {/* Page header */}
            <div className="mb-8">
                <h1 
                    className="text-2xl font-bold text-slate-900 mb-1"
                    style={{ fontFamily: 'Outfit, sans-serif' }}
                >
                    Properties
                </h1>
                <p className="text-slate-500">
                    Manage your short-let properties
                </p>
            </div>

            {/* Empty state */}
            <div className="bg-white rounded-lg border border-slate-200">
                <EmptyState
                    icon={Building2}
                    title="No properties yet"
                    description="Add your first property to start tracking compliance documents, certificates, and deadlines."
                    actionLabel="Add Property"
                    onAction={() => {}}
                />
            </div>
        </div>
    );
}
