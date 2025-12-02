import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action') || 'scan';
    const source = searchParams.get('source') || 'all';

    if (action === 'scan') {
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'recover.py')} scan --source ${source} --config backup_system/backup_config.json`
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
    const { action, backup_id, scope, selective, dry_run, conflict_resolution } = body;

    if (action === 'restore') {
      const scopeArg = scope ? `--scope ${scope.join(',')}` : '';
      const selectiveArg = selective ? `--selective ${selective.join(',')}` : '';
      const dryRunArg = dry_run ? '--dry-run' : '';
      const conflictArg = conflict_resolution ? `--conflict-resolution ${conflict_resolution}` : '';
      
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'recover.py')} restore ${backup_id} ${scopeArg} ${selectiveArg} ${dryRunArg} ${conflictArg} --config backup_system/backup_config.json`
      );
      
      return NextResponse.json({
        success: true,
        data: stdout
      });
    }

    if (action === 'preview') {
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'recover.py')} preview ${backup_id} --config backup_system/backup_config.json`
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
