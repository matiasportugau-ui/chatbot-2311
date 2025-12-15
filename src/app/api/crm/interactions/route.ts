import { NextRequest, NextResponse } from 'next/server';
import { createInteraction, getCustomerInteractions, type CreateInteractionInput } from '@/lib/crm';

/**
 * POST /api/crm/interactions
 * Create new interaction
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    if (!body.customerId || !body.type || !body.content) {
      return NextResponse.json(
        { error: 'Missing required fields: customerId, type, content' },
        { status: 400 }
      );
    }

    const input: CreateInteractionInput = {
      customerId: body.customerId,
      type: body.type,
      direction: body.direction,
      subject: body.subject,
      content: body.content,
      tags: body.tags || [],
      quoteId: body.quoteId,
      orderId: body.orderId,
      occurredAt: body.occurredAt ? new Date(body.occurredAt) : undefined,
    };

    const interaction = await createInteraction(input);

    return NextResponse.json({
      success: true,
      interaction,
    });
  } catch (error) {
    console.error('Error creating interaction:', error);
    return NextResponse.json(
      {
        error: 'Failed to create interaction',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/crm/interactions?customerId=xxx
 * Get customer interactions
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const customerId = searchParams.get('customerId');

    if (!customerId) {
      return NextResponse.json({ error: 'Missing customerId parameter' }, { status: 400 });
    }

    const limit = parseInt(searchParams.get('limit') || '100');
    const interactions = await getCustomerInteractions(customerId, limit);

    return NextResponse.json({
      interactions,
      total: interactions.length,
    });
  } catch (error) {
    console.error('Error getting interactions:', error);
    return NextResponse.json(
      {
        error: 'Failed to get interactions',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
