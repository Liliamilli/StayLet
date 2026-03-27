import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Checkbox } from '../ui/checkbox';
import { Loader2, AlertCircle, ArrowRight } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PropertyModal({ isOpen, onClose, onSave, property }) {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [constants, setConstants] = useState(null);
    const [limitReached, setLimitReached] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        address: '',
        postcode: '',
        uk_nation: 'England',
        is_in_london: false,
        property_type: 'apartment',
        ownership_type: 'owned',
        bedrooms: 1,
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
        if (property) {
            setFormData({
                name: property.name || '',
                address: property.address || '',
                postcode: property.postcode || '',
                uk_nation: property.uk_nation || 'England',
                is_in_london: property.is_in_london || false,
                property_type: property.property_type || 'apartment',
                ownership_type: property.ownership_type || 'owned',
                bedrooms: property.bedrooms || 1,
                notes: property.notes || ''
            });
        } else {
            setFormData({
                name: '',
                address: '',
                postcode: '',
                uk_nation: 'England',
                is_in_london: false,
                property_type: 'apartment',
                ownership_type: 'owned',
                bedrooms: 1,
                notes: ''
            });
        }
        setErrors({});
    }, [property, isOpen]);

    const validate = () => {
        const newErrors = {};
        if (!formData.name.trim()) newErrors.name = 'Property name is required';
        if (!formData.address.trim()) newErrors.address = 'Address is required';
        if (!formData.postcode.trim()) newErrors.postcode = 'Postcode is required';
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!validate()) return;
        
        setLoading(true);
        try {
            await onSave(formData);
        } catch (error) {
            console.error('Save error:', error);
            // Display backend validation errors
            const errorMsg = error.response?.data?.detail;
            const statusCode = error.response?.status;
            
            if (statusCode === 403 && errorMsg?.includes('limit')) {
                // Plan limit reached
                setLimitReached(true);
                setErrors({ general: errorMsg });
            } else if (errorMsg) {
                if (errorMsg.includes('name')) setErrors(prev => ({ ...prev, name: errorMsg }));
                else if (errorMsg.includes('address')) setErrors(prev => ({ ...prev, address: errorMsg }));
                else if (errorMsg.includes('postcode')) setErrors(prev => ({ ...prev, postcode: errorMsg }));
                else setErrors(prev => ({ ...prev, general: errorMsg }));
            }
        } finally {
            setLoading(false);
        }
    };

    const formatLabel = (str) => {
        return str.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle style={{ fontFamily: 'Outfit, sans-serif' }}>
                        {property ? 'Edit Property' : 'Add Property'}
                    </DialogTitle>
                    <DialogDescription>
                        {property ? 'Update the property details below.' : 'Enter the property details below.'}
                    </DialogDescription>
                </DialogHeader>

                {/* Plan limit error */}
                {limitReached && (
                    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                            <div className="flex-1">
                                <p className="text-sm font-medium text-amber-800">Property limit reached</p>
                                <p className="text-sm text-amber-700 mt-1">{errors.general}</p>
                                <Button
                                    type="button"
                                    size="sm"
                                    className="mt-3 bg-amber-600 hover:bg-amber-700 text-white"
                                    onClick={() => {
                                        onClose();
                                        navigate('/app/billing');
                                    }}
                                >
                                    Upgrade Plan
                                    <ArrowRight className="w-4 h-4 ml-1" />
                                </Button>
                            </div>
                        </div>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4 py-4">
                    <div className="space-y-2">
                        <Label htmlFor="name">Property Name *</Label>
                        <Input
                            id="name"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            placeholder="e.g., Camden Flat 1A"
                            className={errors.name ? 'border-red-500' : ''}
                            data-testid="property-name-input"
                        />
                        {errors.name && <p className="text-xs text-red-500">{errors.name}</p>}
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="address">Address *</Label>
                        <Input
                            id="address"
                            value={formData.address}
                            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                            placeholder="123 High Street"
                            className={errors.address ? 'border-red-500' : ''}
                            data-testid="property-address-input"
                        />
                        {errors.address && <p className="text-xs text-red-500">{errors.address}</p>}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="postcode">Postcode *</Label>
                            <Input
                                id="postcode"
                                value={formData.postcode}
                                onChange={(e) => setFormData({ ...formData, postcode: e.target.value.toUpperCase() })}
                                placeholder="NW1 8AB"
                                className={errors.postcode ? 'border-red-500' : ''}
                                data-testid="property-postcode-input"
                            />
                            {errors.postcode && <p className="text-xs text-red-500">{errors.postcode}</p>}
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="uk_nation">UK Nation</Label>
                            <Select
                                value={formData.uk_nation}
                                onValueChange={(value) => setFormData({ ...formData, uk_nation: value })}
                            >
                                <SelectTrigger data-testid="property-nation-select">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {(constants?.uk_nations || ['England', 'Scotland', 'Wales', 'Northern Ireland']).map((nation) => (
                                        <SelectItem key={nation} value={nation}>{nation}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div className="flex items-center space-x-2">
                        <Checkbox
                            id="is_in_london"
                            checked={formData.is_in_london}
                            onCheckedChange={(checked) => setFormData({ ...formData, is_in_london: checked })}
                            data-testid="property-london-checkbox"
                        />
                        <Label htmlFor="is_in_london" className="text-sm font-normal cursor-pointer">
                            Property is in London
                        </Label>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="property_type">Property Type</Label>
                            <Select
                                value={formData.property_type}
                                onValueChange={(value) => setFormData({ ...formData, property_type: value })}
                            >
                                <SelectTrigger data-testid="property-type-select">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {(constants?.property_types || ['apartment', 'house', 'studio']).map((type) => (
                                        <SelectItem key={type} value={type}>{formatLabel(type)}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="ownership_type">Ownership Type</Label>
                            <Select
                                value={formData.ownership_type}
                                onValueChange={(value) => setFormData({ ...formData, ownership_type: value })}
                            >
                                <SelectTrigger data-testid="property-ownership-select">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    {(constants?.ownership_types || ['owned', 'leased', 'managed_for_owner']).map((type) => (
                                        <SelectItem key={type} value={type}>{formatLabel(type)}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="bedrooms">Bedrooms</Label>
                        <Input
                            id="bedrooms"
                            type="number"
                            min="0"
                            max="20"
                            value={formData.bedrooms}
                            onChange={(e) => setFormData({ ...formData, bedrooms: parseInt(e.target.value) || 0 })}
                            data-testid="property-bedrooms-input"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="notes">Notes</Label>
                        <textarea
                            id="notes"
                            value={formData.notes}
                            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                            placeholder="Any additional notes..."
                            className="flex min-h-[80px] w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            data-testid="property-notes-input"
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
                            data-testid="save-property-btn"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                    Saving...
                                </>
                            ) : (
                                property ? 'Update Property' : 'Add Property'
                            )}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
}
