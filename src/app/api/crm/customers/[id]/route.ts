import { NextRequest, NextResponse } from 'next/server';
import {
  getCustomerById,
  getCustomerWithRelations,
  updateCustomer,
  deleteCustomer,
  type UpdateCustomerInput,
} from '@/lib/crm';

/**
 * GET /api/crm/customers/[id]
 * Get customer by ID with optional relations
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { searchParams } = new URL(request.url);
    const includeRelations = searchParams.get('includeRelations') === 'true';

    const customer = includeRelations
      ? await getCustomerWithRelations(params.id)
      : await getCustomerById(params.id);

    if (!customer) {
      return NextResponse.json({ error: 'Customer not found' }, { status: 404 });
    }

    return NextResponse.json(customer);
  } catch (error) {
    console.error('Error getting customer:', error);
    return NextResponse.json(
      {
        error: 'Failed to get customer',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * PATCH /api/crm/customers/[id]
 * Update customer
 */
export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();

    const input: UpdateCustomerInput = {
      name: body.name,
      phone: body.phone,
      company: body.company,
      address: body.address,
      tags: body.tags,
      status: body.status,
      customFields: body.customFields,
    };

    const customer = await updateCustomer(params.id, input);

    if (!customer) {
      return NextResponse.json({ error: 'Customer not found' }, { status: 404 });
    }

    return NextResponse.json({
      success: true,
      customer,
    });
  } catch (error) {
    console.error('Error updating customer:', error);
    return NextResponse.json(
      {
        error: 'Failed to update customer',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/crm/customers/[id]
 * Delete customer and all related data
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await deleteCustomer(params.id);

    return NextResponse.json({
      success: true,
      message: 'Customer and related data deleted successfully',
    });
  } catch (error) {
    console.error('Error deleting customer:', error);
    return NextResponse.json(
      {
        error: 'Failed to delete customer',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
