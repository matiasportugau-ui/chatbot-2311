# Code Review Extensions Setup Guide

## 🎯 Top Recommendations for Your Stack

### 1. **GitLens** (Essential)
**Extension ID:** `eamodio.gitlens`

**Why:** Best Git integration for code review
- See who changed what and when
- Blame annotations inline
- Commit history and file annotations
- Compare branches visually
- Code lens showing recent changes

**Install:**
```bash
code --install-extension eamodio.gitlens
```

---

### 2. **GitHub Pull Requests** (For Team Reviews)
**Extension ID:** `github.vscode-pull-request-github`

**Why:** Native GitHub PR integration
- Review PRs directly in VS Code/Cursor
- Comment on code inline
- Approve/request changes
- View diffs and file changes
- Merge PRs without leaving editor

**Install:**
```bash
code --install-extension github.vscode-pull-request-github
```

---

### 3. **ESLint** (TypeScript/JavaScript)
**Extension ID:** `dbaeumer.vscode-eslint`

**Why:** You already have ESLint in package.json - this makes it work in editor
- Real-time linting errors
- Auto-fix on save
- Integrates with your existing `next lint` script

**Install:**
```bash
code --install-extension dbaeumer.vscode-eslint
```

**Setup:** Create `.eslintrc.json` in root:
```json
{
  "extends": ["next/core-web-vitals", "next/typescript"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "warn",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

---

### 4. **Ruff** (Python - Modern & Fast)
**Extension ID:** `charliermarsh.ruff`

**Why:** Fastest Python linter (replaces flake8, pylint, isort, etc.)
- 10-100x faster than pylint/flake8
- Combines multiple tools
- Auto-fix support
- Perfect for your FastAPI backend

**Install:**
```bash
code --install-extension charliermarsh.ruff
```

**Setup:** Create `pyproject.toml` in root:
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]  # Line too long (handled by formatter)

[tool.ruff.format]
quote-style = "double"
```

---

### 5. **SonarLint** (Code Quality)
**Extension ID:** `sonarsource.sonarlint-vscode`

**Why:** Catches bugs and code smells before review
- Detects bugs, vulnerabilities, code smells
- Works for both TypeScript and Python
- Real-time feedback
- No server setup needed (free version)

**Install:**
```bash
code --install-extension sonarsource.sonarlint-vscode
```

---

### 6. **Error Lens** (Visual Error Display)
**Extension ID:** `usernamehw.errorlens`

**Why:** Makes errors/warnings super visible
- Inline error messages
- Highlights problematic lines
- Works with ESLint, TypeScript, Python errors

**Install:**
```bash
code --install-extension usernamehw.errorlens
```

---

## 🚀 Quick Setup Script

Run this to install all recommended extensions:

```bash
# Code Review & Git
code --install-extension eamodio.gitlens
code --install-extension github.vscode-pull-request-github

# TypeScript/JavaScript
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode

# Python
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension ms-python.black-formatter

# Code Quality
code --install-extension sonarsource.sonarlint-vscode
code --install-extension usernamehw.errorlens
code --install-extension streetsidesoftware.code-spell-checker
```

---

## 📋 Recommended VS Code Settings

Add to `.vscode/settings.json`:

```json
{
  // Editor
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit",
    "source.organizeImports": "explicit"
  },
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  
  // Language-specific formatters
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  
  // ESLint
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ],
  
  // Ruff (Python)
  "ruff.enable": true,
  "ruff.lint.enable": true,
  "ruff.format.args": ["--line-length=100"],
  
  // GitLens
  "gitlens.codeLens.enabled": true,
  "gitlens.currentLine.enabled": true,
  
  // Error Lens
  "errorLens.enabled": true,
  "errorLens.enabledDiagnosticLevels": ["error", "warning"]
}
```

---

## 🔄 Workflow Integration

### Pre-Commit Review Checklist

1. **Run linters:**
   ```bash
   npm run lint          # TypeScript/Next.js
   ruff check .          # Python
   ```

2. **Format code:**
   ```bash
   npm run format        # Prettier
   ruff format .         # Python formatting
   ```

3. **Type check:**
   ```bash
   npm run typecheck     # TypeScript
   ```

4. **Review with GitLens:**
   - Check blame annotations
   - Review recent changes
   - Verify commit messages

---

## 🎓 Alternative: AI-Powered Review Tools

Since you're using Cursor (which has AI built-in), you can also use:

1. **GitHub Copilot** - AI code suggestions and review
2. **Codeium** - Free AI code review alternative
3. **Cursor's Built-in AI** - Already available, great for code review

---

## 📊 Comparison Table

| Extension | Type | Best For | Speed |
|-----------|------|----------|-------|
| **GitLens** | Git | Code history & blame | ⚡⚡⚡ |
| **GitHub PR** | Git | PR reviews | ⚡⚡ |
| **Ruff** | Python Linter | Fast Python linting | ⚡⚡⚡⚡⚡ |
| **ESLint** | JS/TS Linter | TypeScript/Next.js | ⚡⚡⚡ |
| **SonarLint** | Quality | Bug detection | ⚡⚡⚡ |
| **Error Lens** | Visual | Error visibility | ⚡⚡⚡⚡ |

---

## 🎯 My Top 3 Picks for Your Project

1. **GitLens** - Essential for understanding code changes
2. **Ruff** - Best Python linter (much faster than alternatives)
3. **Error Lens** - Makes all errors immediately visible

Install these three first, then add others as needed!

