# 🔧 Fix: Vercel Root Directory Configuration Error

## Error Message

```
The specified Root Directory "matprompts-projects/bmc-cotizacion-inteligente" does not exist. 
Please update your Project Settings.
```

## Problem

Vercel is configured to look for your project in a subdirectory that doesn't exist in your repository. Your project files are at the repository root, not in a subdirectory.

## Solution

### Step 1: Access Vercel Dashboard
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Sign in to your account
3. Select your project: `bmc-cotizacion-inteligente`

### Step 2: Update Root Directory Setting
1. Click on **Settings** in the project navigation
2. Go to **General** tab
3. Scroll down to **Root Directory** section
4. **Clear the Root Directory field** (delete any value)
   - Or set it to `.` if the field requires a value
5. Click **Save**

### Step 3: Redeploy
1. Go to **Deployments** tab
2. Click **Redeploy** on the latest deployment
3. Or push a new commit to trigger automatic deployment

## Verification

After fixing the Root Directory setting:
- ✅ Build should start successfully
- ✅ No more "Root Directory does not exist" error
- ✅ Build logs should show files being found correctly

## Prevention

- **Root Directory should be empty** if your project is at the repository root
- Only set Root Directory if your project is in a subdirectory (e.g., `apps/frontend`)
- Verify the path exists in your repository before setting it

## Related Documentation

- **`DEPLOYMENT_SUMMARY.md`** - Complete deployment guide with troubleshooting
- **`DEPLOYMENT_AI_AGENT_PROMPT.md`** - AI agent instructions for handling this error

## Quick Fix Command (if using Vercel CLI)

If you have Vercel CLI access, you can also update via command line:

```bash
# Link project if not already linked
vercel link

# The Root Directory is set in Vercel dashboard, not via CLI
# You must use the dashboard to change it
```

**Note:** Root Directory is a project setting that must be changed in the Vercel dashboard, not via CLI or configuration files.
