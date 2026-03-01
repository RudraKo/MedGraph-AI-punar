import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { apiClient } from '../api/httpClient';

export const DashboardPage: React.FC = () => {
    const { user, logout } = useAuth();
    const [interactions, setInteractions] = React.useState<any>(null);

    const testInteraction = async () => {
        try {
            const res = await apiClient.post('/interactions/check', { drug_ids: ["Aspirin", "Ibuprofen"] });
            setInteractions(res.data);
        } catch (e) { console.error(e); }
    }

    return (
        <div style={{ padding: '20px' }}>
            <h2>Dashboard</h2>
            <p>Welcome, {user?.name} ({user?.role})</p>
            <button onClick={logout}>Logout</button>
            <hr />
            <h3>Test Interaction API</h3>
            <button onClick={testInteraction}>Check Aspirin + Ibuprofen</button>
            {interactions && <pre>{JSON.stringify(interactions, null, 2)}</pre>}
        </div>
    );
};
