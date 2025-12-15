import { NextRequest, NextResponse } from 'next/server';
import {
  createCustomer,
  searchCustomers,
  getOrCreateCustomer,
  type CreateCustomerInput,
  type CustomerSearchFilters,
} from '@/lib/crm';

/**
 * GET /api/crm/customers
 * Search/list customers
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);

    // Build filters
    const filters: CustomerSearchFilters = {};

    if (searchParams.get('email')) {
      filters.email = searchParams.get('email')!;
    }

    if (searchParams.get('name')) {
      filters.name = searchParams.get('name')!;
    }

    if (searchParams.get('tags')) {
      filters.tags = searchParams.get('tags')!.split(',');
    }

    if (searchParams.get('status')) {
      filters.status = searchParams.get('status')!.split(',') as any[];
    }

    if (searchParams.get('source')) {
      filters.source = searchParams.get('source')!.split(',') as any[];
    }

    // Pagination
    const limit = parseInt(searchParams.get('limit') || '50');
    const offset = parseInt(searchParams.get('offset') || '0');
    const sortBy = searchParams.get('sortBy') || 'createdAt';
    const sortOrder = (searchParams.get('sortOrder') || 'desc') as 'asc' | 'desc';

    const result = await searchCustomers(filters, { limit, offset, sortBy, sortOrder });

    return NextResponse.json(result);
  } catch (error) {
    console.error('Error searching customers:', error);
    return NextResponse.json(
      {
        error: 'Failed to search customers',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * POST /api/crm/customers
 * Create new customer or get existing by email
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { getOrCreate, ...customerData } = body;

    // Validate required fields
    if (!customerData.email || !customerData.name) {
      return NextResponse.json(
        { error: 'Missing required fields: email, name' },
        { status: 400 }
      );
    }

    const input: CreateCustomerInput = {
      email: customerData.email,
      name: customerData.name,
      phone: customerData.phone,
      company: customerData.company,
      address: customerData.address,
      tags: customerData.tags || [],
      source: customerData.source || 'manual',
      status: customerData.status || 'lead',
      customFields: customerData.customFields,
    };

    // Get or create customer based on flag
    const customer = getOrCreate
      ? await getOrCreateCustomer(input)
      : await createCustomer(input);

    return NextResponse.json({
      success: true,
      customer,
    });
  } catch (error) {
    console.error('Error creating customer:', error);
    return NextResponse.json(
      {
        error: 'Failed to create customer',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
