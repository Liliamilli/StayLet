import { NavLink, useLocation } from 'react-router-dom';
import { 
    LayoutDashboard, 
    Building2, 
    ClipboardCheck, 
    ListTodo, 
    CreditCard, 
    Settings,
    ChevronLeft,
    Shield,
    HelpCircle
} from 'lucide-react';

const navigation = [
    { name: 'Dashboard', href: '/app', icon: LayoutDashboard },
    { name: 'Properties', href: '/app/properties', icon: Building2 },
    { name: 'Compliance', href: '/app/compliance', icon: ClipboardCheck },
    { name: 'Tasks', href: '/app/tasks', icon: ListTodo },
    { name: 'Billing', href: '/app/billing', icon: CreditCard },
    { name: 'Settings', href: '/app/settings', icon: Settings },
    { name: 'Help', href: '/app/help', icon: HelpCircle },
];

export default function Sidebar({ isOpen, onClose }) {
    const location = useLocation();

    const isActive = (href) => {
        if (href === '/app') {
            return location.pathname === '/app';
        }
        return location.pathname.startsWith(href);
    };

    return (
        <>
            {/* Mobile overlay */}
            {isOpen && (
                <div 
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
                    onClick={onClose}
                    data-testid="sidebar-overlay"
                />
            )}
            
            {/* Sidebar */}
            <aside 
                className={`
                    fixed top-0 left-0 z-50 h-full w-64 bg-white border-r border-slate-200
                    transform transition-transform duration-200 ease-in-out
                    lg:translate-x-0 lg:static lg:z-auto
                    ${isOpen ? 'translate-x-0' : '-translate-x-full'}
                `}
                data-testid="sidebar"
            >
                {/* Logo */}
                <div className="h-16 flex items-center justify-between px-4 border-b border-slate-200">
                    <NavLink to="/app" className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                            <Shield className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-lg font-semibold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                            Staylet
                        </span>
                    </NavLink>
                    <button 
                        onClick={onClose}
                        className="lg:hidden p-2 hover:bg-slate-100 rounded-lg transition-colors"
                        data-testid="close-sidebar-btn"
                    >
                        <ChevronLeft className="w-5 h-5 text-slate-500" />
                    </button>
                </div>

                {/* Navigation */}
                <nav className="p-4 space-y-1 pb-32">
                    {navigation.map((item) => {
                        const Icon = item.icon;
                        const active = isActive(item.href);
                        
                        return (
                            <NavLink
                                key={item.name}
                                to={item.href}
                                onClick={onClose}
                                className={`
                                    flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                                    transition-colors
                                    ${active 
                                        ? 'bg-blue-50 text-blue-700' 
                                        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                                    }
                                `}
                                data-testid={`nav-${item.name.toLowerCase()}`}
                            >
                                <Icon className={`w-5 h-5 ${active ? 'text-blue-600' : 'text-slate-400'}`} />
                                {item.name}
                            </NavLink>
                        );
                    })}
                </nav>

                {/* Bottom section */}
                <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-200">
                    <div className="bg-slate-50 rounded-lg p-4">
                        <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">
                            Current Plan
                        </p>
                        <p className="text-sm font-semibold text-slate-900 mb-2">Free Trial</p>
                        <NavLink 
                            to="/app/billing"
                            className="text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors"
                            data-testid="upgrade-link"
                        >
                            Upgrade Plan →
                        </NavLink>
                    </div>
                </div>
            </aside>
        </>
    );
}
