export interface AuthResult {
    url: string
}

export interface CallbackResult {
    redirectTo: string
    tokens?: any
}

export async function startAuthorization(returnTo?: string): Promise<AuthResult> {
    // Mock implementation
    const authUrl = `https://auth.mercadolibre.com/authorization?response_type=code&client_id=${process.env.MELI_APP_ID || 'dummy'}`
    // In a real app we'd encode state with returnTo
    return { url: authUrl }
}

export async function handleAuthorizationCallback(code: string, state: string): Promise<CallbackResult> {
    // Mock implementation
    // Assume state contains the return path
    let redirectTo = '/dashboard'
    try {
        const stateObj = JSON.parse(decodeURIComponent(state))
        if (stateObj.returnTo) redirectTo = stateObj.returnTo
    } catch (e) { }

    return { redirectTo }
}
