export const dynamic = 'force-dynamic'
export const runtime = 'nodejs'

import { NextRequest, NextResponse } from 'next/server'
import { OpenAI } from 'openai'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

function asString(value: FormDataEntryValue | null): string | undefined {
  if (typeof value !== 'string') return undefined
  const trimmed = value.trim()
  return trimmed ? trimmed : undefined
}

function asBoolean(value: FormDataEntryValue | null): boolean | undefined {
  const s = asString(value)
  if (!s) return undefined
  if (s === 'true' || s === '1' || s === 'yes' || s === 'on') return true
  if (s === 'false' || s === '0' || s === 'no' || s === 'off') return false
  return undefined
}

function asStringArrayFromJson(value: FormDataEntryValue | null): string[] | undefined {
  const s = asString(value)
  if (!s) return undefined
  try {
    const parsed = JSON.parse(s)
    if (!Array.isArray(parsed)) return undefined
    if (!parsed.every(v => typeof v === 'string')) return undefined
    return parsed
  } catch {
    return undefined
  }
}

export async function POST(request: NextRequest) {
  try {
    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json(
        { success: false, error: 'OPENAI_API_KEY is not configured' },
        { status: 500 }
      )
    }

    const form = await request.formData()

    const file = form.get('file')
    if (!(file instanceof File)) {
      return NextResponse.json(
        { success: false, error: 'file is required (multipart/form-data)' },
        { status: 400 }
      )
    }

    const mode = (asString(form.get('mode')) || 'transcribe') as
      | 'transcribe'
      | 'translate'

    // Defaults:
    // - transcribe: gpt-4o-mini-transcribe (fast/cheap)
    // - translate: whisper-1 (only model supported by /translations)
    const model =
      asString(form.get('model')) ||
      (mode === 'translate' ? 'whisper-1' : 'gpt-4o-mini-transcribe')

    const response_format = asString(form.get('response_format'))
    const prompt = asString(form.get('prompt'))
    const language = asString(form.get('language'))

    // Whisper-only options
    const timestamp_granularities = asStringArrayFromJson(
      form.get('timestamp_granularities')
    ) as Array<'word' | 'segment'> | undefined

    // Diarization / chunking
    const chunking_strategy = asString(form.get('chunking_strategy')) || 'auto'
    const known_speaker_names = asStringArrayFromJson(form.get('known_speaker_names'))
    const known_speaker_references = asStringArrayFromJson(
      form.get('known_speaker_references')
    )

    // Logprobs (supported by gpt-4o-* transcribe models)
    const include_logprobs = asBoolean(form.get('include_logprobs')) || false

    if (mode === 'translate') {
      const translation = await openai.audio.translations.create({
        model: 'whisper-1',
        file,
        ...(response_format ? { response_format } : {}),
        ...(prompt ? { prompt } : {}),
      })

      return NextResponse.json({
        success: true,
        mode,
        model: 'whisper-1',
        result: translation,
      })
    }

    const isDiarizeModel = model === 'gpt-4o-transcribe-diarize'
    const isWhisperModel = model === 'whisper-1'
    const isGptTranscribeModel =
      model === 'gpt-4o-transcribe' || model === 'gpt-4o-mini-transcribe'

    const transcription = await openai.audio.transcriptions.create({
      model,
      file,
      ...(response_format ? { response_format } : {}),
      ...(language ? { language } : {}),
      ...(isGptTranscribeModel && prompt ? { prompt } : {}),
      ...(isWhisperModel && prompt ? { prompt } : {}),
      ...(isWhisperModel && timestamp_granularities
        ? {
            response_format: response_format || 'verbose_json',
            timestamp_granularities,
          }
        : {}),
      ...(isDiarizeModel
        ? {
            chunking_strategy,
            extra_body: {
              ...(known_speaker_names ? { known_speaker_names } : {}),
              ...(known_speaker_references ? { known_speaker_references } : {}),
            },
          }
        : {}),
      ...(isGptTranscribeModel && include_logprobs ? { include: ['logprobs'] } : {}),
    })

    return NextResponse.json({
      success: true,
      mode,
      model,
      result: transcription,
    })
  } catch (error) {
    console.error('Error in audio transcribe API:', error)
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    )
  }
}

