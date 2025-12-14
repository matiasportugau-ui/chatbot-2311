# Quick Setup: GPG Secrets for GitHub Actions

This guide provides step-by-step instructions for repository administrators to configure GPG signing for verified commits.

## Prerequisites

- Admin access to the GitHub repository
- GPG installed locally (`gpg --version` to check)

## Step 1: Generate GPG Key (5 minutes)

```bash
# Generate a new GPG key
gpg --full-generate-key

# When prompted, choose:
# 1. RSA and RSA (default)
# 2. 4096 bits
# 3. Key expiration: 0 (does not expire) or set your preference
# 4. Real name: Your GitHub username or "GitHub Actions Bot"
# 5. Email address: MUST match the email used for GitHub commits
#    - Use: <username>@users.noreply.github.com or your GitHub email
# 6. Set a passphrase (required for security)
```

## Step 2: Export GPG Keys (2 minutes)

```bash
# List your GPG keys to get the KEY_ID
gpg --list-secret-keys --keyid-format=long

# Output will look like:
# sec   rsa4096/ABC123DEF456 2024-12-14 [SC]
#                ^^^^^^^^^^^^
#                This is your KEY_ID

# Export PRIVATE key (keep this secure!)
gpg --armor --export-secret-keys YOUR_KEY_ID > private-key.asc

# Export PUBLIC key
gpg --armor --export YOUR_KEY_ID > public-key.asc
```

## Step 3: Add Public Key to GitHub (2 minutes)

1. Go to https://github.com/settings/keys
2. Click **"New GPG key"**
3. Open `public-key.asc` and copy its contents
4. Paste the public key into GitHub
5. Click **"Add GPG key"**

## Step 4: Add Secrets to Repository (3 minutes)

1. Go to your GitHub repository
   - Example: `https://github.com/YOUR_USERNAME/YOUR_REPOSITORY`
   - For this project: `https://github.com/matiasportugau-ui/chatbot-2311`
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**

### Add GPG_PRIVATE_KEY:
- Name: `GPG_PRIVATE_KEY`
- Value: Copy the ENTIRE contents of `private-key.asc` file
  - Including `-----BEGIN PGP PRIVATE KEY BLOCK-----`
  - And `-----END PGP PRIVATE KEY BLOCK-----`
- Click **"Add secret"**

### Add GPG_PASSPHRASE:
- Name: `GPG_PASSPHRASE`
- Value: The passphrase you set when creating the GPG key
- Click **"Add secret"**

## Step 5: Clean Up (1 minute)

```bash
# IMPORTANT: Delete the exported key files for security
rm private-key.asc public-key.asc

# Verify files are deleted
ls -la | grep key.asc  # Should show nothing
```

## Step 6: Verify Setup (5 minutes)

### Test Locally
```bash
# Configure git to use the GPG key
git config --global user.signingkey YOUR_KEY_ID
git config --global commit.gpgsign true

# Create a test commit
echo "test" > test.txt
git add test.txt
git commit -S -m "Test signed commit"

# Verify the signature
git log --show-signature -1

# Clean up test
git reset --hard HEAD~1
rm test.txt
```

### Test in GitHub Actions
1. Trigger any workflow that uses GPG signing (e.g., push to main branch)
2. Check workflow logs for "Import GPG key" step
3. Verify commits show as "Verified" on GitHub

## Troubleshooting

### "No secret key" error
- Verify the private key was exported correctly
- Check that the KEY_ID matches the exported key

### Commits not showing as "Verified"
- Ensure the GPG key's email matches the commit author email
- Verify the public key is added to GitHub
- Check that the key hasn't expired

### GitHub Actions fails to import key
- Verify both `GPG_PRIVATE_KEY` and `GPG_PASSPHRASE` are set in repository secrets
- Check the private key format is correct (includes headers and footers)
- Ensure there are no extra spaces or newlines in the secret values

## Security Best Practices

✅ **DO:**
- Use a strong passphrase for your GPG key
- Store the private key securely (use a password manager)
- Rotate keys periodically (every 1-2 years)
- Delete exported key files immediately after use
- Use separate keys for different purposes

❌ **DON'T:**
- Share your private key or passphrase
- Commit keys to repositories
- Use keys without passphrases
- Reuse the same key across multiple organizations
- Export keys on shared computers

## Optional: Enable Verified Commits in Vercel

To require verified commits for Vercel deployments:

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Git**
3. Enable **"Deploy only verified commits"**
4. Save changes

After enabling, Vercel will reject any deployment from unverified commits.

## Estimated Total Time: ~20 minutes

Once configured, all future commits created by GitHub Actions will be automatically signed with your GPG key, and they will appear as "Verified" on GitHub.

---

For detailed information, see [GIT_VERIFIED_COMMITS_SETUP.md](./GIT_VERIFIED_COMMITS_SETUP.md)
