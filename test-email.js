/**
 * Email Service Smoke Test
 * Tests all email endpoints to verify email integration
 */

const BASE_URL = 'http://localhost:3000';

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function testEndpoint(name, method, path, body = null) {
  try {
    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`${BASE_URL}${path}`, options);
    const data = await response.json();

    if (response.ok) {
      log(`✓ ${name}`, 'green');
      return { success: true, data };
    } else {
      log(`✗ ${name} - ${data.error || data.message || 'Unknown error'}`, 'red');
      return { success: false, error: data };
    }
  } catch (error) {
    log(`✗ ${name} - ${error.message}`, 'red');
    return { success: false, error: error.message };
  }
}

async function runTests() {
  log('\n=== Email Service Smoke Tests ===\n', 'cyan');

  // Test 1: Check configuration
  log('1. Testing email configuration...', 'blue');
  const configResult = await testEndpoint(
    'Check Configuration',
    'GET',
    '/api/email/test'
  );

  if (!configResult.success || !configResult.data.configured) {
    log('\n⚠️  Email service not configured!', 'yellow');
    log('Please set SMTP_USER and SMTP_APP_PASSWORD in your .env file', 'yellow');
    log('See EMAIL_SETUP.md for instructions\n', 'yellow');
    return;
  }

  log(`   Configuration: ${configResult.data.configured ? 'OK' : 'Missing'}`, 'green');
  log(`   Connection: ${configResult.data.connected ? 'OK' : 'Failed'}`, configResult.data.connected ? 'green' : 'red');

  if (!configResult.data.connected) {
    log('\n⚠️  Email service connection failed!', 'yellow');
    log('Please check your SMTP credentials and try again\n', 'yellow');
    return;
  }

  // Prompt for test email address
  log('\n2. To test email sending, please provide a test email address:', 'blue');
  log('   (Press Ctrl+C to skip email tests)\n', 'yellow');

  // In a real scenario, you would get this from command line args or user input
  // For now, we'll check if TEST_EMAIL env var is set
  const testEmail = process.env.TEST_EMAIL;

  if (!testEmail) {
    log('   No TEST_EMAIL environment variable set', 'yellow');
    log('   Skipping email sending tests', 'yellow');
    log('   To test email sending, run:', 'cyan');
    log('   TEST_EMAIL=your@email.com node test-email.js\n', 'cyan');
    return;
  }

  // Test 2: Send test email
  log(`\n3. Sending test email to ${testEmail}...`, 'blue');
  await testEndpoint(
    'Send Test Email',
    'POST',
    '/api/email/test',
    { to: testEmail }
  );

  // Test 3: Send quote email
  log('\n4. Sending quote email...', 'blue');
  await testEndpoint(
    'Send Quote Email',
    'POST',
    '/api/email/quote',
    {
      to: testEmail,
      data: {
        customerName: 'Test Customer',
        quoteNumber: 'Q-TEST-001',
        items: [
          {
            name: 'Panel Isodec 100mm',
            quantity: 10,
            unitPrice: 150.00,
            total: 1500.00,
          },
          {
            name: 'Chapa Trapezoidal',
            quantity: 5,
            unitPrice: 200.00,
            total: 1000.00,
          },
        ],
        subtotal: 2500.00,
        iva: 550.00,
        total: 3050.00,
        validUntil: '2024-12-31',
      },
    }
  );

  // Test 4: Send order email
  log('\n5. Sending order email...', 'blue');
  await testEndpoint(
    'Send Order Email',
    'POST',
    '/api/email/order',
    {
      to: testEmail,
      data: {
        customerName: 'Test Customer',
        orderNumber: 'ORD-TEST-001',
        orderDate: new Date().toLocaleDateString(),
        items: [
          {
            name: 'Panel Isodec 100mm',
            quantity: 10,
            price: 1500.00,
          },
        ],
        total: 1830.00,
        shippingAddress: 'Av. 18 de Julio 1234, Montevideo, Uruguay',
        trackingNumber: 'TRACK-TEST-123',
      },
    }
  );

  // Test 5: Send custom email
  log('\n6. Sending custom email...', 'blue');
  await testEndpoint(
    'Send Custom Email',
    'POST',
    '/api/email/send',
    {
      to: testEmail,
      subject: 'Test Custom Email from BMC',
      html: '<h1>Test Email</h1><p>This is a custom test email from the BMC Chatbot system.</p>',
      text: 'Test Email\n\nThis is a custom test email from the BMC Chatbot system.',
    }
  );

  log('\n=== Email Tests Complete ===\n', 'cyan');
  log('Check your inbox at:', 'blue');
  log(`   ${testEmail}\n`, 'green');
  log('You should have received:', 'blue');
  log('   ✓ Test email', 'green');
  log('   ✓ Quote confirmation email', 'green');
  log('   ✓ Order confirmation email', 'green');
  log('   ✓ Custom email\n', 'green');
}

// Run tests
runTests().catch((error) => {
  log(`\nTest suite failed: ${error.message}`, 'red');
  process.exit(1);
});
