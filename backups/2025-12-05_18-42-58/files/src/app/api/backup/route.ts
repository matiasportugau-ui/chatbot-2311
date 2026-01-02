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
      // List all backups
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'backup.py')} list --config backup_system/backup_config.json`
      );
      
      // Parse output (simplified - would need proper parsing)
      return NextResponse.json({
        success: true,
        data: stdout
      });
    }

    if (action === 'storage') {
      // Get storage usage
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'backup.py')} storage --config backup_system/backup_config.json`
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
    const body = await request.json();
    const { action, type, scope } = body;

    if (action === 'create') {
      const scopeArg = scope ? `--scope ${scope.join(',')}` : '';
      const typeArg = type === 'incremental' ? '--incremental' : '--full';
      
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'backup.py')} create ${typeArg} ${scopeArg} --config backup_system/backup_config.json`
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


