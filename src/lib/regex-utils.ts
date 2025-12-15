/**
 * Regex patterns ported from ia_conversacional_integrada.py
 * for consistent entity extraction across the platform.
 */

export const REGEX_PATTERNS = {
    // Dimensions: 10x5, 10.5 x 5.2, 10m x 5m
    DIMENSIONS: [
        /(\d+(?:\.\d+)?)\s*[x×]\s*(\d+(?:\.\d+)?)/i,
        /(\d+(?:\.\d+)?)\s*metros?\s*[x×]\s*(\d+(?:\.\d+)?)\s*metros?/i,
        /(\d+(?:\.\d+)?)\s*m\s*[x×]\s*(\d+(?:\.\d+)?)\s*m/i
    ],

    // Phone: +598 99 123 456, 099123456
    PHONE: /(\+?598\s?)?(\d{2,3}\s?\d{3}\s?\d{3})/,

    // Name extraction patterns
    NAME_PRESENTATION: /(?:me llamo|soy|mi nombre es)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)/i,
    NAME_SIMPLE: /^([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)$/
};

export function extractDimensions(text: string): { largo: number, ancho: number } | null {
    for (const pattern of REGEX_PATTERNS.DIMENSIONS) {
        const match = text.match(pattern);
        if (match) {
            try {
                const largo = parseFloat(match[1]);
                const ancho = parseFloat(match[2]);
                return { largo, ancho };
            } catch (e) {
                continue;
            }
        }
    }
    return null;
}

export function extractPhone(text: string): string | null {
    const match = text.match(REGEX_PATTERNS.PHONE);
    if (match) {
        return match[0].replace(/\s/g, '');
    }
    return null;
}
