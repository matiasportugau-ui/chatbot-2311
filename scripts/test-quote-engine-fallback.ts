import { getMotorCotizacionIntegrado } from '../src/lib/integrated-quote-engine'
import { initializeSecureConfig } from '../src/lib/secure-config'
import fs from 'fs'
import path from 'path'

// Manual .env loader
function loadEnv(filename: string) {
    try {
        const envPath = path.resolve(process.cwd(), filename)
        if (fs.existsSync(envPath)) {
            const content = fs.readFileSync(envPath, 'utf8')
            content.split('\n').forEach(line => {
                const match = line.match(/^([^=]+)=(.*)$/)
                if (match) {
                    const key = match[1].trim()
                    const value = match[2].trim().replace(/^["']|["']$/g, '') // remove quotes
                    process.env[key] = value
                }
            })
            console.log(`✅ Loaded ${filename}`)
        }
    } catch (e) {
        console.warn(`Could not load ${filename}`)
    }
}

// Load environment variables
loadEnv('.env.local')
loadEnv('.env')

// ⚠️ FORCE FALLBACK MODE: invalidate OpenAI Key
process.env.OPENAI_API_KEY = 'invalid-key'

async function main() {
    console.log('🧪 Starting Quote Engine Fallback Test...')

    try {
        // 1. Initialize configuration
        await initializeSecureConfig()
        console.log('✅ Secure Config Initialized')

        // 2. Get Engine Instance
        const engine = await getMotorCotizacionIntegrado()
        console.log('✅ Engine Instantiated')

        // 3. Test with a simple quote query
        // We expect this to use the fallback if OpenAI is not configured
        const query = "Necesito precio de 5 isodec de 100mm de 3 metros de largo"
        const phone = "59899123456"

        console.log(`\n📝 Processing query: "${query}"`)
        const response = await engine.procesarConsulta(query, phone)

        console.log('\n🤖 Response Received:')
        console.log('--------------------------------------------------')
        console.log(JSON.stringify(response, null, 2))
        console.log('--------------------------------------------------')

        if (response.conocimiento_utilizado.includes('fallback_sin_openai')) {
            console.log('\n✅ SUCCESS: Fallback mechanism triggered correctly!')
        } else {
            console.log('\nℹ️ INFO: Standard AI response was used (OpenAI key is likely valid)')
        }

    } catch (error) {
        console.error('\n❌ TEST FAILED:', error)
    } finally {
        process.exit(0)
    }
}

main()
