# Codespaces Security Guide

Security best practices for developing the BMC Chatbot in GitHub Codespaces.

## 🔐 Secrets Management

### ✅ DO: Use GitHub Repository Secrets
**Location**: Settings → Secrets and variables → Codespaces

**Why**:
- Encrypted at rest
- Automatically available in Codespaces
- Centralized management
- Easy to rotate

**How**:
1. Go to repository settings
2. Secrets and variables → Codespaces
3. Add new repository secret
4. Secret is automatically loaded in Codespaces

### ❌ DON'T: Commit Secrets to Git
**Never commit**:
- `.env` files with real secrets
- API keys in code
- Passwords in configuration files
- Access tokens in scripts

**Already protected**:
- `.env` is in `.gitignore`
- `env.example` has placeholders only

### ✅ DO: Use Environment Variables
```bash
# In Codespaces, secrets are automatically available
echo $OPENAI_API_KEY  # From GitHub Secrets

# Or use .env file (not committed)
source .env
```

## 🔒 Port Visibility

### Public Ports (Shareable)
**Use for**: Web apps you want to share
- Next.js Dashboard (3000)
- FastAPI API (8000)
- n8n Workflows (5678)

**Security**:
- ✅ HTTPS by default
- ✅ Unique URLs per Codespace
- ✅ Can be revoked by stopping Codespace
- ⚠️ Accessible to anyone with URL

**Best Practice**: Only make public when needed for demos/testing

### Private Ports (Internal)
**Use for**: Internal services
- MongoDB (27017)
- Qdrant (6333, 6334)

**Security**:
- ✅ Only accessible within Codespace
- ✅ Not shareable
- ✅ More secure

**Best Practice**: Keep database ports private

## 🛡️ Access Control

### Repository Permissions
**Recommended**:
- **Read**: For viewers
- **Write**: For developers
- **Admin**: For team leads only

**How to set**:
1. Settings → Collaborators
2. Manage access
3. Set appropriate permissions

### Codespace Access
- Each person gets their own Codespace
- Codespaces are isolated
- Can share temporarily for pair programming
- Stop sharing when done

## 🔐 API Key Security

### Rotation Policy
**Recommended**: Rotate keys every 90 days

**Steps**:
1. Generate new API key
2. Update in GitHub Secrets
3. Test in Codespace
4. Revoke old key

### Key Storage
**✅ Secure**:
- GitHub Repository Secrets
- Encrypted at rest
- Not in code
- Not in Git history

**❌ Insecure**:
- Hardcoded in files
- Committed to Git
- Shared in chat
- Stored in plain text

## 🌐 Network Security

### HTTPS by Default
- All Codespaces URLs use HTTPS
- Certificates managed by GitHub
- No configuration needed

### Firewall Considerations
- Codespaces run in GitHub's cloud
- No local firewall configuration
- GitHub handles network security

### VPN Not Required
- Codespaces accessible from anywhere
- No VPN needed
- Secure by default

## 📝 Data Persistence

### What's Stored
- **Code**: In Git repository (secure)
- **Secrets**: In GitHub Secrets (encrypted)
- **Data**: In Codespace volumes (temporary)

### What's NOT Stored
- **Secrets in Git**: Protected by `.gitignore`
- **API keys in code**: Should never be committed
- **Passwords**: Use GitHub Secrets

### Data Cleanup
- Codespaces are temporary
- Data deleted when Codespace is deleted
- Secrets remain in GitHub Secrets
- Code remains in Git repository

## 🔍 Security Checklist

### Before Starting Work
- [ ] Secrets configured in GitHub
- [ ] `.env` not committed to Git
- [ ] Port visibility set appropriately
- [ ] Repository is private (if sensitive)
- [ ] Collaborators have appropriate permissions

### During Development
- [ ] No secrets in code
- [ ] No secrets in commit messages
- [ ] Ports are private unless needed
- [ ] Regular commits (don't lose work)
- [ ] Code reviews before merging

### After Work
- [ ] Committed all changes
- [ ] No secrets left in terminal history
- [ ] Stopped Codespace (saves money)
- [ ] Reviewed access logs (if available)

## 🚨 Incident Response

### If Secrets Are Exposed
1. **Immediately rotate** the exposed secret
2. **Revoke** old key/token
3. **Review** Git history for exposure
4. **Update** all Codespaces with new secret
5. **Document** the incident

### If Codespace Is Compromised
1. **Stop** the Codespace immediately
2. **Delete** the Codespace
3. **Rotate** all secrets
4. **Review** access logs
5. **Create** new Codespace

### If Repository Is Compromised
1. **Revoke** all collaborator access
2. **Rotate** all secrets
3. **Review** recent commits
4. **Restore** from backup if needed
5. **Re-add** trusted collaborators

## 📊 Security Monitoring

### What to Monitor
- Codespace usage patterns
- Unusual access times
- Multiple Codespaces from same user
- Failed authentication attempts
- Unusual port forwarding

### GitHub Security Features
- **Dependabot**: Scans for vulnerabilities
- **Secret scanning**: Detects exposed secrets
- **Code scanning**: Finds security issues
- **Access logs**: Track who accessed what

## 🔐 Best Practices Summary

1. ✅ **Use GitHub Secrets** for all API keys
2. ✅ **Never commit secrets** to Git
3. ✅ **Keep database ports private**
4. ✅ **Make web app ports public only when needed**
5. ✅ **Rotate secrets regularly**
6. ✅ **Use private repositories** for sensitive code
7. ✅ **Limit collaborator permissions**
8. ✅ **Stop Codespaces when done**
9. ✅ **Review access regularly**
10. ✅ **Keep dependencies updated**

## 📚 Additional Resources

- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Codespaces Security](https://docs.github.com/en/codespaces/codespaces-reference/security-in-codespaces)
- [Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Dependabot](https://docs.github.com/en/code-security/dependabot)

---

**Stay Secure!** 🔒

