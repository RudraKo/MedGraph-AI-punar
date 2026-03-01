import React from 'react';
import { useAuth } from '../hooks/useAuth';

export const LoginPage: React.FC = () => {
    const { login } = useAuth();
    return (
        <div style={{ display: 'flex', height: '100vh', justifyContent: 'center', alignItems: 'center' }}>
            <div>
                <h1>Welcome to MedGraph.AI</h1>
                <button onClick={login} style={{ padding: '10px 20px', fontSize: '16px' }}>Login with Google</button>
            </div>
        </div>
    );
};
