import { NextRequest, NextResponse } from 'next/server';
import { createNote, getCustomerNotes, updateNote, deleteNote, type CreateNoteInput } from '@/lib/crm';

/**
 * POST /api/crm/notes
 * Create new note
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    if (!body.customerId || !body.content) {
      return NextResponse.json(
        { error: 'Missing required fields: customerId, content' },
        { status: 400 }
      );
    }

    const input: CreateNoteInput = {
      customerId: body.customerId,
      content: body.content,
      isPinned: body.isPinned || false,
      tags: body.tags || [],
    };

    const note = await createNote(input);

    return NextResponse.json({
      success: true,
      note,
    });
  } catch (error) {
    console.error('Error creating note:', error);
    return NextResponse.json(
      {
        error: 'Failed to create note',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/crm/notes?customerId=xxx
 * Get customer notes
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const customerId = searchParams.get('customerId');

    if (!customerId) {
      return NextResponse.json({ error: 'Missing customerId parameter' }, { status: 400 });
    }

    const notes = await getCustomerNotes(customerId);

    return NextResponse.json({
      notes,
      total: notes.length,
    });
  } catch (error) {
    console.error('Error getting notes:', error);
    return NextResponse.json(
      {
        error: 'Failed to get notes',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * PATCH /api/crm/notes?id=xxx
 * Update note
 */
export async function PATCH(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const noteId = searchParams.get('id');

    if (!noteId) {
      return NextResponse.json({ error: 'Missing id parameter' }, { status: 400 });
    }

    const body = await request.json();
    const note = await updateNote(noteId, {
      content: body.content,
      isPinned: body.isPinned,
      tags: body.tags,
    });

    if (!note) {
      return NextResponse.json({ error: 'Note not found' }, { status: 404 });
    }

    return NextResponse.json({
      success: true,
      note,
    });
  } catch (error) {
    console.error('Error updating note:', error);
    return NextResponse.json(
      {
        error: 'Failed to update note',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/crm/notes?id=xxx
 * Delete note
 */
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const noteId = searchParams.get('id');

    if (!noteId) {
      return NextResponse.json({ error: 'Missing id parameter' }, { status: 400 });
    }

    await deleteNote(noteId);

    return NextResponse.json({
      success: true,
      message: 'Note deleted successfully',
    });
  } catch (error) {
    console.error('Error deleting note:', error);
    return NextResponse.json(
      {
        error: 'Failed to delete note',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
