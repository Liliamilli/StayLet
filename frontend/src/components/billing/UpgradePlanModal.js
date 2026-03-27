import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Button } from '../ui/button';
import { 
    AlertTriangle, 
    ArrowRight, 
    Building2,
    Check,
    Sparkles
} from 'lucide-react';

const PLANS = {
    solo: { name: 'Solo', price: 19, limit: 1 },
    portfolio: { name: 'Portfolio', price: 39, limit: 5 },
    operator: { name: 'Operator', price: 79, limit: 15 }
};

export default function UpgradePlanModal({ isOpen, onClose, currentPlan, propertyCount, limitMessage }) {
    const navigate = useNavigate();
    const currentPlanInfo = PLANS[currentPlan] || PLANS.solo;
    
    // Determine next plan
    const planOrder = ['solo', 'portfolio', 'operator'];
    const currentIdx = planOrder.indexOf(currentPlan);
    const nextPlan = currentIdx < planOrder.length - 1 ? planOrder[currentIdx + 1] : null;
    const nextPlanInfo = nextPlan ? PLANS[nextPlan] : null;

    const handleUpgrade = () => {
        onClose();
        navigate('/app/billing');
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-md">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        <AlertTriangle className="w-5 h-5 text-amber-500" />
                        Property Limit Reached
                    </DialogTitle>
                    <DialogDescription>
                        You've reached the maximum properties for your current plan.
                    </DialogDescription>
                </DialogHeader>

                <div className="py-4 space-y-4">
                    {/* Current status */}
                    <div className="bg-slate-50 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-sm text-slate-600">Current Plan</span>
                            <span className="font-semibold text-slate-900">{currentPlanInfo.name}</span>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-slate-600">Properties</span>
                            <span className="font-semibold text-slate-900">
                                <Building2 className="w-4 h-4 inline mr-1" />
                                {propertyCount} / {currentPlanInfo.limit}
                            </span>
                        </div>
                    </div>

                    {limitMessage && (
                        <p className="text-sm text-slate-600 text-center">
                            {limitMessage}
                        </p>
                    )}

                    {/* Upgrade option */}
                    {nextPlanInfo && (
                        <div className="border-2 border-blue-200 bg-blue-50 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-3">
                                <Sparkles className="w-5 h-5 text-blue-600" />
                                <span className="font-semibold text-blue-900">Upgrade to {nextPlanInfo.name}</span>
                            </div>
                            <ul className="space-y-2 mb-4">
                                <li className="flex items-center gap-2 text-sm text-blue-800">
                                    <Check className="w-4 h-4 text-blue-600" />
                                    Up to {nextPlanInfo.limit} properties
                                </li>
                                <li className="flex items-center gap-2 text-sm text-blue-800">
                                    <Check className="w-4 h-4 text-blue-600" />
                                    All {currentPlanInfo.name} features included
                                </li>
                                <li className="flex items-center gap-2 text-sm text-blue-800">
                                    <Check className="w-4 h-4 text-blue-600" />
                                    Priority support
                                </li>
                            </ul>
                            <div className="flex items-center justify-between">
                                <div>
                                    <span className="text-2xl font-bold text-blue-900">£{nextPlanInfo.price}</span>
                                    <span className="text-sm text-blue-700">/month</span>
                                </div>
                                <Button 
                                    onClick={handleUpgrade}
                                    className="bg-blue-600 hover:bg-blue-700 text-white"
                                >
                                    Upgrade Now
                                    <ArrowRight className="w-4 h-4 ml-2" />
                                </Button>
                            </div>
                        </div>
                    )}

                    {!nextPlanInfo && (
                        <div className="text-center p-4 bg-slate-50 rounded-lg">
                            <p className="text-sm text-slate-600 mb-2">
                                You're on our largest standard plan.
                            </p>
                            <p className="text-sm text-slate-500">
                                Need more properties? Contact us for enterprise options.
                            </p>
                        </div>
                    )}
                </div>

                <div className="flex justify-end gap-3 pt-2 border-t border-slate-200">
                    <Button variant="outline" onClick={onClose}>
                        Maybe Later
                    </Button>
                    <Button 
                        onClick={handleUpgrade}
                        variant="ghost"
                        className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                    >
                        View All Plans
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}
