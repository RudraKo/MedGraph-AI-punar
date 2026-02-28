import { UserSession } from './token_validator';

/**
 * Extract required identity fields from Google's userinfo response.
 * 
 * @param googleUserinfo The raw JSON response from Google userinfo API.
 * @returns A structured object containing user_id, email, name, and picture.
 */
export function extractUserIdentity(googleUserinfo: Record<string, any>): UserSession {
    // Extract identity fields safely
    const userId = googleUserinfo.sub || googleUserinfo.id;
    const email = googleUserinfo.email;
    const name = googleUserinfo.name;
    const picture = googleUserinfo.picture;

    if (!userId || !email) {
        throw new Error("Invalid userinfo response: missing required identity fields (sub/email).");
    }

    return {
        user_id: String(userId),
        email: String(email),
        name: name ? String(name) : "",
        picture: picture ? String(picture) : ""
    };
}
