import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Checkbox } from '../ui/checkbox';
import { Loader2 } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const priorityConfig = {
    low: { label: 'Low', color: 'text-slate-600' },
    medium: { label: 'Medium', color: 'text-blue-600' },
    high: { label: 'High', color: 'text-amber-600' },
    urgent: { label: 'Urgent', color: 'text-red-600' }
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

const recurrenceOptions = [
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'yearly', label: 'Yearly' }
];

export default function TaskModal({ isOpen, onClose, onSave, task, propertyId, properties = [] }) {
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        due_date: '',
        priority: 'medium',
        category: 'general',
        property_id: propertyId || '',
        is_recurring: false,
        recurrence_pattern: ''
    });
    const [errors, setErrors] = useState({});

    useEffect(() => {
        if (task) {
            setFormData({
                title: task.title || '',
                description: task.description || '',
                due_date: task.due_date ? task.due_date.split('T')[0] : '',
                priority: task.priority || 'medium',
                category: task.category || 'general',
                property_id: task.property_id || propertyId || '',
                is_recurring: task.is_recurring || false,
                recurrence_pattern: task.recurrence_pattern || ''
            });
        } else {
            setFormData({
                title: '',
                description: '',
                due_date: '',
                priority: 'medium',
                category: 'general',
                property_id: propertyId || '',
                is_recurring: false,
                recurrence_pattern: ''
            });
        }
        setErrors({});
    }, [task, propertyId, isOpen]);

    const validate = () => {
        const newErrors = {};
        if (!formData.title.trim()) newErrors.title = 'Task title is required';
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
                due_date: formData.due_date || null,
                property_id: formData.property_id || null,
                recurrence_pattern: formData.is_recurring ? formData.recurrence_pattern : null
            };
            await onSave(submitData);
        } catch (error) {
            console.error('Save error:', error);
            const errorMsg = error.response?.data?.detail;
            if (errorMsg) {
                setErrors({ general: errorMsg });
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle style={{ fontFamily: 'Outfit, sans-serif' }}>
                        {task ? 'Edit Task' : 'Create Task'}
                    </DialogTitle>
                    <DialogDescription>
                        {task ? 'Update the task details below.' : 'Add a new task to track.'}
                    </DialogDescription>
                </DialogHeader>

                <form onSubmit={handleSubmit} className="space-y-4 py-4">
                    {errors.general && (
                        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                            {errors.general}
                        </div>
                    )}

                    <div className="space-y-2">
                        <Label htmlFor="title">Task Title *</Label>
                        <Input
                            id="title"
                            value={formData.title}
                            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                            placeholder="e.g., Schedule gas safety inspection"
                            className={errors.title ? 'border-red-500' : ''}
                            data-testid="task-title-input"
                        />
                        {errors.title && <p className="text-xs text-red-500">{errors.title}</p>}
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <textarea
                            id="description"
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            placeholder="Add details about this task..."
                            className="flex min-h-[80px] w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            data-testid="task-description-input"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="due_date">Due Date</Label>
                            <Input
                                id="due_date"
                                type="date"
                                value={formData.due_date}
                                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                                data-testid="task-due-date"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="priority">Priority</Label>
                            <Select
                                value={formData.priority}
                                onValueChange={(value) => setFormData({ ...formData, priority: value })}
                            >
                                <SelectTrigger data-testid="task-priority-select">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {Object.entries(priorityConfig).map(([key, config]) => (
                                        <SelectItem key={key} value={key}>
                                            <span className={config.color}>{config.label}</span>
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="category">Category</Label>
                            <Select
                                value={formData.category}
                                onValueChange={(value) => setFormData({ ...formData, category: value })}
                            >
                                <SelectTrigger data-testid="task-category-select">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {Object.entries(categoryLabels).map(([key, label]) => (
                                        <SelectItem key={key} value={key}>{label}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        {properties.length > 0 && (
                            <div className="space-y-2">
                                <Label htmlFor="property_id">Property</Label>
                                <Select
                                    value={formData.property_id || "none"}
                                    onValueChange={(value) => setFormData({ ...formData, property_id: value === "none" ? "" : value })}
                                >
                                    <SelectTrigger data-testid="task-property-select">
                                        <SelectValue placeholder="Select property" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="none">No property</SelectItem>
                                        {properties.map((prop) => (
                                            <SelectItem key={prop.id} value={prop.id}>{prop.name}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        )}
                    </div>

                    <div className="space-y-3 pt-2">
                        <div className="flex items-center space-x-2">
                            <Checkbox
                                id="is_recurring"
                                checked={formData.is_recurring}
                                onCheckedChange={(checked) => setFormData({ ...formData, is_recurring: checked })}
                                data-testid="task-recurring-checkbox"
                            />
                            <Label htmlFor="is_recurring" className="text-sm font-normal cursor-pointer">
                                This is a recurring task
                            </Label>
                        </div>

                        {formData.is_recurring && (
                            <div className="pl-6 space-y-2">
                                <Label htmlFor="recurrence_pattern">Repeat</Label>
                                <Select
                                    value={formData.recurrence_pattern || "monthly"}
                                    onValueChange={(value) => setFormData({ ...formData, recurrence_pattern: value })}
                                >
                                    <SelectTrigger data-testid="task-recurrence-select">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {recurrenceOptions.map((option) => (
                                            <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                                <p className="text-xs text-slate-500">
                                    A new task will be created when you complete this one.
                                </p>
                            </div>
                        )}
                    </div>

                    <DialogFooter className="pt-4">
                        <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
                            Cancel
                        </Button>
                        <Button 
                            type="submit" 
                            className="bg-blue-600 hover:bg-blue-700 text-white"
                            disabled={loading}
                            data-testid="save-task-btn"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Saving...
                                </>
                            ) : (
                                task ? 'Update Task' : 'Create Task'
                            )}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
