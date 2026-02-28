import { processOauthCallback, getOptionalUser } from './lifecycle';
import { handleAuthError } from './error_handler';

// Simulating a per-request initialization tracker for idempotency 
// Note: In an Express backend, this logic would typically live in middleware attached to the request object.
const _AUTH_INITIALIZED = new WeakSet<any>();

/**
 * Authentication Lifecycle Manager.
 * Designed to be generic for backend endpoints (like Express or Next.js API).
 * 
 * @param req Any incoming request object (e.g. Express Request) that carries query and session info
 * @param sessionId The current client's session ID
 */
export async function initializeAuth(req: any, sessionId: string): Promise<void> {
    // Prevent duplicate initialization per request object if provided
    if (req && _AUTH_INITIALIZED.has(req)) {
        return;
    }

    try {
        // 1. Detect OAuth return query parameters
        // Assuming req.query exists (common in Express/NextJS)
        if (req && req.query) {
            const code = req.query.code as string;
            const state = req.query.state as string;

            if (code && state) {
                // 2. Process authorization code silently
                await processOauthCallback(sessionId, code, state);

                // 3. In typical JS frameworks, redirecting clears query params 
                // e.g. res.redirect(req.path) would happen here to clear URL params.
            }
        }

        // 4. Check session validity automatically by fetching the optional user
        getOptionalUser(sessionId);

        // 5. Lock initialization for this specific request processing 
        if (req) {
            _AUTH_INITIALIZED.add(req);
        }

    } catch (e) {
        handleAuthError(e);
        if (req) {
            _AUTH_INITIALIZED.add(req);
        }
    }
}
