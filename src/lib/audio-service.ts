export interface AudioTranscriptionOptions {
  model?: string;
  prompt?: string;
  response_format?: 'json' | 'text' | 'srt' | 'verbose_json' | 'vtt';
  language?: string;
  temperature?: number;
  timestamp_granularities?: ('word' | 'segment')[];
  chunking_strategy?: string;
  known_speaker_names?: string[];
  known_speaker_references?: string[];
}

export interface AudioTranslationOptions {
  model?: string;
  prompt?: string;
  response_format?: 'json' | 'text' | 'srt' | 'verbose_json' | 'vtt';
  temperature?: number;
}

export async function transcribeAudio(file: File, options: AudioTranscriptionOptions = {}) {
  const formData = new FormData();
  formData.append('file', file);
  
  if (options.model) formData.append('model', options.model);
  if (options.prompt) formData.append('prompt', options.prompt);
  if (options.response_format) formData.append('response_format', options.response_format);
  if (options.language) formData.append('language', options.language);
  if (options.temperature !== undefined) formData.append('temperature', options.temperature.toString());
  if (options.timestamp_granularities) {
    options.timestamp_granularities.forEach(g => formData.append('timestamp_granularities[]', g));
  }
  if (options.chunking_strategy) formData.append('chunking_strategy', options.chunking_strategy);
  if (options.known_speaker_names) {
    options.known_speaker_names.forEach(n => formData.append('known_speaker_names[]', n));
  }
  if (options.known_speaker_references) {
    options.known_speaker_references.forEach(r => formData.append('known_speaker_references[]', r));
  }

  const response = await fetch('/api/audio/transcribe', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || 'Transcription failed');
  }

  return response.json();
}

export async function translateAudio(file: File, options: AudioTranslationOptions = {}) {
  const formData = new FormData();
  formData.append('file', file);

  if (options.model) formData.append('model', options.model);
  if (options.prompt) formData.append('prompt', options.prompt);
  if (options.response_format) formData.append('response_format', options.response_format);
  if (options.temperature !== undefined) formData.append('temperature', options.temperature.toString());

  const response = await fetch('/api/audio/translate', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || 'Translation failed');
  }

  return response.json();
}
