export interface SessionOptions {
    source?: string
    agent_type?: string
}

export interface MessageOptions {
    intent?: string
    message_type?: string
}

export interface Message {
    role: string
    content: string
    timestamp: Date
    intent?: string
    message_type?: string
}

export interface SharedContext {
    session_id: string
    user_phone: string
    intent: string
    messages: Message[]
    context_summary: string
    token_count: number
    last_updated: Date
    // Allow extra properties for compatibility
    quote_state?: any
    entities?: any
}

export type ConversationContext = SharedContext

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

    async addMessage(session_id: string, message: string, role: string, options: MessageOptions = {}): Promise<boolean> {
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
            return true
        }
        return false
    }

    async getContext(session_id: string, user_phone: string): Promise<SharedContext | null> {
        return this.sessions.get(session_id) || null
    }

    async getSession(session_id: string): Promise<SharedContext | null> {
        return this.sessions.get(session_id) || null
    }

    async saveContext(session_id: string, context: SharedContext): Promise<boolean> {
        this.sessions.set(session_id, context)
        return true
    }

    async listSessions(user_phone?: string, limit: number = 50): Promise<SharedContext[]> {
        let sessions = Array.from(this.sessions.values())
        if (user_phone) {
            sessions = sessions.filter(s => s.user_phone === user_phone)
        }
        return sessions.slice(0, limit)
    }
}

// Singleton instance
const service = new SharedContextService()

export function getSharedContextService() {
    return service
}
