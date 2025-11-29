import { NextResponse } from 'next/server'
import { getGrantStatus, refreshTokens } from '@/lib/mercado-libre/client'

export async function GET() {
  try {
    const status = await getGrantStatus()
    return NextResponse.json(status)
  } catch (error) {
    console.error('Error fetching Mercado Libre grant status:', error)
    return NextResponse.json({ error: 'Unable to fetch Mercado Libre status' }, { status: 500 })
  }
}

export async function POST() {
  try {
    const tokens = await refreshTokens()
    return NextResponse.json({
      success: true,
      expiresIn: tokens.expires_in
    })
  } catch (error) {
    console.error('Error refreshing Mercado Libre token:', error)
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : 'Unable to refresh Mercado Libre token'
      },
      { status: 500 }
    )
  }
}

