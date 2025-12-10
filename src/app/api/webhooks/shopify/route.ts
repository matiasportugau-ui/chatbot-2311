import { NextRequest, NextResponse } from 'next/server';
import { decodePubSubMessage, PubSubMessage } from '@/lib/google-pubsub';

export async function POST(req: NextRequest) {
    try {
        // 1. Parse the incoming request body as a Pub/Sub message
        const body: PubSubMessage = await req.json();

        if (!body.message || !body.message.data) {
            console.error('Invalid Pub/Sub message format', body);
            return NextResponse.json({ error: 'Invalid message format' }, { status: 400 });
        }

        // 2. Decode the data field (base64 encoded JSON)
        const shopifyEvent = decodePubSubMessage(body.message.data);

        if (!shopifyEvent) {
            return NextResponse.json({ error: 'Failed to decode message data' }, { status: 400 });
        }

        // 3. Log the event (In a real app, you would process it based on topic)
        // The topic is usually available in the subscription name or attributes if configured
        console.log('Received Shopify Webhook via Pub/Sub:', {
            messageId: body.message.messageId,
            publishTime: body.message.publishTime,
            event: shopifyEvent,
            attributes: body.message.attributes
        });

        // TODO: Add specific extraction logic here based on requirements (e.g. update product DB)

        // 4. Acknowledge receipt to Pub/Sub
        // Returning a success status code (200, 201, 202, 204) acknowledges the message.
        // If we return 5xx or 4xx (except 404/403/401 maybe?), Pub/Sub will retry.
        return NextResponse.json({ status: 'received' }, { status: 200 });

    } catch (error) {
        console.error('Error processing Pub/Sub webhook:', error);
        return NextResponse.json(
            { error: 'Internal Server Error' },
            { status: 500 }
        );
    }
}
