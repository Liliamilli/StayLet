import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

const API_URL = process.env.REACT_APP_BACKEND_URL;

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('staylet_token'));
    const [loading, setLoading] = useState(true);

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
        
        return userData;
    };

    const logout = () => {
        localStorage.removeItem('staylet_token');
        setToken(null);
        setUser(null);
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
        signup,
        login,
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
