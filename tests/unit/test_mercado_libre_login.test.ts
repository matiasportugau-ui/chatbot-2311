import { verifyMercadoLibreLogin } from '../../src/lib/mercado-libre/auth';
import * as tokenStore from '../../src/lib/mercado-libre/token-store';

// Mock fetch globally
global.fetch = jest.fn();

describe('verifyMercadoLibreLogin', () => {
    afterEach(() => {
        jest.resetAllMocks();
    });

    it('returns loggedIn false when no active grant', async () => {
        jest.spyOn(tokenStore, 'getActiveGrant').mockResolvedValue(null as any);
        const result = await verifyMercadoLibreLogin();
        expect(result.loggedIn).toBe(false);
    });

    it('returns loggedIn false when fetch fails', async () => {
        const mockGrant = {
            accessToken: 'dummy-token',
            apiBaseUrl: 'https://api.mercadolibre.com',
        } as any;
        jest.spyOn(tokenStore, 'getActiveGrant').mockResolvedValue(mockGrant);
        (global.fetch as jest.Mock).mockResolvedValue({ ok: false, status: 401 });
        const result = await verifyMercadoLibreLogin();
        expect(result.loggedIn).toBe(false);
    });

    it('returns loggedIn true with profile on successful fetch', async () => {
        const mockGrant = {
            accessToken: 'valid-token',
            apiBaseUrl: 'https://api.mercadolibre.com',
        } as any;
        jest.spyOn(tokenStore, 'getActiveGrant').mockResolvedValue(mockGrant);
        const mockProfile = { id: 123, nickname: 'testuser' };
        (global.fetch as jest.Mock).mockResolvedValue({
            ok: true,
            json: async () => mockProfile,
        });
        const result = await verifyMercadoLibreLogin();
        expect(result.loggedIn).toBe(true);
        expect(result.profile).toEqual(mockProfile);
    });
});
