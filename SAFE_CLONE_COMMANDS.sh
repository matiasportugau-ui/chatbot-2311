#!/bin/bash
# safe_clone_commands.sh
# Safe commands for cloning and setting up on a second computer

echo "🛡️  Safe Clone Commands for Second Computer"
echo "============================================"
echo ""

echo "📥 Option 1: Clone with default name (recommended)"
echo "   git clone https://github.com/matiasportugau-ui/chatbot-2311.git"
echo "   cd chatbot-2311"
echo ""

echo "📥 Option 2: Clone with custom folder name (also safe)"
echo "   git clone https://github.com/matiasportugau-ui/chatbot-2311.git my-chatbot"
echo "   cd my-chatbot"
echo ""

echo "📥 Option 3: Clone with descriptive name"
echo "   git clone https://github.com/matiasportugau-ui/chatbot-2311.git chatbot-second-computer"
echo "   cd chatbot-second-computer"
echo ""

echo "✅ After cloning, switch to your working branch:"
echo "   git checkout 5122025-CHATBOT-2000"
echo ""

echo "✅ Then set up environment:"
echo "   ./setup_new_computer.sh"
echo ""

echo "💡 Remember:"
echo "   - Folder name doesn't affect Git branches"
echo "   - Cloning is 100% safe - it's just a copy"
echo "   - Your remote repository stays untouched"
echo ""

