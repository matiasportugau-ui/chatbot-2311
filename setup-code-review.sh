#!/bin/bash

# Setup script for code review extensions and configurations
# This script sets up VS Code/Cursor extensions and configurations

set -e

echo "🔧 Setting up Code Review Extensions and Configurations..."
echo ""

# Create .vscode directory if it doesn't exist
mkdir -p .vscode

# Create VS Code settings.json
echo "📝 Creating .vscode/settings.json..."
cat > .vscode/settings.json << 'EOF'
{
  // Editor Settings
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit",
    "source.organizeImports": "explicit"
  },
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.rulers": [80, 100],
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  
  // Language-specific formatters
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    },
    "editor.tabSize": 4
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[javascriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[json]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[jsonc]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  
  // ESLint Configuration
  "eslint.enable": true,
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact"
  ],
  "eslint.workingDirectories": [
    { "pattern": "./" },
    { "pattern": "./nextjs-app" }
  ],
  
  // Ruff (Python) Configuration
  "ruff.enable": true,
  "ruff.lint.enable": true,
  "ruff.format.enable": true,
  "ruff.lint.args": ["--line-length=100"],
  "ruff.format.args": ["--line-length=100"],
  
  // Python Configuration
  "python.defaultInterpreterPath": "python3",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": false,
  "python.formatting.provider": "black",
  "python.analysis.typeCheckingMode": "basic",
  
  // GitLens Configuration
  "gitlens.codeLens.enabled": true,
  "gitlens.currentLine.enabled": true,
  "gitlens.hovers.enabled": true,
  "gitlens.statusBar.enabled": true,
  
  // Error Lens Configuration
  "errorLens.enabled": true,
  "errorLens.enabledDiagnosticLevels": ["error", "warning"],
  "errorLens.followCursor": "allLines",
  "errorLens.gutterIconsEnabled": true,
  
  // File Associations
  "files.associations": {
    "*.json": "jsonc"
  },
  
  // Exclude patterns
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true
  },
  
  // Search exclude patterns
  "search.exclude": {
    "**/node_modules": true,
    "**/__pycache__": true,
    "**/.next": true,
    "**/.git": true,
    "**/dist": true,
    "**/build": true
  }
}
EOF

# Create ESLint configuration
echo "📝 Creating .eslintrc.json..."
cat > .eslintrc.json << 'EOF'
{
  "extends": [
    "next/core-web-vitals",
    "next/typescript"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": [
      "warn",
      {
        "argsIgnorePattern": "^_",
        "varsIgnorePattern": "^_"
      }
    ],
    "@typescript-eslint/no-explicit-any": "warn",
    "@typescript-eslint/explicit-module-boundary-types": "off",
    "react-hooks/exhaustive-deps": "warn",
    "no-console": [
      "warn",
      {
        "allow": ["warn", "error"]
      }
    ],
    "prefer-const": "warn",
    "no-var": "error"
  },
  "ignorePatterns": [
    "node_modules/",
    ".next/",
    "out/",
    "build/",
    "dist/",
    "*.config.js",
    "*.config.ts"
  ]
}
EOF

echo "✅ Configuration files created!"
echo ""

# Install Python dependencies (Ruff, Black)
echo "🐍 Installing Python linting tools..."
if command -v pip3 &> /dev/null; then
    pip3 install --upgrade ruff black || echo "⚠️  Warning: Could not install Python tools. Run manually: pip3 install ruff black"
else
    echo "⚠️  Warning: pip3 not found. Install Python tools manually: pip3 install ruff black"
fi
echo ""

# Install VS Code extensions (if code command is available)
echo "📦 Installing VS Code/Cursor extensions..."
if command -v code &> /dev/null; then
    echo "Installing extensions via 'code' command..."
    code --install-extension eamodio.gitlens || echo "⚠️  Could not install GitLens"
    code --install-extension github.vscode-pull-request-github || echo "⚠️  Could not install GitHub PR"
    code --install-extension dbaeumer.vscode-eslint || echo "⚠️  Could not install ESLint"
    code --install-extension esbenp.prettier-vscode || echo "⚠️  Could not install Prettier"
    code --install-extension ms-python.python || echo "⚠️  Could not install Python"
    code --install-extension ms-python.vscode-pylance || echo "⚠️  Could not install Pylance"
    code --install-extension charliermarsh.ruff || echo "⚠️  Could not install Ruff"
    code --install-extension ms-python.black-formatter || echo "⚠️  Could not install Black"
    code --install-extension sonarsource.sonarlint-vscode || echo "⚠️  Could not install SonarLint"
    code --install-extension usernamehw.errorlens || echo "⚠️  Could not install Error Lens"
    code --install-extension streetsidesoftware.code-spell-checker || echo "⚠️  Could not install Code Spell Checker"
    echo "✅ Extensions installation attempted!"
else
    echo "⚠️  'code' command not found. Please install extensions manually:"
    echo "   - Open Cursor/VS Code"
    echo "   - Go to Extensions (Cmd+Shift+X)"
    echo "   - Search and install the extensions listed in CODE_REVIEW_SETUP.md"
fi
echo ""

# Run initial linting check
echo "🔍 Running initial lint checks..."
echo ""

# Check TypeScript/JavaScript
if [ -f "package.json" ]; then
    echo "📋 Checking TypeScript/JavaScript..."
    if command -v npm &> /dev/null; then
        npm run lint || echo "⚠️  ESLint found some issues (this is normal)"
    else
        echo "⚠️  npm not found. Run 'npm run lint' manually"
    fi
    echo ""
fi

# Check Python
if command -v ruff &> /dev/null; then
    echo "🐍 Checking Python with Ruff..."
    ruff check . --select E,F,I,N,W,UP || echo "⚠️  Ruff found some issues (this is normal)"
    echo ""
else
    echo "⚠️  Ruff not installed. Run 'pip3 install ruff' and then 'ruff check .'"
    echo ""
fi

echo "✨ Setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Reload Cursor/VS Code window (Cmd+Shift+P -> 'Reload Window')"
echo "   2. Check that extensions are installed in Extensions panel"
echo "   3. Open a file to see linting/formatting in action"
echo "   4. Run 'npm run lint' for TypeScript/JavaScript"
echo "   5. Run 'ruff check .' for Python"
echo ""

