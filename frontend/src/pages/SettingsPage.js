import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { 
    User, 
    Bell, 
    Shield, 
    Loader2,
    CheckCircle2,
    Info
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function SettingsPage() {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('profile');
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);
    
    // Notification preferences state
    const [preferences, setPreferences] = useState({
        email_reminders: true,
        inapp_reminders: true,
        reminder_lead_days: [90, 60, 30, 7]
    });
    const [prefsLoading, setPrefsLoading] = useState(true);

    useEffect(() => {
        if (activeTab === 'notifications') {
            fetchPreferences();
        }
    }, [activeTab]);

    const fetchPreferences = async () => {
        setPrefsLoading(true);
        try {
            const response = await axios.get(`${API_URL}/api/user/preferences`);
            setPreferences(response.data);
        } catch (error) {
            console.error('Failed to fetch preferences:', error);
        } finally {
            setPrefsLoading(false);
        }
    };

    const savePreferences = async () => {
        setSaving(true);
        try {
            await axios.put(`${API_URL}/api/user/preferences`, preferences);
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        } catch (error) {
            console.error('Failed to save preferences:', error);
        } finally {
            setSaving(false);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        // Simulate save
        await new Promise(resolve => setTimeout(resolve, 1000));
        setSaving(false);
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
    };

    const toggleReminderDay = (day) => {
        setPreferences(prev => {
            const days = prev.reminder_lead_days || [];
            if (days.includes(day)) {
                return { ...prev, reminder_lead_days: days.filter(d => d !== day) };
            } else {
                return { ...prev, reminder_lead_days: [...days, day].sort((a, b) => b - a) };
            }
        });
    };

    const tabs = [
        { id: 'profile', label: 'Profile', icon: User },
        { id: 'notifications', label: 'Notifications', icon: Bell },
        { id: 'security', label: 'Security', icon: Shield },
    ];

    return (
        <div data-testid="settings-page">
            {/* Page header */}
            <div className="mb-8">
                <h1 
                    className="text-2xl font-bold text-slate-900 mb-1"
                    style={{ fontFamily: 'Outfit, sans-serif' }}
                >
                    Settings
                </h1>
                <p className="text-slate-500">
                    Manage your account settings and preferences
                </p>
            </div>

            <div className="bg-white rounded-lg border border-slate-200">
                {/* Tabs */}
                <div className="border-b border-slate-200">
                    <nav className="flex gap-0">
                        {tabs.map((tab) => {
                            const Icon = tab.icon;
                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`
                                        flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-colors
                                        ${activeTab === tab.id 
                                            ? 'text-blue-600 border-blue-600' 
                                            : 'text-slate-500 border-transparent hover:text-slate-700 hover:border-slate-300'
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

                {/* Tab content */}
                <div className="p-6">
                    {activeTab === 'profile' && (
                        <div className="max-w-lg space-y-6">
                            <div className="space-y-2">
                                <Label htmlFor="fullName">Full name</Label>
                                <Input
                                    id="fullName"
                                    defaultValue={user?.full_name || ''}
                                    className="h-11"
                                    data-testid="settings-name"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="email">Email address</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    defaultValue={user?.email || ''}
                                    className="h-11"
                                    disabled
                                    data-testid="settings-email"
                                />
                                <p className="text-xs text-slate-500">
                                    Contact support to change your email address
                                </p>
                            </div>

                            <div className="pt-4">
                                <Button 
                                    onClick={handleSave}
                                    disabled={saving}
                                    className="bg-blue-600 hover:bg-blue-700 text-white"
                                    data-testid="save-profile"
                                >
                                    {saving ? (
                                        <>
                                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                            Saving...
                                        </>
                                    ) : saved ? (
                                        <>
                                            <CheckCircle2 className="w-4 h-4 mr-2" />
                                            Saved
                                        </>
                                    ) : (
                                        'Save Changes'
                                    )}
                                </Button>
                            </div>
                        </div>
                    )}

                    {activeTab === 'notifications' && (
                        <div className="max-w-lg">
                            <p className="text-sm text-slate-500 mb-6">
                                Configure how and when you receive notifications about your properties.
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
                                                <p className="font-medium text-slate-900">In-app reminders</p>
                                                <p className="text-sm text-slate-500">Show reminders in the notification bell</p>
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
                                    </div>

                                    {/* Reminder lead times */}
                                    <div className="space-y-3">
                                        <div>
                                            <p className="font-medium text-slate-900 mb-1">Reminder timing</p>
                                            <p className="text-sm text-slate-500">Select when you want to be reminded before a document expires</p>
                                        </div>
                                        
                                        <div className="flex flex-wrap gap-2">
                                            {[90, 60, 30, 14, 7].map((day) => (
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
                                                    {day} days
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* Info about email */}
                                    <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 flex gap-3">
                                        <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                                        <div>
                                            <p className="text-sm font-medium text-blue-900">Email notifications</p>
                                            <p className="text-sm text-blue-700 mt-1">
                                                Email reminders will be enabled once we integrate an email service. 
                                                Your preference will be saved for when this feature goes live.
                                            </p>
                                        </div>
                                    </div>

                                    <div className="pt-4">
                                        <Button 
                                            onClick={savePreferences}
                                            disabled={saving}
                                            className="bg-blue-600 hover:bg-blue-700 text-white"
                                            data-testid="save-notifications"
                                        >
                                            {saving ? (
                                                <>
                                                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                                    Saving...
                                                </>
                                            ) : saved ? (
                                                <>
                                                    <CheckCircle2 className="w-4 h-4 mr-2" />
                                                    Saved
                                                </>
                                            ) : (
                                                'Save Preferences'
                                            )}
                                        </Button>
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'security' && (
                        <div className="max-w-lg space-y-6">
                            <div className="space-y-2">
                                <Label htmlFor="currentPassword">Current password</Label>
                                <Input
                                    id="currentPassword"
                                    type="password"
                                    className="h-11"
                                    data-testid="current-password"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="newPassword">New password</Label>
                                <Input
                                    id="newPassword"
                                    type="password"
                                    className="h-11"
                                    data-testid="new-password"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="confirmPassword">Confirm new password</Label>
                                <Input
                                    id="confirmPassword"
                                    type="password"
                                    className="h-11"
                                    data-testid="confirm-password"
                                />
                            </div>

                            <div className="pt-4">
                                <Button 
                                    className="bg-blue-600 hover:bg-blue-700 text-white"
                                    data-testid="change-password"
                                >
                                    Change Password
                                </Button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
