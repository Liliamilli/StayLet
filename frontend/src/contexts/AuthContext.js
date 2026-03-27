import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const API_URL = process.env.REACT_APP_BACKEND_URL;

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('staylet_token'));
    const [loading, setLoading] = useState(true);
    const [subscription, setSubscription] = useState(null);
    const [isDemo, setIsDemo] = useState(false);
    const [onboardingStatus, setOnboardingStatus] = useState(null);

    // Configure axios defaults
    useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
            delete axios.defaults.headers.common['Authorization'];
        }
    }, [token]);

    // Verify token and get user on mount
    const verifyToken = useCallback(async () => {
        if (!token) {
            setLoading(false);
            return;
        }

        try {
            const response = await axios.get(`${API_URL}/api/auth/me`);
            setUser(response.data);
            setIsDemo(response.data.email?.includes('@staylet-demo.com') || false);
            
            // Also fetch subscription details
            try {
                const subResponse = await axios.get(`${API_URL}/api/subscription`);
                setSubscription(subResponse.data);
            } catch (e) {
                console.error('Failed to fetch subscription:', e);
            }
            
            // Fetch onboarding status
            try {
                const onboardingResponse = await axios.get(`${API_URL}/api/user/onboarding`);
                setOnboardingStatus(onboardingResponse.data);
            } catch (e) {
                console.error('Failed to fetch onboarding status:', e);
            }
        } catch (error) {
            console.error('Token verification failed:', error);
            localStorage.removeItem('staylet_token');
            setToken(null);
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, [token]);

    useEffect(() => {
        verifyToken();
    }, [verifyToken]);

    const refreshSubscription = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/subscription`);
            setSubscription(response.data);
            return response.data;
        } catch (error) {
            console.error('Failed to refresh subscription:', error);
            return null;
        }
    };

    const signup = async (email, password, fullName) => {
        const response = await axios.post(`${API_URL}/api/auth/signup`, {
            email,
            password,
            full_name: fullName
        });
        
        const { user: userData, token: authToken } = response.data;
        localStorage.setItem('staylet_token', authToken);
        setToken(authToken);
        setUser(userData);
        setIsDemo(false);
        setOnboardingStatus({ completed: false, current_step: 1, steps_completed: [] });
        
        // Set initial subscription from user data
        setSubscription({
            plan: userData.subscription_plan,
            status: userData.subscription_status,
            property_limit: userData.property_limit,
            property_count: userData.property_count,
            trial_end: userData.trial_end
        });
        
        return userData;
    };

    const login = async (email, password) => {
        const response = await axios.post(`${API_URL}/api/auth/login`, {
            email,
            password
        });
        
        const { user: userData, token: authToken } = response.data;
        localStorage.setItem('staylet_token', authToken);
        setToken(authToken);
        setUser(userData);
        setIsDemo(userData.email?.includes('@staylet-demo.com') || false);
        
        // Fetch full subscription details
        try {
            const subResponse = await axios.get(`${API_URL}/api/subscription`);
            setSubscription(subResponse.data);
        } catch (e) {
            console.error('Failed to fetch subscription:', e);
        }
        
        // Fetch onboarding status
        try {
            const onboardingResponse = await axios.get(`${API_URL}/api/user/onboarding`);
            setOnboardingStatus(onboardingResponse.data);
        } catch (e) {
            console.error('Failed to fetch onboarding status:', e);
        }
        
        return userData;
    };

    const startDemo = async () => {
        const response = await axios.post(`${API_URL}/api/auth/demo`);
        
        const { user: userData, token: authToken } = response.data;
        localStorage.setItem('staylet_token', authToken);
        setToken(authToken);
        setUser(userData);
        setIsDemo(true);
        setOnboardingStatus({ completed: true, current_step: 4, steps_completed: ['add_property', 'add_compliance', 'view_dashboard'] });
        
        // Set subscription
        setSubscription({
            plan: userData.subscription_plan,
            plan_name: 'Portfolio',
            status: userData.subscription_status,
            property_limit: userData.property_limit,
            property_count: userData.property_count,
            trial_end: userData.trial_end
        });
        
        return userData;
    };

    const refreshOnboarding = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/user/onboarding`);
            setOnboardingStatus(response.data);
            return response.data;
        } catch (error) {
            console.error('Failed to refresh onboarding:', error);
            return null;
        }
    };

    const completeOnboarding = async () => {
        try {
            await axios.post(`${API_URL}/api/user/onboarding/complete`);
            setOnboardingStatus(prev => ({ ...prev, completed: true }));
        } catch (error) {
            console.error('Failed to complete onboarding:', error);
        }
    };

    const logout = () => {
        localStorage.removeItem('staylet_token');
        setToken(null);
        setUser(null);
        setSubscription(null);
        setIsDemo(false);
        setOnboardingStatus(null);
        delete axios.defaults.headers.common['Authorization'];
    };

    const resetPassword = async (email) => {
        const response = await axios.post(`${API_URL}/api/auth/reset-password`, {
            email
        });
        return response.data;
    };

    const value = {
        user,
        token,
        loading,
        isAuthenticated: !!user,
        isDemo,
        subscription,
        onboardingStatus,
        refreshSubscription,
        refreshOnboarding,
        completeOnboarding,
        signup,
        login,
        startDemo,
        logout,
        resetPassword
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
