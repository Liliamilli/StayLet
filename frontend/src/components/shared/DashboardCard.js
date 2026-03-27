import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

export default function DashboardCard({ 
    title, 
    value, 
    icon: Icon, 
    status = 'neutral', // 'success' | 'warning' | 'error' | 'neutral'
    trend,
    trendLabel,
    onClick 
}) {
    const statusStyles = {
        success: {
            bg: 'bg-emerald-50',
            iconBg: 'bg-emerald-100',
            iconColor: 'text-emerald-600',
            valueColor: 'text-emerald-700'
        },
        warning: {
            bg: 'bg-amber-50',
            iconBg: 'bg-amber-100',
            iconColor: 'text-amber-600',
            valueColor: 'text-amber-700'
        },
        error: {
            bg: 'bg-red-50',
            iconBg: 'bg-red-100',
            iconColor: 'text-red-600',
            valueColor: 'text-red-700'
        },
        neutral: {
            bg: 'bg-white',
            iconBg: 'bg-slate-100',
            iconColor: 'text-slate-600',
            valueColor: 'text-slate-900'
        }
    };

    const styles = statusStyles[status] || statusStyles.neutral;

    const TrendIcon = trend === 'up' ? ArrowUpRight : trend === 'down' ? ArrowDownRight : Minus;
    const trendColor = trend === 'up' ? 'text-emerald-600' : trend === 'down' ? 'text-red-600' : 'text-slate-400';

    return (
        <div 
            className={`
                ${styles.bg} border border-slate-200 rounded-lg p-5
                ${onClick ? 'cursor-pointer hover:shadow-md hover:border-slate-300 transition-all' : ''}
            `}
            onClick={onClick}
            data-testid={`dashboard-card-${title.toLowerCase().replace(/\s+/g, '-')}`}
        >
            <div className="flex items-start justify-between mb-4">
                <div className={`${styles.iconBg} p-2.5 rounded-lg`}>
                    {Icon && <Icon className={`w-5 h-5 ${styles.iconColor}`} />}
                </div>
                
                {trend && (
                    <div className={`flex items-center gap-1 ${trendColor}`}>
                        <TrendIcon className="w-4 h-4" />
                        {trendLabel && <span className="text-xs font-medium">{trendLabel}</span>}
                    </div>
                )}
            </div>

            <div>
                <p className="text-sm font-medium text-slate-500 mb-1">{title}</p>
                <p className={`text-3xl font-semibold ${styles.valueColor}`} style={{ fontFamily: 'Outfit, sans-serif' }}>
                    {value}
                </p>
            </div>
        </div>
    );
}
