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
    const temperature = formData.get('temperature') ? Number(formData.get('temperature')) : undefined;

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    const translationParams: any = {
      file: file,
      model: model,
    };

    if (prompt) translationParams.prompt = prompt;
    if (responseFormat) translationParams.response_format = responseFormat;
    if (temperature !== undefined) translationParams.temperature = temperature;

    const translation = await openai.audio.translations.create(translationParams);

    return NextResponse.json(translation);
  } catch (error: any) {
    console.error('Translation error:', error);
    return NextResponse.json(
      { error: error.message || 'Error processing audio translation' },
      { status: 500 }
    );
  }
}
