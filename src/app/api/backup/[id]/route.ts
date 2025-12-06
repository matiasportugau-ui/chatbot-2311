import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const backupId = params.id;
    
    // Get backup metadata (would need to read from backup_metadata directory)
    // For now, return placeholder
    return NextResponse.json({
      success: true,
      data: {
        backup_id: backupId,
        // Would load actual metadata here
      }
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const backupId = params.id;
    const body = await request.json();
    const { action } = body;

    if (action === 'verify') {
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'backup.py')} verify ${backupId} --config backup_system/backup_config.json`
      );
      
      return NextResponse.json({
        success: true,
        data: stdout
      });
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const backupId = params.id;
    
    const { stdout } = await execAsync(
      `python3 ${path.join(process.cwd(), 'backup.py')} delete ${backupId} --config backup_system/backup_config.json`
    );
    
    return NextResponse.json({
      success: true,
      message: `Backup ${backupId} deleted`
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}


