'use client'

import React, { useMemo, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

type Mode = 'transcribe' | 'translate'

export function SpeechToText() {
  const [mode, setMode] = useState<Mode>('transcribe')
  const [model, setModel] = useState<string>('gpt-4o-mini-transcribe')
  const [responseFormat, setResponseFormat] = useState<string>('json')
  const [prompt, setPrompt] = useState<string>('')
  const [language, setLanguage] = useState<string>('')
  const [includeLogprobs, setIncludeLogprobs] = useState<boolean>(false)
  const [chunkingStrategy, setChunkingStrategy] = useState<string>('auto')
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const isDiarize = model === 'gpt-4o-transcribe-diarize'

  const responseFormatOptions = useMemo(() => {
    if (mode === 'translate') return ['json', 'text', 'srt', 'vtt', 'verbose_json']
    if (model === 'whisper-1') return ['json', 'text', 'srt', 'vtt', 'verbose_json']
    if (isDiarize) return ['diarized_json', 'json', 'text']
    return ['json', 'text']
  }, [isDiarize, mode, model])

  async function onSubmit() {
    setError(null)
    setResult(null)
    if (!file) {
      setError('Selecciona un archivo de audio primero.')
      return
    }

    setLoading(true)
    try {
      const fd = new FormData()
      fd.append('file', file)
      fd.append('mode', mode)
      fd.append('model', mode === 'translate' ? 'whisper-1' : model)
      if (responseFormat) fd.append('response_format', responseFormat)
      if (prompt.trim()) fd.append('prompt', prompt.trim())
      if (language.trim()) fd.append('language', language.trim())
      if (includeLogprobs) fd.append('include_logprobs', 'true')
      if (isDiarize) fd.append('chunking_strategy', chunkingStrategy)

      const res = await fetch('/api/audio/transcribe', {
        method: 'POST',
        body: fd,
      })

      const json = await res.json()
      if (!res.ok || !json?.success) {
        throw new Error(json?.error || `Request failed (${res.status})`)
      }
      setResult(json)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Error desconocido')
    } finally {
      setLoading(false)
    }
  }

  const transcriptText =
    result?.result?.text ??
    (typeof result?.result === 'string' ? result.result : undefined)

  const diarizedSegments: Array<any> | undefined = result?.result?.segments

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Speech to Text</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Modo</label>
              <select
                className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                value={mode}
                onChange={e => {
                  const nextMode = e.target.value as Mode
                  setMode(nextMode)
                  if (nextMode === 'translate') {
                    setModel('whisper-1')
                    setResponseFormat('json')
                    setIncludeLogprobs(false)
                  }
                }}
              >
                <option value="transcribe">Transcribir (mismo idioma)</option>
                <option value="translate">Traducir a inglés (whisper-1)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Modelo</label>
              <select
                className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                value={mode === 'translate' ? 'whisper-1' : model}
                onChange={e => {
                  setModel(e.target.value)
                  setIncludeLogprobs(false)
                }}
                disabled={mode === 'translate'}
              >
                <option value="gpt-4o-mini-transcribe">gpt-4o-mini-transcribe</option>
                <option value="gpt-4o-transcribe">gpt-4o-transcribe</option>
                <option value="gpt-4o-transcribe-diarize">gpt-4o-transcribe-diarize</option>
                <option value="whisper-1">whisper-1</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Response format</label>
              <select
                className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                value={responseFormat}
                onChange={e => setResponseFormat(e.target.value)}
              >
                {responseFormatOptions.map(opt => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Idioma (opcional)</label>
              <Input
                value={language}
                onChange={e => setLanguage(e.target.value)}
                placeholder='Ej: "es" o "en"'
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Prompt (opcional)</label>
              <Input
                value={prompt}
                onChange={e => setPrompt(e.target.value)}
                placeholder="Contexto para mejorar la transcripción (siglas, nombres, etc.)"
                disabled={isDiarize}
              />
              {isDiarize && (
                <p className="text-xs text-muted-foreground mt-1">
                  Nota: diarization no soporta prompt/logprobs.
                </p>
              )}
            </div>
          </div>

          <div className="flex flex-col md:flex-row gap-4 md:items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-1">Archivo</label>
              <Input
                type="file"
                accept=".mp3,.mp4,.mpeg,.mpga,.m4a,.wav,.webm"
                onChange={e => setFile(e.target.files?.[0] || null)}
              />
            </div>

            {isDiarize && (
              <div className="w-full md:w-56">
                <label className="block text-sm font-medium mb-1">Chunking</label>
                <select
                  className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                  value={chunkingStrategy}
                  onChange={e => setChunkingStrategy(e.target.value)}
                >
                  <option value="auto">auto</option>
                </select>
              </div>
            )}

            {!isDiarize && mode === 'transcribe' && (model === 'gpt-4o-transcribe' || model === 'gpt-4o-mini-transcribe') && (
              <label className="flex items-center gap-2 text-sm select-none">
                <input
                  type="checkbox"
                  checked={includeLogprobs}
                  onChange={e => setIncludeLogprobs(e.target.checked)}
                />
                Include logprobs
              </label>
            )}

            <Button onClick={onSubmit} disabled={loading || !file}>
              {loading ? 'Procesando…' : 'Transcribir'}
            </Button>
          </div>

          {error && <div className="text-sm text-red-600">{error}</div>}
        </CardContent>
      </Card>

      {(transcriptText || diarizedSegments || result) && (
        <Card>
          <CardHeader>
            <CardTitle>Resultado</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {transcriptText && (
              <div>
                <div className="text-sm font-medium mb-2">Texto</div>
                <pre className="whitespace-pre-wrap rounded-md border p-3 text-sm bg-muted/30">
                  {transcriptText}
                </pre>
              </div>
            )}

            {Array.isArray(diarizedSegments) && diarizedSegments.length > 0 && (
              <div>
                <div className="text-sm font-medium mb-2">Segmentos (diarization)</div>
                <div className="space-y-2">
                  {diarizedSegments.map((seg, idx) => (
                    <div key={idx} className="rounded-md border p-3 text-sm">
                      <div className="font-medium">
                        {seg.speaker ?? 'speaker'}{' '}
                        <span className="font-normal text-muted-foreground">
                          {typeof seg.start === 'number' && typeof seg.end === 'number'
                            ? `(${seg.start.toFixed?.(2) ?? seg.start}–${seg.end.toFixed?.(2) ?? seg.end}s)`
                            : ''}
                        </span>
                      </div>
                      <div className="mt-1 whitespace-pre-wrap">{seg.text}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result && (
              <div>
                <div className="text-sm font-medium mb-2">Raw JSON</div>
                <pre className="overflow-auto rounded-md border p-3 text-xs bg-muted/30">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

