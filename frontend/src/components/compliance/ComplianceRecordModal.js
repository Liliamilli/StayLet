import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Loader2 } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const categoryLabels = {
    gas_safety: 'Gas Safety Certificate (CP12)',
    eicr: 'EICR (Electrical Installation)',
    epc: 'EPC (Energy Performance)',
    insurance: 'Landlord Insurance',
    fire_risk_assessment: 'Fire Risk Assessment',
    pat_testing: 'PAT Testing',
    legionella: 'Legionella Risk Assessment',
    smoke_co_alarms: 'Smoke/CO Alarm Check',
    licence: 'Licence/Registration',
    custom: 'Custom Item'
};

export default function ComplianceRecordModal({ isOpen, onClose, onSave, record, propertyId }) {
    const [loading, setLoading] = useState(false);
    const [constants, setConstants] = useState(null);
    const [formData, setFormData] = useState({
        title: '',
        category: 'gas_safety',
        issue_date: '',
        expiry_date: '',
        reminder_preference: '30_days',
        notes: ''
    });
    const [errors, setErrors] = useState({});

    useEffect(() => {
        const fetchConstants = async () => {
            try {
                const response = await axios.get(`${API_URL}/api/constants`);
                setConstants(response.data);
            } catch (error) {
                console.error('Failed to fetch constants:', error);
            }
        };
        fetchConstants();
    }, []);

    useEffect(() => {
        if (record) {
            setFormData({
                title: record.title || '',
                category: record.category || 'gas_safety',
                issue_date: record.issue_date ? record.issue_date.split('T')[0] : '',
                expiry_date: record.expiry_date ? record.expiry_date.split('T')[0] : '',
                reminder_preference: record.reminder_preference || '30_days',
                notes: record.notes || ''
            });
        } else {
            setFormData({
                title: '',
                category: 'gas_safety',
                issue_date: '',
                expiry_date: '',
                reminder_preference: '30_days',
                notes: ''
            });
        }
        setErrors({});
    }, [record, isOpen]);

    // Auto-fill title based on category
    useEffect(() => {
        if (!record && formData.category && !formData.title) {
            setFormData(prev => ({ ...prev, title: categoryLabels[formData.category] || '' }));
        }
    }, [formData.category, record]);

    const validate = () => {
        const newErrors = {};
        if (!formData.title.trim()) newErrors.title = 'Title is required';
        if (!formData.category) newErrors.category = 'Category is required';
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validate()) return;
        
        setLoading(true);
        try {
            const submitData = {
                ...formData,
                property_id: propertyId,
                issue_date: formData.issue_date || null,
                expiry_date: formData.expiry_date || null
            };
            await onSave(submitData);
        } catch (error) {
            console.error('Save error:', error);
        } finally {
            setLoading(false);
        }
    };

    const reminderLabels = {
        none: 'No reminder',
        '30_days': '30 days before',
        '60_days': '60 days before',
        '90_days': '90 days before'
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle style={{ fontFamily: 'Outfit, sans-serif' }}>
                        {record ? 'Edit Compliance Record' : 'Add Compliance Record'}
                    </DialogTitle>
                </DialogHeader>

                <form onSubmit={handleSubmit} className="space-y-4 py-4">
                    <div className="space-y-2">
                        <Label htmlFor="category">Category *</Label>
                        <Select
                            value={formData.category}
                            onValueChange={(value) => {
                                setFormData({ 
                                    ...formData, 
                                    category: value,
                                    title: record ? formData.title : (categoryLabels[value] || '')
                                });
                            }}
                        >
                            <SelectTrigger data-testid="compliance-category-select">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                {Object.entries(categoryLabels).map(([key, label]) => (
                                    <SelectItem key={key} value={key}>{label}</SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        {errors.category && <p className="text-xs text-red-500">{errors.category}</p>}
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="title">Title *</Label>
                        <Input
                            id="title"
                            value={formData.title}
                            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                            placeholder="e.g., Gas Safety Certificate 2024"
                            className={errors.title ? 'border-red-500' : ''}
                            data-testid="compliance-title-input"
                        />
                        {errors.title && <p className="text-xs text-red-500">{errors.title}</p>}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="issue_date">Issue Date</Label>
                            <Input
                                id="issue_date"
                                type="date"
                                value={formData.issue_date}
                                onChange={(e) => setFormData({ ...formData, issue_date: e.target.value })}
                                data-testid="compliance-issue-date"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="expiry_date">Expiry Date</Label>
                            <Input
                                id="expiry_date"
                                type="date"
                                value={formData.expiry_date}
                                onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                                data-testid="compliance-expiry-date"
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="reminder_preference">Reminder</Label>
                        <Select
                            value={formData.reminder_preference}
                            onValueChange={(value) => setFormData({ ...formData, reminder_preference: value })}
                        >
                            <SelectTrigger data-testid="compliance-reminder-select">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                {(constants?.reminder_options || ['none', '30_days', '60_days', '90_days']).map((option) => (
                                    <SelectItem key={option} value={option}>
                                        {reminderLabels[option] || option}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="notes">Notes</Label>
                        <textarea
                            id="notes"
                            value={formData.notes}
                            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                            placeholder="Any additional notes..."
                            className="flex min-h-[80px] w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            data-testid="compliance-notes-input"
                        />
                    </div>

                    <DialogFooter className="pt-4">
                        <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
                            Cancel
                        </Button>
                        <Button 
                            type="submit" 
                            className="bg-blue-600 hover:bg-blue-700 text-white"
                            disabled={loading}
                            data-testid="save-compliance-btn"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Saving...
                                </>
                            ) : (
                                record ? 'Update Record' : 'Add Record'
                            )}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
