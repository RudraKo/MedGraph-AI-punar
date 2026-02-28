import { UserSession } from './token_validator';

/**
 * Generic In-Memory Session storage for Hackathon purposes.
 * This acts as a lightweight session store. In a generic TS backend,
 * you would associate this with a sessionID stored in a cookie.
 */

interface SessionData {
    user?: UserSession;
    oauthState?: string;
}

// Global in-memory store
const sessionStore = new Map<string, SessionData>();

// Helper to get or create session object
export function getOrCreateSessionData(sessionId: string): SessionData {
    if (!sessionStore.has(sessionId)) {
        sessionStore.set(sessionId, {});
    }
    return sessionStore.get(sessionId)!;
}

/**
 * Create a new authenticated session for the user.
 * 
 * @param sessionId Unique identifier for the client session
 * @param userInfo Extracted user identity dictionary.
 */
export function createSession(sessionId: string, userInfo: UserSession): void {
    const data = getOrCreateSessionData(sessionId);
    data.user = userInfo;
}

/**
 * Retrieve the current authenticated user's profile info.
 * 
 * @param sessionId Unique identifier for the client session
 * @returns User profile info if authenticated, else null.
 */
export function getCurrentUser(sessionId: string): UserSession | null {
    const data = sessionStore.get(sessionId);
    return data?.user || null;
}

/**
 * Clear the current authentication session.
 * 
 * @param sessionId Unique identifier for the client session
 */
export function logout(sessionId: string): void {
    if (sessionStore.has(sessionId)) {
        const data = sessionStore.get(sessionId)!;
        delete data.user;
    }
}

/** Store the OAuth state token to verify upon callback. */
export function setOAuthState(sessionId: string, state: string): void {
    const data = getOrCreateSessionData(sessionId);
    data.oauthState = state;
}

/** Retrieve the stored OAuth state token. */
export function getOAuthState(sessionId: string): string | null {
    const data = sessionStore.get(sessionId);
    return data?.oauthState || null;
}

/** Clear the OAuth state token. */
export function clearOAuthState(sessionId: string): void {
    if (sessionStore.has(sessionId)) {
        const data = sessionStore.get(sessionId)!;
        delete data.oauthState;
    }
}
