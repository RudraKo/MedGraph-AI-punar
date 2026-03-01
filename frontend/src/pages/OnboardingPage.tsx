import React, { useState } from 'react';
import { apiClient } from '../api/httpClient';
import { useNavigate } from 'react-router-dom';

export const OnboardingPage: React.FC = () => {
    const [role, setRole] = useState('patient');
    const navigate = useNavigate();

    const handleSave = async () => {
        await apiClient.post('/auth/onboarding', { role });
        navigate('/dashboard');
    };

    return (
        <div style={{ padding: '20px' }}>
            <h2>Select Your Role</h2>
            <select value={role} onChange={e => setRole(e.target.value)}>
                <option value="patient">Patient</option>
                <option value="doctor">Doctor</option>
                <option value="guardian">Guardian</option>
            </select>
            <br /><br />
            <button onClick={handleSave}>Complete Onboarding</button>
        </div>
    );
};
