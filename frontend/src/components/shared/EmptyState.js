import { Button } from '../ui/button';

export default function EmptyState({ 
    icon: Icon, 
    title, 
    description, 
    actionLabel, 
    onAction,
    secondaryActionLabel,
    onSecondaryAction 
}) {
    return (
        <div 
            className="flex flex-col items-center justify-center py-16 px-4 text-center"
            data-testid="empty-state"
        >
            {Icon && (
                <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mb-6">
                    <Icon className="w-8 h-8 text-slate-400" />
                </div>
            )}
            
            <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                {title}
            </h3>
            
            <p className="text-sm text-slate-500 max-w-sm mb-6">
                {description}
            </p>
            
            <div className="flex items-center gap-3">
                {actionLabel && onAction && (
                    <Button 
                        onClick={onAction}
                        className="bg-blue-600 hover:bg-blue-700 text-white"
                        data-testid="empty-state-action"
                    >
                        {actionLabel}
                    </Button>
                )}
                
                {secondaryActionLabel && onSecondaryAction && (
                    <Button 
                        variant="outline"
                        onClick={onSecondaryAction}
                        data-testid="empty-state-secondary"
                    >
                        {secondaryActionLabel}
                    </Button>
                )}
            </div>
        </div>
    );
}
