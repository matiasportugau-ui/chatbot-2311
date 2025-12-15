import { NextRequest, NextResponse } from 'next/server';
import { getCRMStats } from '@/lib/crm';

/**
 * GET /api/crm/stats
 * Get CRM statistics and analytics
 */
export async function GET(request: NextRequest) {
  try {
    const stats = await getCRMStats();

    return NextResponse.json(stats);
  } catch (error) {
    console.error('Error getting CRM stats:', error);
    return NextResponse.json(
      {
        error: 'Failed to get CRM stats',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
