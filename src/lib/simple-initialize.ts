/**
 * Simple System Initialization
 * Provides basic system status and initialization functions
 */

export interface SystemStatus {
  initialized: boolean
  timestamp: string
  version?: string
}

let systemInitialized = false
let initializationTimestamp: string | null = null

/**
 * Initialize the simple system
 * @returns Promise with initialization result
 */
export async function initializeSimpleSystem(): Promise<{
  success: boolean
  timestamp: string
}> {
  if (!systemInitialized) {
    systemInitialized = true
    initializationTimestamp = new Date().toISOString()
  }

  return {
    success: true,
    timestamp: initializationTimestamp || new Date().toISOString(),
  }
}

/**
 * Get current system status
 * @returns System status object
 */
export function getSystemStatus(): SystemStatus {
  return {
    initialized: systemInitialized,
    timestamp: initializationTimestamp || new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
  }
}

