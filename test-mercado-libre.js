#!/usr/bin/env node

/**
 * Lightweight smoke tests for the Mercado Libre integration.
 * Requires the Next.js dev server running locally and credentials configured.
 */

const BASE_URL = process.env.MERCADO_LIBRE_TEST_BASE_URL || 'http://localhost:3000'

const endpoints = [
  {
    name: 'OAuth Status',
    path: '/api/mercado-libre/auth/token',
    method: 'GET'
  },
  {
    name: 'Listings List',
    path: '/api/mercado-libre/listings/list?limit=1',
    method: 'GET'
  },
  {
    name: 'Orders List',
    path: '/api/mercado-libre/orders/list?limit=1',
    method: 'GET'
  },
  {
    name: 'Webhook Events',
    path: '/api/mercado-libre/webhook?events=true',
    method: 'GET'
  }
]

function log(message, type = 'info') {
  const colors = {
    info: '\x1b[36m',
    success: '\x1b[32m',
    error: '\x1b[31m',
    warn: '\x1b[33m',
    reset: '\x1b[0m'
  }
  console.log(`${colors[type]}${message}${colors.reset}`)
}

async function checkEndpoint(endpoint) {
  const url = `${BASE_URL}${endpoint.path}`
  try {
    const response = await fetch(url, { method: endpoint.method })
    const text = await response.text()
    const ok = response.ok
    log(`${ok ? '✅' : '❌'} ${endpoint.name} (${response.status})`, ok ? 'success' : 'error')
    if (!ok) {
      log(`   Response body: ${text}`, 'warn')
    }
    return ok
  } catch (error) {
    log(`❌ ${endpoint.name} - ${error.message}`, 'error')
    return false
  }
}

async function run() {
  log(`🔍 Running Mercado Libre integration smoke tests against ${BASE_URL}`)
  let passed = 0

  for (const endpoint of endpoints) {
    if (await checkEndpoint(endpoint)) {
      passed += 1
    }
  }

  log(`\n📊 Result: ${passed}/${endpoints.length} endpoints reachable`, passed === endpoints.length ? 'success' : 'warn')
  if (passed !== endpoints.length) {
    process.exitCode = 1
  }
}

run()

