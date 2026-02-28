export interface UserSession {
    user_id: string;
    email: string;
    name: string;
    picture: string;
    expires_at?: number;
    [key: string]: any;
}

/**
 * Validates token existence, malformed token handling, and expiration awareness.
 * If the session is invalid, returns false.
 * 
 * @param userSession The current extracted user dict which may contain expiry.
 * @returns True if token is considered valid, false otherwise.
 */
export function validateToken(userSession: UserSession | null | undefined): boolean {
    if (!userSession) {
        return false;
    }

    // Check if this token has tracking info
    const expiresAt = userSession.expires_at;
    if (!expiresAt) {
        // If no expiration tracking, default to valid for session duration
        return true;
    }

    try {
        const currentTime = Date.now() / 1000; // in seconds
        // 5 minute grace period (300 seconds)
        if (currentTime > (expiresAt - 300)) {
            return false;
        }
    } catch (e) {
        // Malformed expiration
        return false;
    }

    return true;
}
