import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Button } from '../ui/button';
import { Checkbox } from '../ui/checkbox';
import { Label } from '../ui/label';
import { Loader2, Zap, CheckCircle2 } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const complianceTemplates = [
    { 
        category: 'gas_safety', 
        title: 'Gas Safety Certificate (CP12)', 
        description: 'Annual gas safety check required for all gas appliances',
        required: true
    },
    { 
        category: 'eicr', 
        title: 'EICR (Electrical Installation)', 
        description: 'Electrical safety check, valid for 5 years',
        required: true
    },
    { 
        category: 'epc', 
        title: 'EPC (Energy Performance Certificate)', 
        description: 'Energy rating certificate, valid for 10 years',
        required: true
    },
    { 
        category: 'insurance', 
        title: 'Landlord Insurance', 
        description: 'Property and liability insurance coverage',
        required: true
    },
    { 
        category: 'fire_risk_assessment', 
        title: 'Fire Risk Assessment', 
        description: 'Assessment of fire hazards and safety measures',
        required: false
    },
    { 
        category: 'pat_testing', 
        title: 'PAT Testing', 
        description: 'Portable appliance testing for electrical items',
        required: false
    },
    { 
        category: 'legionella', 
        title: 'Legionella Risk Assessment', 
        description: 'Water system safety assessment',
        required: false
    },
    { 
        category: 'smoke_co_alarms', 
        title: 'Smoke & CO Alarm Check', 
        description: 'Annual check of smoke and carbon monoxide alarms',
        required: true
    },
    { 
        category: 'licence', 
        title: 'Property Licence/Registration', 
        description: 'Local authority licence or registration if required',
        required: false
    }
];

export default function BulkComplianceModal({ isOpen, onClose, onComplete, propertyId, propertyName }) {
    const [loading, setLoading] = useState(false);
    const [selectedCategories, setSelectedCategories] = useState([]);
    const [completed, setCompleted] = useState(false);
    const [createdCount, setCreatedCount] = useState(0);

    useEffect(() => {
        if (isOpen) {
            // Pre-select required items
            setSelectedCategories(
                complianceTemplates
                    .filter(t => t.required)
                    .map(t => t.category)
            );
            setCompleted(false);
            setCreatedCount(0);
        }
    }, [isOpen]);

    const toggleCategory = (category) => {
        setSelectedCategories(prev => 
            prev.includes(category)
                ? prev.filter(c => c !== category)
                : [...prev, category]
        );
    };

    const selectAll = () => {
        setSelectedCategories(complianceTemplates.map(t => t.category));
    };

    const selectNone = () => {
        setSelectedCategories([]);
    };

    const handleSubmit = async () => {
        if (selectedCategories.length === 0) return;
        
        setLoading(true);
        try {
            const promises = selectedCategories.map(category => {
                const template = complianceTemplates.find(t => t.category === category);
                return axios.post(`${API_URL}/api/compliance-records`, {
                    property_id: propertyId,
                    title: template.title,
                    category: category,
                    reminder_preference: '30_days',
                    notes: ''
                });
            });
            
            await Promise.all(promises);
            setCreatedCount(selectedCategories.length);
            setCompleted(true);
            
            // Auto-close after showing success
            setTimeout(() => {
                onComplete();
                onClose();
            }, 1500);
        } catch (error) {
            console.error('Failed to create compliance records:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        <Zap className="w-5 h-5 text-blue-600" />
                        Quick Setup
                    </DialogTitle>
                    <p className="text-sm text-slate-500">
                        Select the compliance documents you need to track for {propertyName || 'this property'}.
                    </p>
                </DialogHeader>

                {completed ? (
                    <div className="py-12 text-center">
                        <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <CheckCircle2 className="w-8 h-8 text-emerald-600" />
                        </div>
                        <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                            {createdCount} Records Created!
                        </h3>
                        <p className="text-sm text-slate-500">
                            Add expiry dates to start tracking compliance status.
                        </p>
                    </div>
                ) : (
                    <>
                        <div className="py-4">
                            {/* Quick actions */}
                            <div className="flex items-center justify-between mb-4">
                                <span className="text-sm text-slate-500">
                                    {selectedCategories.length} of {complianceTemplates.length} selected
                                </span>
                                <div className="flex gap-2">
                                    <button 
                                        onClick={selectAll}
                                        className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                                    >
                                        Select all
                                    </button>
                                    <span className="text-slate-300">|</span>
                                    <button 
                                        onClick={selectNone}
                                        className="text-xs text-slate-500 hover:text-slate-700 font-medium"
                                    >
                                        Clear
                                    </button>
                                </div>
                            </div>

                            {/* Checklist */}
                            <div className="space-y-3">
                                {complianceTemplates.map((template) => (
                                    <div 
                                        key={template.category}
                                        className={`
                                            flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-all
                                            ${selectedCategories.includes(template.category) 
                                                ? 'border-blue-200 bg-blue-50' 
                                                : 'border-slate-200 hover:border-slate-300'
                                            }
                                        `}
                                        onClick={() => toggleCategory(template.category)}
                                        data-testid={`bulk-item-${template.category}`}
                                    >
                                        <Checkbox
                                            checked={selectedCategories.includes(template.category)}
                                            onCheckedChange={() => toggleCategory(template.category)}
                                            className="mt-0.5"
                                        />
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2">
                                                <Label className="font-medium text-slate-900 cursor-pointer">
                                                    {template.title}
                                                </Label>
                                                {template.required && (
                                                    <span className="text-xs text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">
                                                        Recommended
                                                    </span>
                                                )}
                                            </div>
                                            <p className="text-xs text-slate-500 mt-0.5">
                                                {template.description}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <DialogFooter className="pt-4 border-t border-slate-100">
                            <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
                                Cancel
                            </Button>
                            <Button 
                                onClick={handleSubmit}
                                className="bg-blue-600 hover:bg-blue-700 text-white"
                                disabled={loading || selectedCategories.length === 0}
                                data-testid="bulk-create-btn"
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Creating...
                                    </>
                                ) : (
                                    <>
                                        <Zap className="w-4 h-4 mr-2" />
                                        Create {selectedCategories.length} Record{selectedCategories.length !== 1 ? 's' : ''}
                                    </>
                                )}
                            </Button>
                        </DialogFooter>
                    </>
                )}
            </DialogContent>
        </Dialog>
    );
}
