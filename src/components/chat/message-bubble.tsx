import React from 'react'
import { cn } from '@/lib/utils'
import { Bot, User, Copy, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import Image from 'next/image'

interface MessageBubbleProps {
    role: 'user' | 'assistant' | 'system'
    content: string
    className?: string
    confidence?: number
}

export function MessageBubble({ role, content, className, ...props }: MessageBubbleProps) {
    const [copied, setCopied] = React.useState(false)

    const copyToClipboard = () => {
        navigator.clipboard.writeText(content)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    const isUser = role === 'user'

    return (
        <div
            className={cn(
                "flex w-full mb-4",
                isUser ? "justify-end" : "justify-start",
                className
            )}
        >
            <div className={cn(
                "speech-bubble",
                isUser ? "user-bubble" : ""
            )}>
                <div className="prose prose-sm dark:prose-invert max-w-none break-words">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {content}
                    </ReactMarkdown>
                </div>

                {/* Metadata footer */}
                <div className="flex items-center gap-3 mt-3 pt-2 border-t border-gray-100">
                    {props.confidence !== undefined && (
                        <div className="confidence-badge">
                            <span className="confidence-indicator"></span>
                            {(props.confidence * 100).toFixed(0)}%
                        </div>
                    )}
                    {!isUser && (
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-7 w-7 ml-auto"
                            onClick={copyToClipboard}
                        >
                            {copied ? (
                                <Check className="h-3 w-3" />
                            ) : (
                                <Copy className="h-3 w-3" />
                            )}
                            <span className="sr-only">Copy message</span>
                        </Button>
                    )}
                </div>
            </div>
        </div>
    )
}
