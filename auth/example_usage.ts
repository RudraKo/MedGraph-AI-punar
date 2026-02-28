import {
    initializeAuth,
    generateAuthUrl,
    requireAuth,
    getOptionalUser,
    logoutUser,
    protectedRoute
} from './index';

// Setup Environment Variables (Normally in your .env file)
process.env.GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com";
process.env.GOOGLE_CLIENT_SECRET = "your-client-secret";
process.env.GOOGLE_REDIRECT_URI = "http://localhost:3000/oauth2callback";

// In a real framework (Express/Next.js), sessionId usually comes from a tracking cookie.
const DUMMY_SESSION_ID = "req_session_uuid456";

async function runExampleServerFlow() {
    // Example Request Object (e.g. from Express)
    const mockRequest = {
        query: {
            // In a real flow, if the user returns from Google, these are set
            // code: "4/0AeaYSH...",
            // state: "stored_state_from_url"
        }
    };

    // 1. Initialize Auth Lifecycle (Call this EARLY in your middleware)
    // This will silently handle query parameters and sync sessions.
    await initializeAuth(mockRequest, DUMMY_SESSION_ID);

    // 2. Check Optional User
    const currentUser = getOptionalUser(DUMMY_SESSION_ID);

    if (!currentUser) {
        // 3. Generate Login URL for user to navigate to
        const loginUrl = generateAuthUrl(DUMMY_SESSION_ID);
        console.log("Redirect user to:", loginUrl);
    } else {
        console.log(`Welcome back, ${currentUser.name}!`);
    }

    // 4. Protect a specific backend function using Higher Order Function wrapper
    const fetchSensitiveData = protectedRoute(true)((sessionId: string) => {
        console.log("Fetching secure health data for session:", sessionId);
        return { status: "success", data: [1, 2, 3] };
    });

    try {
        const data = fetchSensitiveData(DUMMY_SESSION_ID);
        console.log(data);
    } catch (e: any) {
        console.log("Access Denied to protected backend function:", e.message);
    }

    // 5. Inline strict authorization check
    try {
        const user = requireAuth(DUMMY_SESSION_ID, true);
        console.log("User is authorized for manual action:", user!.email);
    } catch (e: any) {
        console.log("Manual action blocked:", e.message);
    }

    // 6. Logout seamlessly
    // logoutUser(DUMMY_SESSION_ID);
    // console.log("Logged out safely");
}

runExampleServerFlow().catch(console.error);
