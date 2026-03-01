import express from 'express';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import axios from 'axios';
import dotenv from 'dotenv';
import { generateAuthUrl, handleOauthCallback } from './oauth_service';
import { extractUserIdentity } from './user_service';

dotenv.config({ path: '../.env' }); // load from root

const app = express();
const PORT = process.env.AUTH_PORT || 3000;
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173';

app.use(cors({
    origin: FRONTEND_URL,
    credentials: true
}));
app.use(express.json());
app.use(cookieParser());

app.get('/auth/login', (req, res) => {
    let sessionId = req.cookies.sessionId;
    if (!sessionId) {
        sessionId = require('crypto').randomUUID();
        res.cookie('sessionId', sessionId, { httpOnly: true, maxAge: 10 * 60 * 1000 });
    }
    const url = generateAuthUrl(sessionId);
    res.redirect(url);
});

app.get('/auth/google/callback', async (req, res) => {
    const code = req.query.code as string;
    const state = req.query.state as string;
    if (!code || !state) return res.status(400).send('Missing code or state');

    try {
        const userInfo = await handleOauthCallback(req.cookies.sessionId, code, state);
        const { user_id, email, name, picture } = userInfo;

        // Push user to FastAPI
        const response = await axios.post(`${FASTAPI_URL}/api/v1/auth/google-callback`, {
            google_id: user_id,
            email,
            name,
            picture
        });

        const { token, is_new, role } = response.data as any;

        // Store the JWT (contains role, email, name) issued by the FastAPI backend
        res.cookie('medgraph_token', token, {
            httpOnly: false,           // must be readable by frontend JS to extract role
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'lax',
            maxAge: 7 * 24 * 60 * 60 * 1000
        });

        if (is_new || role === '__pending__') {
            // New user – send to onboarding to pick their role
            res.redirect(`${FRONTEND_URL}/onboarding`);
        } else {
            // Returning user – go directly to their role-specific dashboard
            const roleDestination: Record<string, string> = {
                admin: '/roles/admin',
                doctor: '/roles/doctor',
                patient: '/roles/patient',
                caretaker: '/roles/caretaker',
            };
            res.redirect(`${FRONTEND_URL}${roleDestination[role] || '/dashboard'}`);
        }
    } catch (error) {
        console.error('OAuth Error:', error);
        res.redirect(`${FRONTEND_URL}/login?error=auth_failed`);
    }
});

app.post('/auth/logout', (req, res) => {
    res.clearCookie('medgraph_token');
    res.json({ success: true });
});

app.listen(PORT, () => {
    console.log(`Auth server running on port ${PORT}`);
});
