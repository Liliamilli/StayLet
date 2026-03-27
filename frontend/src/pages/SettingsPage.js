import { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Switch } from '../components/ui/switch';
import { 
    Settings, 
    User, 
    Bell, 
    Shield, 
    Lock, 
    Loader2,
    Check,
    Mail,
    Building,
    AlertCircle,
    CheckCircle2,
    Send
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const tabs = [
    { id: 'account', label: 'Account', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'support', label: 'Support', icon: Mail },
];

export default function SettingsPage() {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('account');
    const [preferences, setPreferences] = useState({
        email_reminders: true,
        inapp_reminders: true,
        reminder_lead_days: [90, 60, 30, 7],
        company_name: '',
        weekly_digest: true,
        marketing_emails: false
    });
    const [prefsLoading, setPrefsLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [saveSuccess, setSaveSuccess] = useState(false);
    
    // Security form
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [passwordError, setPasswordError] = useState('');
    const [passwordSuccess, setPasswordSuccess] = useState(false);
    const [changingPassword, setChangingPassword] = useState(false);

    // Contact form
    const [contactSubject, setContactSubject] = useState('');
    const [contactMessage, setContactMessage] = useState('');
    const [contactType, setContactType] = useState('support');
    const [sendingContact, setSendingContact] = useState(false);
    const [contactSuccess, setContactSuccess] = useState(false);

    useEffect(() => {
        fetchPreferences();
    }, []);

    const fetchPreferences = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/user/preferences`);
            setPreferences({
                email_reminders: response.data.email_reminders ?? true,
                inapp_reminders: response.data.inapp_reminders ?? true,
                reminder_lead_days: response.data.reminder_lead_days ?? [90, 60, 30, 7],
                company_name: response.data.company_name ?? '',
                weekly_digest: response.data.weekly_digest ?? true,
                marketing_emails: response.data.marketing_emails ?? false
            });
        } catch (error) {
            console.error('Failed to fetch preferences:', error);
        } finally {
            setPrefsLoading(false);
        }
    };

    const savePreferences = async () => {
        setSaving(true);
        setSaveSuccess(false);
        try {
            await axios.put(`${API_URL}/api/user/preferences`, preferences);
            setSaveSuccess(true);
            setTimeout(() => setSaveSuccess(false), 3000);
        } catch (error) {
            console.error('Failed to save preferences:', error);
        } finally {
            setSaving(false);
        }
    };

    const toggleReminderDay = (day) => {
        const current = preferences.reminder_lead_days || [];
        const updated = current.includes(day)
            ? current.filter(d => d !== day)
            : [...current, day].sort((a, b) => b - a);
        setPreferences({ ...preferences, reminder_lead_days: updated });
    };

    const handlePasswordChange = async () => {
        setPasswordError('');
        setPasswordSuccess(false);
        
        if (newPassword.length < 8) {
            setPasswordError('Password must be at least 8 characters');
            return;
        }
        if (newPassword !== confirmPassword) {
            setPasswordError('Passwords do not match');
            return;
        }
        
        setChangingPassword(true);
        try {
            await axios.post(`${API_URL}/api/auth/change-password`, {
                current_password: currentPassword,
                new_password: newPassword
            });
            setPasswordSuccess(true);
            setCurrentPassword('');
            setNewPassword('');
            setConfirmPassword('');
            setTimeout(() => setPasswordSuccess(false), 3000);
        } catch (error) {
            setPasswordError(error.response?.data?.detail || 'Failed to change password');
        } finally {
            setChangingPassword(false);
        }
    };

    const handleContactSubmit = async () => {
        if (!contactSubject.trim() || !contactMessage.trim()) return;
        
        setSendingContact(true);
        setContactSuccess(false);
        try {
            await axios.post(`${API_URL}/api/contact`, {
                subject: contactSubject,
                message: contactMessage,
                contact_type: contactType
            });
            setContactSuccess(true);
            setContactSubject('');
            setContactMessage('');
        } catch (error) {
            console.error('Failed to send message:', error);
        } finally {
            setSendingContact(false);
        }
    };

    return (
        <div data-testid="settings-page">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2" style={{ fontFamily: 'Outfit, sans-serif' }}>
                    <Settings className="w-6 h-6 text-slate-400" />
                    Settings
                </h1>
                <p className="text-slate-500 mt-1">
                    Manage your account, notifications, and preferences
                </p>
            </div>

            <div className="flex flex-col lg:flex-row gap-6">
                {/* Tabs Navigation */}
                <div className="lg:w-56 flex-shrink-0">
                    <nav className="flex lg:flex-col gap-1 overflow-x-auto lg:overflow-x-visible pb-2 lg:pb-0">
                        {tabs.map((tab) => {
                            const Icon = tab.icon;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`
                                        flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all
                                        ${activeTab === tab.id 
                                            ? 'bg-blue-50 text-blue-700' 
                                            : 'text-slate-600 hover:bg-slate-100'
                                        }
                                    `}
                                    data-testid={`tab-${tab.id}`}
                                >
                                    <Icon className="w-4 h-4" />
                                    {tab.label}
                                </button>
                            );
                        })}
                    </nav>
                </div>

                {/* Tab Content */}
                <div className="flex-1 bg-white rounded-xl border border-slate-200 p-6">
                    {/* Account Tab */}
                    {activeTab === 'account' && (
                        <div className="max-w-lg">
                            <h2 className="text-lg font-semibold text-slate-900 mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                Account Details
                            </h2>
                            <p className="text-sm text-slate-500 mb-6">
                                Your account information and business details
                            </p>
                            
                            <div className="space-y-5">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1.5">
                                        Full Name
                                    </label>
                                    <Input 
                                        value={user?.full_name || ''} 
                                        disabled 
                                        className="bg-slate-50"
                                        data-testid="account-name"
                                    />
                                </div>
                                
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1.5">
                                        Email Address
                                    </label>
                                    <Input 
                                        value={user?.email || ''} 
                                        disabled 
                                        className="bg-slate-50"
                                        data-testid="account-email"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1.5">
                                        <div className="flex items-center gap-2">
                                            <Building className="w-4 h-4 text-slate-400" />
                                            Company Name
                                        </div>
                                    </label>
                                    <Input 
                                        value={preferences.company_name || ''} 
                                        onChange={(e) => setPreferences({ ...preferences, company_name: e.target.value })}
                                        placeholder="Your company or business name"
                                        data-testid="company-name"
                                    />
                                    <p className="text-xs text-slate-500 mt-1">
                                        This will appear on exported compliance reports
                                    </p>
                                </div>

                                <div className="pt-4">
                                    <Button 
                                        onClick={savePreferences}
                                        disabled={saving}
                                        className="bg-blue-600 hover:bg-blue-700 text-white"
                                        data-testid="save-account-btn"
                                    >
                                        {saving ? (
                                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        ) : saveSuccess ? (
                                            <Check className="w-4 h-4 mr-2" />
                                        ) : null}
                                        {saveSuccess ? 'Saved' : 'Save Changes'}
                                    </Button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Notifications Tab */}
                    {activeTab === 'notifications' && (
                        <div className="max-w-lg">
                            <h2 className="text-lg font-semibold text-slate-900 mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                Notification Preferences
                            </h2>
                            <p className="text-sm text-slate-500 mb-6">
                                Configure how and when you receive notifications
                            </p>
                            
                            {prefsLoading ? (
                                <div className="flex items-center justify-center py-8">
                                    <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
                                </div>
                            ) : (
                                <div className="space-y-6">
                                    {/* Notification toggles */}
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between py-3 border-b border-slate-100">
                                            <div>
                                                <p className="font-medium text-slate-900">In-app notifications</p>
                                                <p className="text-sm text-slate-500">Show alerts in the notification bell</p>
                                            </div>
                                            <Switch
                                                checked={preferences.inapp_reminders}
                                                onCheckedChange={(checked) => setPreferences({ ...preferences, inapp_reminders: checked })}
                                                data-testid="toggle-inapp"
                                            />
                                        </div>
                                        
                                        <div className="flex items-center justify-between py-3 border-b border-slate-100">
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <p className="font-medium text-slate-900">Email reminders</p>
                                                    <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-700 rounded">Coming soon</span>
                                                </div>
                                                <p className="text-sm text-slate-500">Receive email alerts before documents expire</p>
                                            </div>
                                            <Switch
                                                checked={preferences.email_reminders}
                                                onCheckedChange={(checked) => setPreferences({ ...preferences, email_reminders: checked })}
                                                data-testid="toggle-email"
                                            />
                                        </div>

                                        <div className="flex items-center justify-between py-3 border-b border-slate-100">
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <p className="font-medium text-slate-900">Weekly digest</p>
                                                    <span className="text-xs px-2 py-0.5 bg-amber-100 text-amber-700 rounded">Coming soon</span>
                                                </div>
                                                <p className="text-sm text-slate-500">Weekly summary of compliance status sent on Mondays</p>
                                            </div>
                                            <Switch
                                                checked={preferences.weekly_digest}
                                                onCheckedChange={(checked) => setPreferences({ ...preferences, weekly_digest: checked })}
                                                data-testid="toggle-digest"
                                            />
                                        </div>

                                        <div className="flex items-center justify-between py-3 border-b border-slate-100">
                                            <div>
                                                <p className="font-medium text-slate-900">Marketing emails</p>
                                                <p className="text-sm text-slate-500">Product updates and feature announcements</p>
                                            </div>
                                            <Switch
                                                checked={preferences.marketing_emails}
                                                onCheckedChange={(checked) => setPreferences({ ...preferences, marketing_emails: checked })}
                                                data-testid="toggle-marketing"
                                            />
                                        </div>
                                    </div>

                                    {/* Reminder lead times */}
                                    <div className="space-y-3">
                                        <div>
                                            <p className="font-medium text-slate-900 mb-1">Reminder timing</p>
                                            <p className="text-sm text-slate-500">Days before expiry to remind you</p>
                                        </div>
                                        
                                        <div className="flex flex-wrap gap-2">
                                            {[90, 60, 30, 14, 7, 3, 1].map((day) => (
                                                <button
                                                    key={day}
                                                    onClick={() => toggleReminderDay(day)}
                                                    className={`
                                                        px-4 py-2 rounded-lg text-sm font-medium transition-all
                                                        ${(preferences.reminder_lead_days || []).includes(day)
                                                            ? 'bg-blue-100 text-blue-700 border-2 border-blue-300'
                                                            : 'bg-slate-100 text-slate-600 border-2 border-transparent hover:border-slate-300'
                                                        }
                                                    `}
                                                    data-testid={`reminder-day-${day}`}
                                                >
                                                    {day} {day === 1 ? 'day' : 'days'}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <div className="pt-4">
                                        <Button 
                                            onClick={savePreferences}
                                            disabled={saving}
                                            className="bg-blue-600 hover:bg-blue-700 text-white"
                                            data-testid="save-notifications-btn"
                                        >
                                            {saving ? (
                                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                            ) : saveSuccess ? (
                                                <Check className="w-4 h-4 mr-2" />
                                            ) : null}
                                            {saveSuccess ? 'Saved' : 'Save Preferences'}
                                        </Button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* Security Tab */}
                    {activeTab === 'security' && (
                        <div className="max-w-lg">
                            <h2 className="text-lg font-semibold text-slate-900 mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                Security Settings
                            </h2>
                            <p className="text-sm text-slate-500 mb-6">
                                Update your password and security preferences
                            </p>
                            
                            <div className="space-y-5">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1.5">
                                        Current Password
                                    </label>
                                    <Input 
                                        type="password"
                                        value={currentPassword}
                                        onChange={(e) => setCurrentPassword(e.target.value)}
                                        placeholder="Enter current password"
                                        data-testid="current-password"
                                    />
                                </div>
                                
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1.5">
                                        New Password
                                    </label>
                                    <Input 
                                        type="password"
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                        placeholder="Enter new password"
                                        data-testid="new-password"
                                    />
                                </div>
                                
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-1.5">
                                        Confirm New Password
                                    </label>
                                    <Input 
                                        type="password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        placeholder="Confirm new password"
                                        data-testid="confirm-password"
                                    />
                                </div>

                                {passwordError && (
                                    <div className="flex items-center gap-2 text-red-600 text-sm">
                                        <AlertCircle className="w-4 h-4" />
                                        {passwordError}
                                    </div>
                                )}

                                {passwordSuccess && (
                                    <div className="flex items-center gap-2 text-emerald-600 text-sm">
                                        <CheckCircle2 className="w-4 h-4" />
                                        Password changed successfully
                                    </div>
                                )}

                                <div className="pt-4">
                                    <Button 
                                        onClick={handlePasswordChange}
                                        disabled={changingPassword || !currentPassword || !newPassword || !confirmPassword}
                                        className="bg-blue-600 hover:bg-blue-700 text-white"
                                        data-testid="change-password-btn"
                                    >
                                        {changingPassword && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                                        Change Password
                                    </Button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Support Tab */}
                    {activeTab === 'support' && (
                        <div className="max-w-lg">
                            <h2 className="text-lg font-semibold text-slate-900 mb-1" style={{ fontFamily: 'Outfit, sans-serif' }}>
                                Contact Support
                            </h2>
                            <p className="text-sm text-slate-500 mb-6">
                                Send us a message and we'll get back to you within 24 hours
                            </p>

                            {contactSuccess ? (
                                <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6 text-center">
                                    <CheckCircle2 className="w-12 h-12 text-emerald-600 mx-auto mb-4" />
                                    <h3 className="text-lg font-semibold text-emerald-900 mb-2">Message Sent!</h3>
                                    <p className="text-emerald-700">
                                        Thank you for contacting us. We'll get back to you within 24 hours.
                                    </p>
                                    <Button 
                                        variant="outline" 
                                        onClick={() => setContactSuccess(false)}
                                        className="mt-4"
                                    >
                                        Send Another Message
                                    </Button>
                                </div>
                            ) : (
                                <div className="space-y-5">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1.5">
                                            What can we help with?
                                        </label>
                                        <div className="flex gap-2">
                                            {[
                                                { id: 'support', label: 'Support' },
                                                { id: 'billing', label: 'Billing' },
                                                { id: 'feedback', label: 'Feedback' }
                                            ].map((type) => (
                                                <button
                                                    key={type.id}
                                                    onClick={() => setContactType(type.id)}
                                                    className={`
                                                        px-4 py-2 rounded-lg text-sm font-medium transition-all
                                                        ${contactType === type.id
                                                            ? 'bg-blue-100 text-blue-700 border-2 border-blue-300'
                                                            : 'bg-slate-100 text-slate-600 border-2 border-transparent hover:border-slate-300'
                                                        }
                                                    `}
                                                >
                                                    {type.label}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1.5">
                                            Subject
                                        </label>
                                        <Input 
                                            value={contactSubject}
                                            onChange={(e) => setContactSubject(e.target.value)}
                                            placeholder="Brief description of your question"
                                            data-testid="contact-subject"
                                        />
                                    </div>
                                    
                                    <div>
                                        <label className="block text-sm font-medium text-slate-700 mb-1.5">
                                            Message
                                        </label>
                                        <textarea 
                                            value={contactMessage}
                                            onChange={(e) => setContactMessage(e.target.value)}
                                            placeholder="Please describe your question or issue in detail..."
                                            className="w-full h-32 px-3 py-2 border border-slate-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                            data-testid="contact-message"
                                        />
                                    </div>

                                    <div className="pt-4">
                                        <Button 
                                            onClick={handleContactSubmit}
                                            disabled={sendingContact || !contactSubject.trim() || !contactMessage.trim()}
                                            className="bg-blue-600 hover:bg-blue-700 text-white"
                                            data-testid="send-contact-btn"
                                        >
                                            {sendingContact ? (
                                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                            ) : (
                                                <Send className="w-4 h-4 mr-2" />
                                            )}
                                            Send Message
                                        </Button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
