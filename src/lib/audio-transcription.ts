import OpenAI from "openai";
import * as fs from "fs";

// Initialize OpenAI client
// Ensure OPENAI_API_KEY is set in environment variables
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export type TranscriptionModel = "whisper-1" | "gpt-4o-transcribe" | "gpt-4o-mini-transcribe";

/**
 * Transcribe an audio file using OpenAI's Audio API
 * NOTE: This function is intended to be run on the server side (Node.js).
 */
export async function transcribeAudio(
  filePath: string,
  model: TranscriptionModel = "gpt-4o-transcribe",
  prompt?: string
) {
  try {
    const transcription = await openai.audio.transcriptions.create({
      file: fs.createReadStream(filePath),
      model: model,
      prompt: prompt,
      response_format: "json",
    });

    return transcription;
  } catch (error) {
    console.error("Error transcribing audio:", error);
    throw error;
  }
}

/**
 * Transcribe an audio file with speaker diarization
 * NOTE: This function is intended to be run on the server side (Node.js).
 */
export async function transcribeWithDiarization(
  filePath: string,
  chunkingStrategy: "auto" = "auto"
) {
  try {
    // Cast to any because the type definitions might not be fully updated for the new model/params yet
    // but the library supports it if it's recent enough.
    const transcript = await openai.audio.transcriptions.create({
      file: fs.createReadStream(filePath),
      model: "gpt-4o-transcribe-diarize",
      response_format: "diarized_json" as any, 
      chunking_strategy: chunkingStrategy as any,
    } as any);

    return transcript;
  } catch (error) {
    console.error("Error diarizing audio:", error);
    throw error;
  }
}

/**
 * Translate an audio file to English
 * NOTE: This function is intended to be run on the server side (Node.js).
 */
export async function translateAudio(filePath: string) {
  try {
    const translation = await openai.audio.translations.create({
      file: fs.createReadStream(filePath),
      model: "whisper-1",
    });

    return translation;
  } catch (error) {
    console.error("Error translating audio:", error);
    throw error;
  }
}
