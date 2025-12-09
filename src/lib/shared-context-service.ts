export interface SessionOptions {
    source?: string
    agent_type?: string
}

export interface MessageOptions {
    intent?: string
    message_type?: string
}

export interface SharedContext {
    session_id: string
    user_phone: string
    intent: string
    messages: any[]
    context_summary: string
    token_count: number
    last_updated: Date
}

class SharedContextService {
    private sessions: Map<string, SharedContext> = new Map()

    constructor() { }

    async createSession(user_phone: string, initial_message: string, options: SessionOptions = {}): Promise<string> {
        const session_id = `sess_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

        this.sessions.set(session_id, {
            session_id,
            user_phone,
            intent: 'greeting',
            messages: [],
            context_summary: '',
            token_count: 0,
            last_updated: new Date()
        })

        return session_id
    }

    async addMessage(session_id: string, message: string, role: string, options: MessageOptions = {}): Promise<void> {
        const session = this.sessions.get(session_id)
        if (session) {
            session.messages.push({
                role,
                content: message,
                timestamp: new Date(),
                ...options
            })
            session.token_count += Math.ceil(message.length / 4)
            session.last_updated = new Date()
            if (options.intent) session.intent = options.intent
        }
    }

    async getContext(session_id: string, user_phone: string): Promise<SharedContext | null> {
        return this.sessions.get(session_id) || null
    }
}

// Singleton instance
const service = new SharedContextService()

export function getSharedContextService() {
    return service
}
