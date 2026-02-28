import { getOptionalUser } from './lifecycle';
import { AuthError } from './error_handler';
import { UserSession } from './token_validator';

/**
 * Protected Execution Guard.
 * 
 * Modes:
 * - strict mode -> throws AuthError backend exception if unauthenticated
 * - optional mode -> graceful null return
 * 
 * @param sessionId The current client's session identifier
 * @param strict Whether to throw an error if unauthenticated (default: true)
 */
export function requireAuth(sessionId: string, strict: boolean = true): UserSession | null {
    const user = getOptionalUser(sessionId);

    if (!user && strict) {
        throw new AuthError("User is not authenticated. Please log in first.");
    }

    return user;
}

/**
 * Higher Order Function decorator proxy for protecting backend API functions.
 * Automatically checks for authentication before executing the wrapped function.
 * 
 * @param strict Whether to enforce authentication (default: true)
 */
export function protectedRoute(strict: boolean = true) {
    return function <T extends (...args: any[]) => any>(
        // The wrapped function must explicitly accept sessionId as its first parameter
        func: (sessionId: string, ...funcArgs: any[]) => ReturnType<T>
    ) {
        return function (sessionId: string, ...args: any[]): ReturnType<T> {
            requireAuth(sessionId, strict);
            return func(sessionId, ...args);
        };
    };
}
