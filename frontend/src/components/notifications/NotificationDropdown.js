import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
    Bell, 
    X, 
    Clock, 
    AlertCircle, 
    CheckCircle2, 
    FileX,
    ListTodo,
    ChevronRight
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const notificationIcons = {
    expiry_reminder: Clock,
    overdue_alert: AlertCircle,
    task_due: ListTodo,
    missing_record: FileX,
    system: CheckCircle2
};

const notificationColors = {
    expiry_reminder: { bg: 'bg-amber-50', icon: 'text-amber-600', border: 'border-amber-100' },
    overdue_alert: { bg: 'bg-red-50', icon: 'text-red-600', border: 'border-red-100' },
    task_due: { bg: 'bg-blue-50', icon: 'text-blue-600', border: 'border-blue-100' },
    missing_record: { bg: 'bg-slate-50', icon: 'text-slate-600', border: 'border-slate-200' },
    system: { bg: 'bg-emerald-50', icon: 'text-emerald-600', border: 'border-emerald-100' }
};

export default function NotificationDropdown() {
    const navigate = useNavigate();
    const [isOpen, setIsOpen] = useState(false);
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [loading, setLoading] = useState(false);
    const dropdownRef = useRef(null);

    useEffect(() => {
        fetchNotifications();
        // Generate notifications on component mount
        generateNotifications();
    }, []);

    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const generateNotifications = async () => {
        try {
            await axios.get(`${API_URL}/api/notifications/generate`);
            fetchNotifications();
        } catch (error) {
            console.error('Failed to generate notifications:', error);
        }
    };

    const fetchNotifications = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/notifications`);
            setNotifications(response.data);
            setUnreadCount(response.data.filter(n => !n.is_read).length);
        } catch (error) {
            console.error('Failed to fetch notifications:', error);
        }
    };

    const markAsRead = async (notificationId) => {
        try {
            await axios.put(`${API_URL}/api/notifications/${notificationId}/read`);
            setNotifications(notifications.map(n => 
                n.id === notificationId ? { ...n, is_read: true } : n
            ));
            setUnreadCount(prev => Math.max(0, prev - 1));
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
        }
    };

    const markAllAsRead = async () => {
        try {
            await axios.put(`${API_URL}/api/notifications/read-all`);
            setNotifications(notifications.map(n => ({ ...n, is_read: true })));
            setUnreadCount(0);
        } catch (error) {
            console.error('Failed to mark all notifications as read:', error);
        }
    };

    const deleteNotification = async (e, notificationId) => {
        e.stopPropagation();
        try {
            await axios.delete(`${API_URL}/api/notifications/${notificationId}`);
            const notification = notifications.find(n => n.id === notificationId);
            setNotifications(notifications.filter(n => n.id !== notificationId));
            if (!notification?.is_read) {
                setUnreadCount(prev => Math.max(0, prev - 1));
            }
        } catch (error) {
            console.error('Failed to delete notification:', error);
        }
    };

    const handleNotificationClick = (notification) => {
        markAsRead(notification.id);
        
        if (notification.reference_type === 'compliance_record') {
            // Navigate to compliance page or property detail
            navigate('/app/compliance');
        } else if (notification.reference_type === 'task') {
            navigate('/app/tasks');
        }
        
        setIsOpen(false);
    };

    const formatTime = (dateStr) => {
        const date = new Date(dateStr);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <button 
                onClick={() => setIsOpen(!isOpen)}
                className="p-2 hover:bg-slate-100 rounded-lg transition-colors relative"
                data-testid="notifications-btn"
            >
                <Bell className="w-5 h-5 text-slate-500" />
                {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 min-w-[18px] h-[18px] px-1 flex items-center justify-center bg-red-500 text-white text-xs font-medium rounded-full">
                        {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                )}
            </button>

            {isOpen && (
                <div 
                    className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-lg shadow-lg border border-slate-200 z-50 overflow-hidden"
                    data-testid="notifications-dropdown"
                >
                    {/* Header */}
                    <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-slate-50">
                        <h3 className="font-semibold text-slate-900" style={{ fontFamily: 'Outfit, sans-serif' }}>
                            Notifications
                        </h3>
                        {unreadCount > 0 && (
                            <button
                                onClick={markAllAsRead}
                                className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                            >
                                Mark all read
                            </button>
                        )}
                    </div>

                    {/* Notifications list */}
                    <div className="max-h-[400px] overflow-y-auto">
                        {notifications.length === 0 ? (
                            <div className="py-12 text-center">
                                <Bell className="w-10 h-10 text-slate-300 mx-auto mb-3" />
                                <p className="text-sm text-slate-500">No notifications yet</p>
                                <p className="text-xs text-slate-400 mt-1">We'll notify you about important updates</p>
                            </div>
                        ) : (
                            <div className="divide-y divide-slate-100">
                                {notifications.map((notification) => {
                                    const Icon = notificationIcons[notification.notification_type] || Bell;
                                    const colors = notificationColors[notification.notification_type] || notificationColors.system;
                                    
                                    return (
                                        <div
                                            key={notification.id}
                                            onClick={() => handleNotificationClick(notification)}
                                            className={`
                                                flex items-start gap-3 px-4 py-3 cursor-pointer transition-colors group
                                                ${notification.is_read ? 'bg-white' : 'bg-blue-50/30'}
                                                hover:bg-slate-50
                                            `}
                                            data-testid={`notification-${notification.id}`}
                                        >
                                            <div className={`p-2 rounded-lg ${colors.bg} flex-shrink-0`}>
                                                <Icon className={`w-4 h-4 ${colors.icon}`} />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-start justify-between gap-2">
                                                    <p className={`text-sm ${notification.is_read ? 'text-slate-700' : 'text-slate-900 font-medium'}`}>
                                                        {notification.title}
                                                    </p>
                                                    <button
                                                        onClick={(e) => deleteNotification(e, notification.id)}
                                                        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-200 rounded transition-all"
                                                    >
                                                        <X className="w-3 h-3 text-slate-400" />
                                                    </button>
                                                </div>
                                                <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">
                                                    {notification.message}
                                                </p>
                                                <p className="text-xs text-slate-400 mt-1">
                                                    {formatTime(notification.created_at)}
                                                </p>
                                            </div>
                                            {!notification.is_read && (
                                                <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-2" />
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    {notifications.length > 0 && (
                        <div className="px-4 py-3 border-t border-slate-100 bg-slate-50">
                            <button
                                onClick={() => { navigate('/app/settings'); setIsOpen(false); }}
                                className="flex items-center justify-center gap-1 w-full text-sm text-slate-600 hover:text-slate-900 transition-colors"
                            >
                                Notification settings
                                <ChevronRight className="w-4 h-4" />
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
