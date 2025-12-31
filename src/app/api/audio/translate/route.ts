export const dynamic = 'force-dynamic'
export const runtime = 'nodejs'

import { errorResponse, successResponse } from '@/lib/api-response'
import { OpenAI } from 'openai'

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })

const MAX_FILE_BYTES = 25 * 1024 * 1024
const SUPPORTED_EXTENSIONS = new Set([
  'mp3',
  'mp4',
  'mpeg',
  'mpga',
  'm4a',
  'wav',
  'webm',
])

function getExtension(filename: string): string | null {
  const idx = filename.lastIndexOf('.')
  if (idx === -1) return null
  return filename.slice(idx + 1).toLowerCase()
}

export async function POST(request: Request) {
  try {
    if (!process.env.OPENAI_API_KEY) {
      return errorResponse('OPENAI_API_KEY is not configured', 500)
    }

    const formData = await request.formData()

    const file = formData.get('file')
    if (!(file instanceof File)) {
      return errorResponse('Missing audio file field "file"', 400)
    }

    if (file.size <= 0) {
      return errorResponse('Uploaded file is empty', 400)
    }

    if (file.size > MAX_FILE_BYTES) {
      return errorResponse('File too large (max 25 MB)', 413)
    }

    const ext = getExtension(file.name)
    if (!ext || !SUPPORTED_EXTENSIONS.has(ext)) {
      return errorResponse(
        `Unsupported file type. Supported: ${Array.from(SUPPORTED_EXTENSIONS).join(', ')}`,
        400
      )
    }

    // Per OpenAI docs, translations currently support only whisper-1.
    const translation = await openai.audio.translations.create({
      file,
      model: 'whisper-1',
    })

    return successResponse(
      {
        model: 'whisper-1',
        filename: file.name,
        bytes: file.size,
        translation,
      },
      'Translation created'
    )
  } catch (error) {
    console.error('Audio translate API error:', error)
    return errorResponse(
      error instanceof Error ? error.message : 'Unknown error',
      500
    )
  }
}

