# Codespaces Team Collaboration Guide

Complete guide for collaborating on the BMC Chatbot project using GitHub Codespaces.

## 👥 Adding Team Members

### Step 1: Add Collaborators
1. Go to: Repository → Settings → Collaborators
2. Click "Add people"
3. Enter GitHub usernames or emails
4. Choose permission level:
   - **Read**: Can view and clone
   - **Write**: Can push changes
   - **Admin**: Full access

### Step 2: Team Members Create Codespaces
Each team member:
1. Goes to the repository
2. Clicks "Code" → "Codespaces"
3. Creates their own Codespace
4. Gets their own isolated environment

## 🔄 Collaboration Workflows

### Workflow 1: Independent Development (Recommended)
**Best for**: Daily development work

1. **Each person has their own Codespace**
2. **Work on feature branches**
3. **Sync via Git**

```bash
# On your Codespace
git checkout -b feature/my-feature
# Make changes
git add .
git commit -m "Add feature"
git push origin feature/my-feature
# Create PR on GitHub
```

**Benefits**:
- ✅ No conflicts
- ✅ Isolated environments
- ✅ Can work simultaneously
- ✅ Standard Git workflow

### Workflow 2: Shared Development Environment
**Best for**: Pair programming, demos

1. **One person creates Codespace**
2. **Shares the Codespace**
3. **Both work in same environment**

**Steps**:
1. Create Codespace
2. Right-click Codespace → "Share"
3. Generate shareable link
4. Share link with teammate

**Limitations**:
- ⚠️ Only one person should edit at a time
- ⚠️ Changes are in one Codespace
- ⚠️ Need to commit to save work

### Workflow 3: Share Public URLs (Best for Demos)
**Best for**: Showing work to team, testing

1. **Make ports public** in Codespaces
2. **Share public URLs** with team
3. **Team accesses web apps** without Codespace access

**Steps**:
1. Start services: `bash scripts/codespaces-start.sh`
2. Go to "Ports" tab
3. Right-click port → "Change Port Visibility" → "Public"
4. Copy public URL
5. Share with team

**Example URLs**:
```
Next.js: https://matiasportugau-ui-xxxx-3000.preview.app.github.dev
FastAPI: https://matiasportugau-ui-xxxx-8000.preview.app.github.dev
n8n: https://matiasportugau-ui-xxxx-5678.preview.app.github.dev
```

## 🔐 Sharing Secrets with Team

### Method 1: GitHub Repository Secrets (Recommended)
**Best for**: Team-wide secrets

1. Repository → Settings → Secrets and variables → Codespaces
2. Add secrets
3. All Codespaces automatically have access

**Benefits**:
- ✅ Secure
- ✅ Centralized
- ✅ Easy to update
- ✅ All team members get access

### Method 2: Individual .env Files
**Best for**: Personal development keys

1. Each person creates their own `.env`
2. Never commit to Git
3. Use for personal API keys

## 📝 Code Review Process

### Standard Git Workflow
1. **Create feature branch** in Codespace
2. **Make changes**
3. **Commit and push**
4. **Create Pull Request** on GitHub
5. **Team reviews** in GitHub UI
6. **Merge** when approved

### Reviewing in Codespaces
1. **Checkout PR branch** in Codespace
2. **Test changes** locally
3. **Review code** in VS Code
4. **Add comments** in GitHub PR

```bash
# Checkout PR branch
git fetch origin pull/123/head:pr-123
git checkout pr-123

# Test
bash scripts/codespaces-start.sh
bash scripts/codespaces-health.sh

# Review and comment in GitHub
```

## 🎯 Best Practices

### For Team Leads
1. ✅ Set up repository secrets early
2. ✅ Document team workflows
3. ✅ Use branch protection rules
4. ✅ Regular code reviews
5. ✅ Monitor Codespaces usage

### For Team Members
1. ✅ Create your own Codespace
2. ✅ Use feature branches
3. ✅ Commit frequently
4. ✅ Share public URLs for demos
5. ✅ Stop Codespaces when done

### For Pair Programming
1. ✅ Use shared Codespace
2. ✅ Take turns editing
3. ✅ Commit frequently
4. ✅ Use VS Code Live Share extension (optional)

## 🚀 Onboarding New Team Members

### Checklist for New Members
- [ ] Added as collaborator
- [ ] Can access repository
- [ ] Created first Codespace
- [ ] Setup completed successfully
- [ ] Services start correctly
- [ ] Can access web apps
- [ ] Understands Git workflow
- [ ] Knows how to share URLs

### Quick Onboarding Script
```bash
# New team member runs this
git clone https://github.com/matiasportugau-ui/chatbot-2311.git
cd chatbot-2311
# Create Codespace from GitHub
# Or run locally:
bash scripts/codespaces-setup.sh
bash scripts/codespaces-start.sh
```

## 💬 Communication

### Sharing Progress
- **Public URLs**: Share for demos and testing
- **Screenshots**: Share in team chat
- **PRs**: Use for code review
- **Issues**: Track bugs and features

### Getting Help
- Check documentation first
- Ask in team chat
- Create GitHub issue
- Review logs: `cat .devcontainer/setup.log`

## 📊 Monitoring Team Usage

### Check Codespaces Usage
1. GitHub → Settings → Billing
2. View Codespaces usage
3. See hours used per team member

### Cost Management
- Set usage limits
- Monitor free tier usage (60 hours/month)
- Encourage stopping Codespaces when done
- Use smaller machines when possible

## 🔒 Security Considerations

1. ✅ **Repository secrets** - Use for shared secrets
2. ✅ **Private repositories** - Keep code private
3. ✅ **Port visibility** - Make public only when needed
4. ✅ **Access control** - Limit collaborator permissions
5. ✅ **Regular audits** - Review who has access

## 🆘 Troubleshooting Team Issues

### "Can't access Codespace"
- Verify collaborator permissions
- Check repository access
- Try creating new Codespace

### "Secrets not working"
- Verify secrets are in GitHub
- Check secret names match exactly
- Reload: `bash .devcontainer/load-secrets.sh`

### "Ports not accessible"
- Check port visibility (public/private)
- Verify services are running
- Check firewall settings

### "Conflicts in shared Codespace"
- Use separate Codespaces for development
- Only share for demos/pair programming
- Commit frequently

## 📚 Additional Resources

- [GitHub Collaboration Guide](https://docs.github.com/en/get-started/quickstart/contributing-to-projects)
- [Codespaces Documentation](https://docs.github.com/en/codespaces)
- [Git Workflow](https://guides.github.com/introduction/flow/)

---

**Happy Collaborating!** 🎉

