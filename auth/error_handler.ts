/**
 * Raised for authentication related failures.
 */
export class AuthError extends Error {
    constructor(message: string) {
        super(message);
        this.name = "AuthError";
    }
}

/**
 * Centralized handler for authentication failures.
 * Logs safely, resets auth state if needed, and prevents app crashes.
 * @param error The exception that was thrown.
 * @param logoutFn Function to execute logout securely avoiding circular dependencies.
 */
export function handleAuthError(error: Error | unknown, logoutFn?: () => void): void {
    // Safe logging
    console.error("Authentication Error:", error instanceof Error ? error.message : String(error));

    // Safe reset
    if (logoutFn) {
        try {
            logoutFn();
        } catch (resetError) {
            console.error("Failed to cleanly reset auth state during error handling:",
                resetError instanceof Error ? resetError.message : String(resetError)
            );
        }
    }
}
