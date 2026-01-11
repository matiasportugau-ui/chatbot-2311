#!/usr/bin/env node

/**
 * vercel-env-sync.js
 * Automates creation/updating of Vercel project environment variables
 * based on the configuration file `env-config.json`.
 */

const fs = require('fs')
const path = require('path')
const colors = require('colors')
const { Vercel } = require('@vercel/sdk')

// Load Vercel token from environment
const VERCEL_TOKEN = process.env.VERCEL_TOKEN
if (!VERCEL_TOKEN) {
  console.error('❌ VERCEL_TOKEN environment variable not set'.red)
  process.exit(1)
}

const vercel = new Vercel({ bearerToken: VERCEL_TOKEN })

// Load configuration
const configPath = path.resolve(__dirname, 'env-config.json')
if (!fs.existsSync(configPath)) {
  console.error(`❌ Config file not found at ${configPath}`.red)
  process.exit(1)
}

let config
try {
  config = JSON.parse(fs.readFileSync(configPath, 'utf8'))
} catch (e) {
  console.error('❌ Failed to parse env-config.json:'.red, e.message)
  process.exit(1)
}

async function syncProject(projectIdOrName) {
  console.log(`🚀 Syncing project: ${projectIdOrName}`.cyan)
  for (const variable of config.variables) {
    const payload = {
      key: variable.key,
      value: variable.value,
      type: variable.type,
      target: variable.target,
    }
    try {
      const response = await vercel.projects.createProjectEnv({
        idOrName: projectIdOrName,
        upsert: 'true',
        requestBody: payload,
      })
      console.log(
        `   ✅ ${variable.key} -> ${response.created ? 'created' : 'updated'}`
          .green
      )
    } catch (err) {
      console.error(`   ❌ Error syncing ${variable.key}:`, err.message.red)
    }
  }
}

;(async () => {
  const projects = config.projects || []
  if (projects.length === 0) {
    console.warn('⚠️ No projects defined in env-config.json'.yellow)
    return
  }
  for (const proj of projects) {
    await syncProject(proj)
  }
  console.log('\n🎉 All done!'.magenta.bold)
})()
