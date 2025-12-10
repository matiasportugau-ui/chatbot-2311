export interface PubSubMessage {
    message: {
        data: string;
        messageId: string;
        publishTime: string;
        attributes?: Record<string, string>;
    };
    subscription: string;
}

/**
 * Decodes a base64 encoded Pub/Sub message data string into a JSON object.
 */
export function decodePubSubMessage(data: string): any {
    try {
        const buffer = Buffer.from(data, 'base64');
        const jsonString = buffer.toString('utf-8');
        return JSON.parse(jsonString);
    } catch (error) {
        console.error('Error decoding Pub/Sub message:', error);
        return null;
    }
}
