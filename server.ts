import express from 'express';
import cookieParser from 'cookie-parser';
import { v4 as uuidv4 } from 'uuid';
import * as dotenv from 'dotenv';
import {
    initializeAuth,
    generateAuthUrl,
    getOptionalUser,
    logoutUser,
    requireAuth,
    protectedRoute
} from './auth';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(cookieParser());

// Middleware to Ensure every client gets a Session ID
app.use((req, res, next) => {
    let sessionId = req.cookies.sessionId;
    if (!sessionId) {
        sessionId = uuidv4();
        res.cookie('sessionId', sessionId, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'lax',
            maxAge: 1000 * 60 * 60 * 24 // 24 hours
        });
        req.cookies.sessionId = sessionId;
    }
    next();
});


// 1. Initializer Route: The Callback URL Google sends users back to
app.get('/oauth2callback', async (req, res) => {
    try {
        const sessionId = req.cookies.sessionId;
        // This will seamlessly extract ?code= and ?state= and build the session
        await initializeAuth(req, sessionId);

        // Redirect to a protected dashboard upon successful auth
        res.redirect('/dashboard');
    } catch (e: any) {
        console.error("Auth callback failed:", e);
        res.status(500).send("Authentication failed.");
    }
});


// 2. Login URL Generator Route
app.get('/login', (req, res) => {
    const sessionId = req.cookies.sessionId;
    const url = generateAuthUrl(sessionId);
    res.redirect(url);
});


// 3. Logout Route
app.get('/logout', (req, res) => {
    const sessionId = req.cookies.sessionId;
    logoutUser(sessionId);
    res.redirect('/');
});


// 4. Public Route (Optional Auth checking)
app.get('/', (req, res) => {
    const sessionId = req.cookies.sessionId;
    const user = getOptionalUser(sessionId);

    if (user) {
        res.send(`<h1>Welcome to MedGraph AI, ${user.name}!</h1> <a href="/dashboard">Go to Dashboard</a> | <a href="/logout">Logout</a>`);
    } else {
        res.send(`<h1>MedGraph AI</h1> <p>You are not logged in.</p> <a href="/login">Login with Google</a>`);
    }
});


// 5. Protected Route Example
app.get('/dashboard', (req, res) => {
    const sessionId = req.cookies.sessionId;
    try {
        // Enforce strict authorization
        const user = requireAuth(sessionId, true);

        res.send(`
            <h1>Dashboard</h1>
            <p>Welcome to your secure health data, ${user?.name}.</p>
            <p>Email: ${user?.email}</p>
            <img src="${user?.picture}" alt="Profile Picture" style="width: 100px; border-radius: 50%;" />
            <br/><br/>
            <button onclick="fetchHealthData()">Fetch Secure API Data</button>
            <pre id="output"></pre>
            <script>
                async function fetchHealthData() {
                    const res = await fetch('/api/secure-health-data');
                    const data = await res.json();
                    document.getElementById('output').innerText = JSON.stringify(data, null, 2);
                }
            </script>
            <br/><br/>
            <a href="/logout">Logout</a>
        `);
    } catch (e: any) {
        // Specifically trap AuthError and redirect to login
        res.redirect('/login');
    }
});


// 6. Protected Backend API Example (using Higher Order Function wrapper)
const fetchSensitiveData = protectedRoute(true)((sessionId: string) => {
    return {
        status: "success", data: [
            { patientId: "123", diagnosis: "Healthy" },
            { patientId: "456", diagnosis: "Stable" }
        ]
    };
});

app.get('/api/secure-health-data', (req, res) => {
    const sessionId = req.cookies.sessionId;
    try {
        // If unauthenticated, it throws an error that is caught below.
        const data = fetchSensitiveData(sessionId);
        res.json(data);
    } catch (e: any) {
        res.status(401).json({ error: "Access Denied: " + e.message });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
});
