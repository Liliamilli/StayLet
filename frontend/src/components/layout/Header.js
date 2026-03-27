import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import NotificationDropdown from '../notifications/NotificationDropdown';
import { 
    Menu, 
    ChevronDown, 
    User, 
    Settings, 
    LogOut,
    HelpCircle
} from 'lucide-react';

export default function Header({ onMenuClick }) {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const dropdownRef = useRef(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setDropdownOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    const getInitials = (name) => {
        if (!name) return 'U';
        return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    };

    return (
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-4 lg:px-6">
            {/* Left side */}
            <div className="flex items-center gap-4">
                <button 
                    onClick={onMenuClick}
                    className="lg:hidden p-2 hover:bg-slate-100 rounded-lg transition-colors"
                    data-testid="mobile-menu-btn"
                >
                    <Menu className="w-5 h-5 text-slate-600" />
                </button>
            </div>

            {/* Right side */}
            <div className="flex items-center gap-2">
                {/* Help */}
                <button 
                    className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                    data-testid="help-btn"
                >
                    <HelpCircle className="w-5 h-5 text-slate-500" />
                </button>

                {/* Notifications */}
                <NotificationDropdown />

                {/* User dropdown */}
                <div className="relative ml-2" ref={dropdownRef}>
                    <button 
                        onClick={() => setDropdownOpen(!dropdownOpen)}
                        className="flex items-center gap-2 p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
                        data-testid="user-menu-btn"
                    >
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <span className="text-sm font-medium text-blue-700">
                                {getInitials(user?.full_name)}
                            </span>
                        </div>
                        <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
                    </button>

                    {/* Dropdown menu */}
                    {dropdownOpen && (
                        <div 
                            className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-50"
                            data-testid="user-dropdown"
                        >
                            <div className="px-4 py-3 border-b border-slate-100">
                                <p className="text-sm font-medium text-slate-900">{user?.full_name}</p>
                                <p className="text-xs text-slate-500 truncate">{user?.email}</p>
                            </div>
                            
                            <div className="py-1">
                                <button 
                                    onClick={() => { navigate('/app/settings'); setDropdownOpen(false); }}
                                    className="w-full flex items-center gap-3 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
                                    data-testid="dropdown-profile"
                                >
                                    <User className="w-4 h-4 text-slate-400" />
                                    Profile
                                </button>
                                <button 
                                    onClick={() => { navigate('/app/settings'); setDropdownOpen(false); }}
                                    className="w-full flex items-center gap-3 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 transition-colors"
                                    data-testid="dropdown-settings"
                                >
                                    <Settings className="w-4 h-4 text-slate-400" />
                                    Settings
                                </button>
                            </div>
                            
                            <div className="border-t border-slate-100 py-1">
                                <button 
                                    onClick={handleLogout}
                                    className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                                    data-testid="logout-btn"
                                >
                                    <LogOut className="w-4 h-4" />
                                    Sign out
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}
