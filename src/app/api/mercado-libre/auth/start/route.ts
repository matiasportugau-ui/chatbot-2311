import { NextRequest, NextResponse } from 'next/server'
import { startAuthorization } from '@/lib/mercado-libre/client'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}))
    const { returnTo } = body || {}
    const result = await startAuthorization(typeof returnTo === 'string' ? returnTo : undefined)
    return NextResponse.json(result)
  } catch (error) {
    console.error('Error initiating Mercado Libre OAuth:', error)
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}

