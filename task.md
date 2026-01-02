# Task: Vercel Deployment & MercadoLibre Automation

## Vercel Deployment

- [x] Link project to Vercel (`vercel link`)
- [x] Configure environment variables in Vercel
- [x] Create `.vercelignore` to exclude large folders (backups, .git, venv)
- [x] Optimize `next.config.js` (`outputFileTracingExcludes`)
- [x] Resolve TypeScript build errors (`backups` exclusion in `tsconfig.json`)
- [x] Configure bmc-cotizacion-inteligente.vercel.app domain and redirect URIs
- [x] Add Mercado Libre status to Health Check endpoint

## MercadoLibre Integration

- [x] Deploy Python Backend to Cloud Run
- [x] Verify Backend Health
- [x] Generate MercadoLibre Auth URL
- [ ] Complete OAuth flow via authorization link
- [ ] Run `npm run mercado-auto` in Live Mode (verify with real data)
- [ ] Finalize Automation (monitor launchd/cron if needed)
