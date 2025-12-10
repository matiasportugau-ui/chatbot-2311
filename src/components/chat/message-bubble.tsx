import React from 'react'
import { cn } from '@/lib/utils'
import { Bot, User, Copy, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface MessageBubbleProps {
    role: 'user' | 'assistant' | 'system'
    content: string
    className?: string
}

export function MessageBubble({ role, content, className }: MessageBubbleProps) {
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
                "flex w-full items-start gap-4 p-4",
                isUser ? "flex-row-reverse" : "flex-row",
                className
            )}
        >
            <div
                className={cn(
                    "flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-full border",
                    isUser ? "bg-background" : "bg-primary text-primary-foreground"
                )}
            >
                {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
            </div>

            <div className={cn("flex-1 space-y-2 overflow-hidden", isUser ? "text-right" : "text-left")}>
                <div className={cn(
                    "rounded-lg px-4 py-3 text-sm shadow-sm max-w-[85%] inline-block",
                    isUser ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
                )}>
                    {/* Basic text rendering for now, can upgrade to Markdown later */}
                    <div className="whitespace-pre-wrap">{content}</div>
                </div>

                {!isUser && (
                    <div className="flex items-center gap-2">
                        <Button
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6"
                            onClick={copyToClipboard}
                        >
                            {copied ? (
                                <Check className="h-3 w-3" />
                            ) : (
                                <Copy className="h-3 w-3" />
                            )}
                            <span className="sr-only">Copy message</span>
                        </Button>
                    </div>
                )}
            </div>
        </div>
    )
}
