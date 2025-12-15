import { initializeSecureConfig, secureConfig } from '../lib/secure-config';
import { OpenAI } from 'openai';

async function testXAI() {
    await initializeSecureConfig();

    const config = secureConfig.getOpenAIConfig();
    console.log('🔍 Configuration detected:');
    console.log('   Base URL:', config.baseURL);
    console.log('   Model:', config.model);
    console.log('   API Key present:', !!config.apiKey);

    if (!config.baseURL.includes('x.ai')) {
        console.warn('⚠️ WARNING: Not using xAI Base URL. Ensure XAI_API_KEY is set.');
    }

    const client = new OpenAI({
        apiKey: config.apiKey,
        baseURL: config.baseURL
    });

    try {
        console.log('🚀 Sending test request to xAI...');
        const completion = await client.chat.completions.create({
            model: config.model,
            messages: [
                { role: 'system', content: 'You are a helpful assistant.' },
                { role: 'user', content: 'Hello, are you running on Grok?' }
            ],
            max_tokens: 50
        });

        console.log('✅ Response received:');
        console.log(completion.choices[0].message.content);
    } catch (error: any) {
        console.error('❌ Error connecting to AI provider:', error.message);
        if (error.response) {
            console.error('   Status:', error.response.status);
            console.error('   Data:', error.response.data);
        }
    }
}

testXAI();
