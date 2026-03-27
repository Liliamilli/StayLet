import { Button } from '../ui/button';
import { ArrowRight, Lightbulb } from 'lucide-react';

export default function EmptyState({ 
    icon: Icon, 
    title, 
    description, 
    actionLabel, 
    onAction,
    secondaryActionLabel,
    onSecondaryAction,
    tip,
    variant = 'default' // default, minimal, featured
}) {
    if (variant === 'featured') {
        return (
            <div 
                className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100 p-8"
                data-testid="empty-state"
            >
                {/* Background decoration */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-blue-100/50 rounded-full -translate-y-1/2 translate-x-1/2" />
                <div className="absolute bottom-0 left-0 w-32 h-32 bg-indigo-100/50 rounded-full translate-y-1/2 -translate-x-1/2" />
                
                <div className="relative flex flex-col items-center text-center max-w-md mx-auto">
                    {Icon && (
                        <div className="w-20 h-20 bg-white rounded-2xl shadow-lg flex items-center justify-center mb-6 border border-blue-100">
                            <Icon className="w-10 h-10 text-blue-600" />
                        </div>
                    )}
                    
                    <h3 className="text-2xl font-bold text-slate-900 mb-3" style={{ fontFamily: 'Outfit, sans-serif' }}>
                        {title}
                    </h3>
                    
                    <p className="text-slate-600 mb-6 leading-relaxed">
                        {description}
                    </p>
                    
                    <div className="flex flex-col sm:flex-row items-center gap-3">
                        {actionLabel && onAction && (
                            <Button 
                                onClick={onAction}
                                className="bg-blue-600 hover:bg-blue-700 text-white px-6"
                                size="lg"
                                data-testid="empty-state-action"
                            >
                                {actionLabel}
                                <ArrowRight className="w-4 h-4 ml-2" />
                            </Button>
                        )}
                        
                        {secondaryActionLabel && onSecondaryAction && (
                            <Button 
                                variant="outline"
                                onClick={onSecondaryAction}
                                size="lg"
                                data-testid="empty-state-secondary"
                            >
                                {secondaryActionLabel}
                            </Button>
                        )}
                    </div>
                    
                    {tip && (
                        <div className="mt-6 flex items-start gap-2 text-left bg-white/80 rounded-lg p-3 border border-blue-100">
                            <Lightbulb className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                            <p className="text-sm text-slate-600">{tip}</p>
                        </div>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div 
            className={`flex flex-col items-center justify-center text-center ${variant === 'minimal' ? 'py-8' : 'py-16 px-4'}`}
            data-testid="empty-state"
        >
            {Icon && (
                <div className={`${variant === 'minimal' ? 'w-12 h-12 mb-4' : 'w-16 h-16 mb-6'} bg-slate-100 rounded-full flex items-center justify-center`}>
                    <Icon className={`${variant === 'minimal' ? 'w-6 h-6' : 'w-8 h-8'} text-slate-400`} />
                </div>
            )}
            
            <h3 className={`${variant === 'minimal' ? 'text-base' : 'text-lg'} font-semibold text-slate-900 mb-2`} style={{ fontFamily: 'Outfit, sans-serif' }}>
                {title}
            </h3>
            
            <p className={`text-sm text-slate-500 ${variant === 'minimal' ? 'max-w-xs mb-4' : 'max-w-sm mb-6'}`}>
                {description}
            </p>
            
            <div className="flex items-center gap-3">
                {actionLabel && onAction && (
                    <Button 
                        onClick={onAction}
                        className="bg-blue-600 hover:bg-blue-700 text-white"
                        size={variant === 'minimal' ? 'sm' : 'default'}
                        data-testid="empty-state-action"
                    >
                        {actionLabel}
                    </Button>
                )}
                
                {secondaryActionLabel && onSecondaryAction && (
                    <Button 
                        variant="outline"
                        onClick={onSecondaryAction}
                        size={variant === 'minimal' ? 'sm' : 'default'}
                        data-testid="empty-state-secondary"
                    >
                        {secondaryActionLabel}
                    </Button>
                )}
            </div>
            
            {tip && (
                <div className="mt-4 flex items-start gap-2 text-left max-w-sm">
                    <Lightbulb className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                    <p className="text-xs text-slate-500">{tip}</p>
                </div>
            )}
        </div>
    );
}

