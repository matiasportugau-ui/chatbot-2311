# Implementation Plan: Automated Hourly MercadoLibre Draft Answers

## Goal
Create a self‑contained module that runs `draft-answers-script.ts` every hour, starting immediately, and deploy it as a system service.

## Steps
1. **Wrap the script in a Node.js executable**
   - Add a new file `src/lib/mercado-libre/auto-run.ts` that imports the main function from `draft-answers-script.ts` and invokes it.
   - Add a shebang (`#!/usr/bin/env node`) and make the file executable.
2. **Expose a CLI command**
   - Update `package.json` with a `bin` entry, e.g. `"mercado-auto": "src/lib/mercado-libre/auto-run.ts"`.
   - Run `npm install` to generate the binary in `node_modules/.bin`.
3. **Create a systemd service & timer** (Linux/macOS with `launchd` fallback)
   - Service file `/etc/systemd/system/mercado-auto.service`:
     ```ini
     [Unit]
     Description=Run MercadoLibre draft answers hourly
     After=network-online.target

     [Service]
     Type=oneshot
     WorkingDirectory=/Users/matias/chatbot2511/chatbot-2311
     ExecStart=/usr/bin/env bash -c 'source .venv/bin/activate && npm run mercado-auto'
     EnvironmentFile=/Users/matias/chatbot2511/chatbot-2311/.env
     ```
   - Timer file `/etc/systemd/system/mercado-auto.timer`:
     ```ini
     [Unit]
     Description=Hourly trigger for MercadoLibre draft answers

     [Timer]
     OnCalendar=hourly
     Persistent=true

     [Install]
     WantedBy=timers.target
     ```
   - Enable with `sudo systemctl enable --now mercado-auto.timer`.
4. **macOS launchd alternative** (if systemd unavailable)
   - Create `~/Library/LaunchAgents/com.mercado.auto.plist` with `StartInterval` set to `3600` seconds.
   - Load via `launchctl load ~/Library/LaunchAgents/com.mercado.auto.plist`.
5. **Verify immediate start**
   - After installing the service, run `sudo systemctl start mercado-auto.service` (or `launchctl start` on macOS) to execute the script now.
6. **Logging**
   - Direct stdout/stderr to `/var/log/mercado-auto.log` via `StandardOutput=append:/var/log/mercado-auto.log` in the service file.
7. **Testing**
   - Manually trigger the service and confirm `MERCADO_LIBRE_DRAFT_ANSWERS.md` is regenerated.
   - Check the log for any errors.
8. **Documentation**
   - Add a `README.md` section describing the module, how to install, and how to modify the schedule.

## Deliverables
- `auto-run.ts` wrapper script
- Updated `package.json`
- Systemd service & timer files (or launchd plist)
- README documentation
- Implementation plan (this file)

## Risks & Mitigations
- **Missing env vars** – ensure `.env` is referenced via `EnvironmentFile`.
- **Permission issues** – service files require root; provide instructions for sudo.
- **Node version mismatch** – enforce the same Node version used in the repo via `.nvmrc`.

---
*Generated automatically; review and approve before proceeding with code changes.*
