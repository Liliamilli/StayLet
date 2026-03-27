import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { 
    User, 
    Bell, 
    Shield, 
    Loader2,
    CheckCircle2
} from 'lucide-react';

export default function SettingsPage() {
    const { user } = useAuth();
    const [activeTab, setActiveTab] = useState('profile');
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);

    const handleSave = async () => {
        setSaving(true);
        // Simulate save
        await new Promise(resolve => setTimeout(resolve, 1000));
        setSaving(false);
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
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
                            
                            <div className="space-y-4">
                                <div className="flex items-center justify-between py-3 border-b border-slate-100">
                                    <div>
                                        <p className="font-medium text-slate-900">Email reminders</p>
                                        <p className="text-sm text-slate-500">Receive email alerts before documents expire</p>
                                    </div>
                                    <div className="w-11 h-6 bg-blue-600 rounded-full relative cursor-pointer">
                                        <div className="absolute right-0.5 top-0.5 w-5 h-5 bg-white rounded-full shadow" />
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between py-3 border-b border-slate-100">
                                    <div>
                                        <p className="font-medium text-slate-900">Task reminders</p>
                                        <p className="text-sm text-slate-500">Get notified about upcoming tasks</p>
                                    </div>
                                    <div className="w-11 h-6 bg-blue-600 rounded-full relative cursor-pointer">
                                        <div className="absolute right-0.5 top-0.5 w-5 h-5 bg-white rounded-full shadow" />
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between py-3">
                                    <div>
                                        <p className="font-medium text-slate-900">Marketing emails</p>
                                        <p className="text-sm text-slate-500">Receive tips, updates, and offers</p>
                                    </div>
                                    <div className="w-11 h-6 bg-slate-200 rounded-full relative cursor-pointer">
                                        <div className="absolute left-0.5 top-0.5 w-5 h-5 bg-white rounded-full shadow" />
                                    </div>
                                </div>
                            </div>
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
