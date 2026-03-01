import { useState, useEffect } from 'react';
import { apiClient } from '../api/httpClient';

export function useAuth() {
    const [user, setUser] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        apiClient.get('/auth/me')
            .then(res => setUser(res.data.user))
            .catch(() => setUser(null))
            .finally(() => setLoading(false));
    }, []);

    const login = () => {
        window.location.href = `${import.meta.env.VITE_AUTH_URL || 'http://localhost:3000'}/auth/login`;
    };

    const logout = () => {
        document.cookie = 'medgraph_token=; Max-Age=0; path=/;';
        window.location.href = '/login';
    };

    return { user, loading, login, logout };
}
