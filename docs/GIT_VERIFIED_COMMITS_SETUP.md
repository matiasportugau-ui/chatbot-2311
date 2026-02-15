# Git Verified Commits Setup for Vercel

## Quick Setup

**⏱️ Need to set this up quickly?** See [GPG_QUICK_SETUP.md](./GPG_QUICK_SETUP.md) for a streamlined 20-minute setup guide.

---

## Overview

Vercel supports **Verified Commits** as a security feature to ensure that all deployed commits are signed with GPG keys. This helps verify the authenticity of commits and protects against unauthorized code changes.

## What are Verified Commits?

Verified commits are Git commits that have been signed with a GPG (GNU Privacy Guard) key. When a commit is signed:
- GitHub displays a "Verified" badge next to the commit
- You can verify the commit came from a trusted source
- Vercel can enforce that only verified commits are deployed

## Setup for GitHub Actions

### 1. Generate GPG Key

If you don't already have a GPG key, generate one:

```bash
# Generate a new GPG key
gpg --full-generate-key

# Choose:
# - RSA and RSA (default)
# - 4096 bits
# - Key does not expire (or set expiration)
# - Enter your name and email (must match GitHub account)
```

### 2. Export GPG Key

```bash
# List your GPG keys
gpg --list-secret-keys --keyid-format=long

# Export the private key (replace KEY_ID with your actual key ID)
gpg --armor --export-secret-keys KEY_ID

# Export the public key
gpg --armor --export KEY_ID
```

### 3. Add GPG Key to GitHub

1. Go to GitHub Settings → SSH and GPG keys
2. Click "New GPG key"
3. Paste your **public key** (output from `gpg --armor --export KEY_ID`)
4. Save the key

### 4. Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `GPG_PRIVATE_KEY`: Your private GPG key (output from `gpg --armor --export-secret-keys KEY_ID`)
- `GPG_PASSPHRASE`: The passphrase for your GPG key (if you set one)

### 5. GitHub Actions Configuration

The repository's workflows have been updated to automatically sign commits when the GPG secrets are configured:

```yaml
- name: Import GPG key
  if: ${{ secrets.GPG_PRIVATE_KEY != '' }}
  uses: crazy-max/ghaction-import-gpg@v6
  with:
    gpg_private_key: ${{ secrets.GPG_PRIVATE_KEY }}
    passphrase: ${{ secrets.GPG_PASSPHRASE }}
    git_user_signingkey: true
    git_commit_gpgsign: true
```

This configuration has been added to:
- `.github/workflows/ci.yml` (deploy job)
- `.github/workflows/auto-update-products.yml` (update job)
- `.github/workflows/release.yml` (release job)

## Setup for Local Development

To sign commits locally:

```bash
# Configure Git to use your GPG key
git config --global user.signingkey YOUR_KEY_ID
git config --global commit.gpgsign true

# Test signing
git commit -S -m "Test signed commit"

# Verify the commit is signed
git log --show-signature -1
```

## Vercel Configuration

To enable verified commits in Vercel:

1. Go to your Vercel project settings
2. Navigate to **Git** settings
3. Enable **"Deploy only verified commits"**
4. Save the configuration

Once enabled, Vercel will only deploy commits that have a verified signature.

## Benefits

✅ **Enhanced Security**: Ensures commits come from trusted sources  
✅ **Code Integrity**: Protects against unauthorized code changes  
✅ **Compliance**: Meets security requirements for sensitive projects  
✅ **Trust**: Provides cryptographic proof of commit authorship  

## Troubleshooting

### Commit signing fails in GitHub Actions

- Verify that `GPG_PRIVATE_KEY` and `GPG_PASSPHRASE` secrets are correctly set
- Ensure the GPG key format is correct (should include `-----BEGIN PGP PRIVATE KEY BLOCK-----` header)
- Check that the key hasn't expired

### Commits not showing as verified on GitHub

- Make sure the GPG key's email matches the email in your Git commits
- Verify the public key is added to your GitHub account
- Check that the key is not revoked or expired

### Local commits not signing

- Verify GPG is installed: `gpg --version`
- Check Git configuration: `git config --global commit.gpgsign`
- Ensure the signing key is configured: `git config --global user.signingkey`

## References

- [Vercel Verified Commits Documentation](https://vercel.com/docs/project-configuration/git-settings#verified-commits)
- [GitHub GPG Keys Documentation](https://docs.github.com/en/authentication/managing-commit-signature-verification)
- [crazy-max/ghaction-import-gpg Action (v6)](https://github.com/crazy-max/ghaction-import-gpg)

## Security Notes

⚠️ **Important**: 
- Never commit your private GPG key to the repository
- Always use GitHub Secrets for storing sensitive keys
- Rotate your GPG keys periodically
- Use a strong passphrase for your GPG key
