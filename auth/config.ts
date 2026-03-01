import * as crypto from 'crypto';

export interface OAuthConfig {
    clientId: string;
    clientSecret: string;
    redirectUri: string;
    authUri: string;
    tokenUri: string;
    scopes: string[];
}

/**
 * Load Google OAuth 2.0 configuration from environment variables.
 * 
 * @returns Configuration dictionary containing client ID, secret, and scopes.
 */
export function getOAuthConfig(): OAuthConfig {
    const clientId = process.env.GOOGLE_CLIENT_ID;
    const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
    const redirectUri =
        process.env.GOOGLE_REDIRECT_URI ||
        process.env.GOOGLE_CALLBACK_URL ||
        "http://localhost:3000/auth/google/callback";

    if (!clientId || !clientSecret) {
        throw new Error("Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in environment variables.");
    }

    return {
        clientId,
        clientSecret,
        redirectUri,
        authUri: "https://accounts.google.com/o/oauth2/v2/auth",
        tokenUri: "https://oauth2.googleapis.com/token",
        scopes: [
            "openid",
            "email",
            "profile"
        ]
    };
}

/**
 * Generate a secure random state token for CSRF protection.
 * 
 * @returns Hex-encoded random string.
 */
export function generateStateToken(): string {
    return crypto.randomBytes(16).toString('hex');
}
