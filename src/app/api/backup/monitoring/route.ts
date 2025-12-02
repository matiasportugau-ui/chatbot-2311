import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execAsync = promisify(exec);

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action') || 'metrics';

    if (action === 'metrics') {
      // Get monitoring metrics
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'backup_system/monitoring.py')} --metrics --config backup_system/backup_config.json`
      );
      
      return NextResponse.json({
        success: true,
        data: JSON.parse(stdout)
      });
    }

    if (action === 'health') {
      // Get health check
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'backup_system/monitoring.py')} --check --config backup_system/backup_config.json`
      );
      
      return NextResponse.json({
        success: true,
        data: JSON.parse(stdout)
      });
    }

    if (action === 'alerts') {
      // Get alerts
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'backup_system/monitoring.py')} --alerts --config backup_system/backup_config.json`
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


