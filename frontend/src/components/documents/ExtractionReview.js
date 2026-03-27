import { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { 
    AlertCircle, 
    CheckCircle2, 
    HelpCircle,
    FileText,
    Calendar,
    Tag,
    Sparkles,
    Edit2
} from 'lucide-react';

const categoryLabels = {
    gas_safety: 'Gas Safety Certificate',
    eicr: 'EICR (Electrical Installation)',
    epc: 'EPC (Energy Performance)',
    insurance: 'Insurance',
    fire_risk_assessment: 'Fire Risk Assessment',
    pat_testing: 'PAT Testing',
    legionella: 'Legionella Risk Assessment',
    smoke_co_alarms: 'Smoke/CO Alarms',
    licence: 'Licence/Registration',
    custom: 'Custom Document'
};

const confidenceConfig = {
    HIGH: { 
        color: 'bg-emerald-100 text-emerald-700 border-emerald-200', 
        icon: CheckCircle2, 
        label: 'High confidence' 
    },
    MEDIUM: { 
        color: 'bg-amber-100 text-amber-700 border-amber-200', 
        icon: HelpCircle, 
        label: 'Review suggested' 
    },
    LOW: { 
        color: 'bg-slate-100 text-slate-600 border-slate-200', 
        icon: AlertCircle, 
        label: 'Low confidence' 
    },
    NOT_FOUND: { 
        color: 'bg-slate-50 text-slate-500 border-slate-200', 
        icon: AlertCircle, 
        label: 'Not detected' 
    }
};

function ConfidenceBadge({ confidence }) {
    const config = confidenceConfig[confidence] || confidenceConfig.LOW;
    const Icon = config.icon;
    
    return (
        <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${config.color}`}>
            <Icon className="w-3 h-3" />
            {config.label}
        </span>
    );
}

function SuggestedField({ 
    label, 
    value, 
    confidence, 
    rawText, 
    icon: Icon, 
    type = 'text',
    options = null,
    onChange,
    isEditing,
    onEditToggle 
}) {
    const [localValue, setLocalValue] = useState(value || '');
    
    useEffect(() => {
        setLocalValue(value || '');
    }, [value]);
    
    const handleChange = (newValue) => {
        setLocalValue(newValue);
        onChange(newValue);
    };
    
    const isSuggested = confidence && confidence !== 'NOT_FOUND';
    
    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <Label className="flex items-center gap-2 text-slate-700">
                    <Icon className="w-4 h-4 text-slate-400" />
                    {label}
                </Label>
                {isSuggested && (
                    <div className="flex items-center gap-2">
                        <ConfidenceBadge confidence={confidence} />
                        {!isEditing && (
                            <button 
                                onClick={onEditToggle}
                                className="p-1 hover:bg-slate-100 rounded text-slate-400 hover:text-slate-600"
                                title="Edit value"
                            >
                                <Edit2 className="w-3.5 h-3.5" />
                            </button>
                        )}
                    </div>
                )}
            </div>
            
            {options ? (
                <Select value={localValue} onValueChange={handleChange}>
                    <SelectTrigger className={isSuggested && !isEditing ? 'border-blue-200 bg-blue-50/50' : ''}>
                        <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                        {Object.entries(options).map(([key, label]) => (
                            <SelectItem key={key} value={key}>{label}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            ) : (
                <Input
                    type={type}
                    value={localValue}
                    onChange={(e) => handleChange(e.target.value)}
                    className={isSuggested && !isEditing ? 'border-blue-200 bg-blue-50/50' : ''}
                    placeholder={type === 'date' ? 'YYYY-MM-DD' : `Enter ${label.toLowerCase()}`}
                />
            )}
            
            {rawText && isSuggested && (
                <p className="text-xs text-slate-500 flex items-center gap-1">
                    <Sparkles className="w-3 h-3" />
                    Detected: "{rawText}"
                </p>
            )}
        </div>
    );
}

export default function ExtractionReview({ 
    extraction, 
    document,
    onConfirm, 
    onCancel,
    isCreatingNew = false 
}) {
    const suggestions = extraction?.suggestions || {};
    
    const [formData, setFormData] = useState({
        title: suggestions.title?.value || '',
        category: suggestions.category?.value || 'custom',
        issue_date: suggestions.issue_date?.value || '',
        expiry_date: suggestions.expiry_date?.value || '',
        notes: suggestions.notes?.value || ''
    });
    
    const [editingFields, setEditingFields] = useState({});
    const [loading, setLoading] = useState(false);
    
    const updateField = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };
    
    const toggleEditing = (field) => {
        setEditingFields(prev => ({ ...prev, [field]: !prev[field] }));
    };
    
    const handleConfirm = async () => {
        setLoading(true);
        try {
            await onConfirm(formData, document?.id);
        } finally {
            setLoading(false);
        }
    };
    
    const confidenceSummary = suggestions.confidence_summary || 'LOW';
    const hasAnySuggestions = suggestions.category || suggestions.issue_date || suggestions.expiry_date;
    
    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start gap-4 pb-4 border-b border-slate-200">
                <div className="p-3 bg-blue-100 rounded-lg">
                    <FileText className="w-6 h-6 text-blue-600" />
                </div>
                <div className="flex-1">
                    <h3 className="font-semibold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        {isCreatingNew ? 'Create Record from Document' : 'Review Extracted Information'}
                    </h3>
                    <p className="text-sm text-slate-500 mt-1">
                        {document?.original_filename || 'Uploaded document'}
                    </p>
                    
                    {hasAnySuggestions && (
                        <div className="mt-2 p-3 bg-blue-50 border border-blue-100 rounded-lg">
                            <div className="flex items-center gap-2 text-sm">
                                <Sparkles className="w-4 h-4 text-blue-600" />
                                <span className="text-blue-800">
                                    {confidenceSummary === 'HIGH' 
                                        ? 'High confidence extraction - please verify the values below'
                                        : confidenceSummary === 'MEDIUM'
                                        ? 'Some values were extracted - please review and correct if needed'
                                        : 'Limited extraction - please fill in the details manually'
                                    }
                                </span>
                            </div>
                        </div>
                    )}
                    
                    {!hasAnySuggestions && (
                        <div className="mt-2 p-3 bg-amber-50 border border-amber-100 rounded-lg">
                            <div className="flex items-center gap-2 text-sm text-amber-800">
                                <AlertCircle className="w-4 h-4" />
                                <span>Could not extract information automatically. Please fill in the details manually.</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>
            
            {/* Form fields */}
            <div className="space-y-4">
                <SuggestedField
                    label="Document Title"
                    value={formData.title}
                    confidence={suggestions.title?.confidence}
                    icon={FileText}
                    onChange={(v) => updateField('title', v)}
                    isEditing={editingFields.title}
                    onEditToggle={() => toggleEditing('title')}
                />
                
                <SuggestedField
                    label="Category"
                    value={formData.category}
                    confidence={suggestions.category?.confidence}
                    icon={Tag}
                    options={categoryLabels}
                    onChange={(v) => updateField('category', v)}
                    isEditing={editingFields.category}
                    onEditToggle={() => toggleEditing('category')}
                />
                
                <div className="grid grid-cols-2 gap-4">
                    <SuggestedField
                        label="Issue Date"
                        value={formData.issue_date}
                        confidence={suggestions.issue_date?.confidence}
                        rawText={suggestions.issue_date?.raw_text}
                        icon={Calendar}
                        type="date"
                        onChange={(v) => updateField('issue_date', v)}
                        isEditing={editingFields.issue_date}
                        onEditToggle={() => toggleEditing('issue_date')}
                    />
                    
                    <SuggestedField
                        label="Expiry Date"
                        value={formData.expiry_date}
                        confidence={suggestions.expiry_date?.confidence}
                        rawText={suggestions.expiry_date?.raw_text}
                        icon={Calendar}
                        type="date"
                        onChange={(v) => updateField('expiry_date', v)}
                        isEditing={editingFields.expiry_date}
                        onEditToggle={() => toggleEditing('expiry_date')}
                    />
                </div>
                
                <div className="space-y-2">
                    <Label className="text-slate-700">Notes (optional)</Label>
                    <textarea
                        value={formData.notes}
                        onChange={(e) => updateField('notes', e.target.value)}
                        className="flex min-h-[80px] w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Add any additional notes..."
                    />
                </div>
            </div>
            
            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-200">
                <p className="text-xs text-slate-500">
                    You can always edit these values later
                </p>
                <div className="flex items-center gap-3">
                    <Button variant="outline" onClick={onCancel} disabled={loading}>
                        Cancel
                    </Button>
                    <Button 
                        onClick={handleConfirm}
                        disabled={loading || !formData.title || !formData.category}
                        className="bg-blue-600 hover:bg-blue-700 text-white"
                    >
                        {loading ? 'Saving...' : isCreatingNew ? 'Create Record' : 'Save Record'}
                    </Button>
                </div>
            </div>
        </div>
    );
}
