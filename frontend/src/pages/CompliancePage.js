import EmptyState from '../components/shared/EmptyState';
import { ClipboardCheck } from 'lucide-react';

export default function CompliancePage() {
    return (
        <div data-testid="compliance-page">
            {/* Page header */}
            <div className="mb-8">
                <h1 
                    className="text-2xl font-bold text-slate-900 mb-1"
                    style={{ fontFamily: 'Outfit, sans-serif' }}
                >
                    Compliance
                </h1>
                <p className="text-slate-500">
                    Track certificates, documents, and renewal dates
                </p>
            </div>

            {/* Empty state */}
            <div className="bg-white rounded-lg border border-slate-200">
                <EmptyState
                    icon={ClipboardCheck}
                    title="No compliance records yet"
                    description="Add a property first, then upload your compliance documents like gas certificates, EPC ratings, and EICR reports."
                    actionLabel="Add Property"
                    onAction={() => {}}
                />
            </div>
        </div>
    );
}
