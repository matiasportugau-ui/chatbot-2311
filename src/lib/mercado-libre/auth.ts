import { getActiveGrant } from './token-store';

/**
 * Verifies MercadoLibre login status by checking the stored access token and
 * making a lightweight request to the MercadoLibre API.
 *
 * Returns an object indicating whether the user is logged in and, if so,
 * includes the user profile returned by the `/users/me` endpoint.
 */
export async function verifyMercadoLibreLogin(): Promise<{ loggedIn: boolean; profile?: any }> {
    const grant = await getActiveGrant();
    if (!grant || !grant.accessToken) {
        return { loggedIn: false };
    }
    const url = `${grant.apiBaseUrl || 'https://api.mercadolibre.com'}/users/me`;
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${grant.accessToken}`,
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            return { loggedIn: false };
        }
        const data = await response.json();
        return { loggedIn: true, profile: data };
    } catch (err) {
        return { loggedIn: false };
    }
}
