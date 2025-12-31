import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(req: NextRequest) {
  if (!process.env.OPENAI_API_KEY) {
    return NextResponse.json(
      { error: 'OpenAI API key not configured' },
      { status: 500 }
    );
  }

  try {
    const formData = await req.formData();
    const file = formData.get('file') as File;
    const model = (formData.get('model') as string) || 'whisper-1';
    const prompt = formData.get('prompt') as string | null;
    const responseFormat = formData.get('response_format') as string | null;
    const language = formData.get('language') as string | null;
    const timestampGranularities = formData.getAll('timestamp_granularities[]') as string[];
    const chunkingStrategy = formData.get('chunking_strategy') as string | null;
    const knownSpeakerNames = formData.getAll('known_speaker_names[]') as string[];
    const knownSpeakerReferences = formData.getAll('known_speaker_references[]') as string[];

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // OpenAI Node SDK supports File objects directly in recent versions
    const transcriptionParams: any = {
      file: file,
      model: model,
    };

    if (prompt) transcriptionParams.prompt = prompt;
    if (responseFormat) transcriptionParams.response_format = responseFormat;
    if (language) transcriptionParams.language = language;
    if (timestampGranularities.length > 0) {
      transcriptionParams.timestamp_granularities = timestampGranularities;
    }
    if (chunkingStrategy) {
      transcriptionParams.chunking_strategy = chunkingStrategy;
    }
    
    // Handle extra body parameters for diarization if present
    if (knownSpeakerNames.length > 0 || knownSpeakerReferences.length > 0) {
      transcriptionParams.extra_body = {
        ...transcriptionParams.extra_body,
      };
      
      if (knownSpeakerNames.length > 0) {
        transcriptionParams.extra_body.known_speaker_names = knownSpeakerNames;
      }
      if (knownSpeakerReferences.length > 0) {
        transcriptionParams.extra_body.known_speaker_references = knownSpeakerReferences;
      }
    }

    const transcription = await openai.audio.transcriptions.create(transcriptionParams);

    return NextResponse.json(transcription);
  } catch (error: any) {
    console.error('Transcription error:', error);
    return NextResponse.json(
      { error: error.message || 'Error processing audio' },
      { status: 500 }
    );
  }
}
