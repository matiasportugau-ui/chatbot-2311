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

type AudioResponseFormat =
  | 'json'
  | 'text'
  | 'srt'
  | 'verbose_json'
  | 'vtt'
  | 'diarized_json'

function getExtension(filename: string): string | null {
  const idx = filename.lastIndexOf('.')
  if (idx === -1) return null
  return filename.slice(idx + 1).toLowerCase()
}

function asOptionalString(v: FormDataEntryValue | null): string | undefined {
  if (v == null) return undefined
  if (typeof v !== 'string') return undefined
  const s = v.trim()
  return s.length ? s : undefined
}

function getAllStrings(fd: FormData, key: string): string[] {
  return fd
    .getAll(key)
    .filter((v): v is string => typeof v === 'string')
    .map(v => v.trim())
    .filter(Boolean)
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

    const model =
      asOptionalString(formData.get('model')) ?? 'gpt-4o-transcribe'

    const responseFormatRaw = asOptionalString(formData.get('response_format'))
    const response_format = (responseFormatRaw || undefined) as
      | AudioResponseFormat
      | undefined
    const prompt = asOptionalString(formData.get('prompt'))
    const language = asOptionalString(formData.get('language'))
    const chunking_strategy = asOptionalString(formData.get('chunking_strategy'))

    // Speaker diarization extras (optional)
    const knownSpeakerNames = [
      ...getAllStrings(formData, 'known_speaker_names[]'),
      ...getAllStrings(formData, 'known_speaker_names'),
    ]
    const knownSpeakerReferences = [
      ...getAllStrings(formData, 'known_speaker_references[]'),
      ...getAllStrings(formData, 'known_speaker_references'),
    ]

    const isDiarizeModel = model === 'gpt-4o-transcribe-diarize'
    if (isDiarizeModel && knownSpeakerNames.length !== knownSpeakerReferences.length) {
      return errorResponse(
        'known_speaker_names and known_speaker_references must have the same length',
        400
      )
    }

    // For diarization, set a safe default so longer files work out-of-the-box.
    const diarizeChunking =
      isDiarizeModel && chunking_strategy && chunking_strategy !== 'auto'
        ? null
        : isDiarizeModel
          ? 'auto'
          : undefined

    if (isDiarizeModel && chunking_strategy && chunking_strategy !== 'auto') {
      return errorResponse(
        'Only chunking_strategy="auto" is supported by this endpoint (server_vad config not implemented here)',
        400
      )
    }

    const transcript = await openai.audio.transcriptions.create({
      file,
      model,
      stream: false,
      ...(response_format ? { response_format } : {}),
      ...(prompt ? { prompt } : {}),
      ...(language ? { language } : {}),
      ...(isDiarizeModel ? { chunking_strategy: diarizeChunking } : {}),
      ...(isDiarizeModel && (knownSpeakerNames.length || knownSpeakerReferences.length)
        ? {
            known_speaker_names: knownSpeakerNames.slice(0, 4),
            known_speaker_references: knownSpeakerReferences.slice(0, 4),
          }
        : {}),
    })

    return successResponse(
      {
        model,
        filename: file.name,
        bytes: file.size,
        transcript,
      },
      'Transcription created'
    )
  } catch (error) {
    console.error('Audio transcribe API error:', error)
    return errorResponse(
      error instanceof Error ? error.message : 'Unknown error',
      500
    )
  }
}

