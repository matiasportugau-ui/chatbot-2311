import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action') || 'list';

    if (action === 'list') {
      // List recent autosaves
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'backup_system/autosave.py')} --list --config backup_system/backup_config.json`
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

export async function POST(request: NextRequest) {
  try {
    // Create autosave now
    const { stdout } = await execAsync(
      `python3 ${path.join(process.cwd(), 'backup_system/autosave.py')} --create --config backup_system/backup_config.json`
    );
    
    return NextResponse.json({
      success: true,
      data: JSON.parse(stdout)
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

