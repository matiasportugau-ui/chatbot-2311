
import { decodePubSubMessage } from './src/lib/google-pubsub';

const mockData = {
    test: "hello world",
    shopifyId: 12345
};

const base64Data = Buffer.from(JSON.stringify(mockData)).toString('base64');

console.log('Mock Base64:', base64Data);

const decoded = decodePubSubMessage(base64Data);
console.log('Decoded:', decoded);

if (decoded.test === "hello world" && decoded.shopifyId === 12345) {
    console.log('✅ Decoding test passed');
} else {
    console.error('❌ Decoding test failed');
    process.exit(1);
}
