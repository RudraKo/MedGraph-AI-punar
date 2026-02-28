import { getOAuthConfig, generateStateToken } from './config';
import { setOAuthState, getOAuthState, clearOAuthState } from './session_manager';
import { extractUserIdentity } from './user_service';
import { UserSession } from './token_validator';

/**
 * Generate the Google OAuth 2.0 authorization URL.
 * This also generates and stores a state token for CSRF protection.
 * 
 * @param sessionId The current client's session ID
 * @returns The full URL to redirect the user to for Google login.
 */
export function generateAuthUrl(sessionId: string): string {
    const config = getOAuthConfig();
    const state = generateStateToken();

    // Store state in session for validation during callback
    setOAuthState(sessionId, state);

    const params = new URLSearchParams({
        client_id: config.clientId,
        redirect_uri: config.redirectUri,
        response_type: "code",
        scope: config.scopes.join(" "),
        state: state,
        access_type: "online",
        prompt: "select_account"
    });

    return `${config.authUri}?${params.toString()}`;
}

/**
 * Exchange the authorization code for tokens and extract user info.
 * Validates the CSRF state parameter.
 * 
 * @param sessionId The current client's session ID
 * @param authCode The code returned by Google in the redirect URL.
 * @param returnedState The state token returned by Google to prevent CSRF.
 * @returns The structured user identity extracted from Google's response.
 * @throws Error If state validation fails or token exchange fails.
 */
export async function handleOauthCallback(sessionId: string, authCode: string, returnedState: string): Promise<UserSession> {
    // 1. CSRF State Validation
    const storedState = getOAuthState(sessionId);
    clearOAuthState(sessionId);

    if (!storedState || storedState !== returnedState) {
        throw new Error("Invalid state parameter. CSRF validation failed.");
    }

    const config = getOAuthConfig();

    // 2. Exchange Authorization Code for Tokens
    const tokenParams = new URLSearchParams({
        code: authCode,
        client_id: config.clientId,
        client_secret: config.clientSecret,
        redirect_uri: config.redirectUri,
        grant_type: "authorization_code"
    });

    const tokenResponse = await fetch(config.tokenUri, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: tokenParams.toString()
    });

    if (!tokenResponse.ok) {
        const errText = await tokenResponse.text();
        throw new Error(`Failed to exchange token: ${errText}`);
    }

    const tokens = await tokenResponse.json();
    const accessToken = tokens.access_token;

    if (!accessToken) {
        throw new Error("Access token not found in Google response.");
    }

    // 3. Retrieve User Identity Information
    const userinfoUrl = "https://www.googleapis.com/oauth2/v3/userinfo";
    const userinfoResponse = await fetch(userinfoUrl, {
        headers: { "Authorization": `Bearer ${accessToken}` }
    });

    if (!userinfoResponse.ok) {
        throw new Error("Failed to fetch user profile information.");
    }

    const rawUserinfo = await userinfoResponse.json();

    // 4. Extract and return standardized user identity
    const userInfo = extractUserIdentity(rawUserinfo);

    // Track expiration based on token response
    const expiresIn = tokens.expires_in;
    if (expiresIn) {
        userInfo.expires_at = (Date.now() / 1000) + Number(expiresIn);
    }

    return userInfo;
}
