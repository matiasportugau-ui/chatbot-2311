import OpenAI from "openai";
import fs from "fs";
import { secureConfig } from './secure-config';

export async function transcribeAudio(filePath: string): Promise<string> {
  // Ensure we get the latest config
  const config = secureConfig.getOpenAIConfig();
  
  // If not initialized, apiKey might be empty/undefined if environment vars weren't picked up 
  // (though secureConfig tries to load from env vars if file missing).
  // But if secureConfig.isReady() is false, getOpenAIConfig() throws "not loaded" from ensureLoaded().
  // So we rely on the caller to ensure secureConfig is initialized.
  
  if (!config.apiKey) {
      throw new Error("OpenAI API Key not configured");
  }

  const openai = new OpenAI({
    apiKey: config.apiKey,
  });

  try {
    const transcription = await openai.audio.transcriptions.create({
      file: fs.createReadStream(filePath),
      model: "gpt-4o-transcribe",
    });

    return transcription.text;
  } catch (error) {
    console.error("Error transcribing audio:", error);
    throw error;
  }
}
