# 🔐 GitHub Secrets Setup Guide

Complete step-by-step guide to configure all required GitHub secrets for the CI/CD pipeline.

---

## 📍 Location in GitHub

1. Navigate to your repository
2. Click **Settings** tab
3. In left sidebar, click **Secrets and variables**
4. Click **Actions**
5. Click **New repository secret** button

---

## 🔑 Required Secrets (in order of setup)

### 1️⃣ DOCKERHUB_USERNAME
**Purpose:** DockerHub username for authentication

**Where to get it:**
1. Go to https://hub.docker.com/settings/profile
2. Username is in the URL or profile section

**How to add:**
- Name: `DOCKERHUB_USERNAME`
- Value: Your DockerHub username (e.g., `yourname`)
- Click **Add secret**

**Verification:**
```bash
# On your local machine
docker login
# Your username shown in prompt
```

---

### 2️⃣ DOCKERHUB_TOKEN
**Purpose:** Secure authentication token for DockerHub API access

**⚠️ DO NOT use your password! Use an access token instead**

**How to create token:**
1. Go to https://hub.docker.com/settings/security
2. Click **New Access Token** button
3. Fill in:
   - Token name: `github-actions`
   - Permissions: Check `Read & Write`
4. Click **Create** button
5. **Copy the token immediately** (won't be shown again!)

**How to add:**
- Name: `DOCKERHUB_TOKEN`
- Value: Paste the entire token (looks like `dckr_pat_xxx...`)
- Click **Add secret**

**Verification:**
```bash
# Test locally
echo "dckr_pat_xxx..." | docker login -u yourname --password-stdin
# Should show "Login Succeeded"
```

---

### 3️⃣ AWS_ACCESS_KEY_ID
**Purpose:** AWS IAM access key ID for authentication

**How to get it:**
```bash
# If IAM user already created:
aws iam list-access-keys --user-name github-actions

# If need to create new key:
aws iam create-access-key --user-name github-actions
```

**Output will show:**
```json
{
  "AccessKey": {
    "AccessKeyId": "AKIA2EXAMPLEKEY12345",
    "SecretAccessKey": "wJal...",
    ...
  }
}
```

**How to add:**
- Name: `AWS_ACCESS_KEY_ID`
- Value: The AccessKeyId value (starts with `AKIA`)
- Click **Add secret**

---

### 4️⃣ AWS_SECRET_ACCESS_KEY
**Purpose:** AWS IAM secret access key

**How to get it:**
Same as above - from the `create-access-key` output

**⚠️ IMPORTANT:** 
- Save this securely immediately
- Can't retrieve it again
- If lost, delete key and create new one

**How to add:**
- Name: `AWS_SECRET_ACCESS_KEY`
- Value: The SecretAccessKey value (looks like `wJalxxx...`)
- Click **Add secret**

**Verification:**
```bash
# Test locally
aws configure
# Enter your Access Key ID and Secret
aws sts get-caller-identity
# Should show your AWS account and user
```

---

### 5️⃣ AWS_REGION
**Purpose:** AWS region where your EC2 instances are located

**Common values:**
```
us-east-1           # N. Virginia (default)
us-west-2           # Oregon
eu-west-1           # Ireland
eu-central-1        # Frankfurt
ap-southeast-1      # Singapore
ap-northeast-1      # Tokyo
```

**How to find your region:**
```bash
# Option 1: Check EC2 console URL
# https://console.aws.amazon.com/ec2/v2/home?region=us-east-1

# Option 2: Query with AWS CLI
aws ec2 describe-instances \
  --query 'Reservations[0].Instances[0].Placement.AvailabilityZone' \
  --output text
# Returns: us-east-1a (remove the 'a' → us-east-1)
```

**How to add:**
- Name: `AWS_REGION`
- Value: Your region (e.g., `us-east-1`)
- Click **Add secret**

---

### 6️⃣ EC2_SSH_KEY
**Purpose:** Private SSH key to connect to EC2 instances

**⚠️ CRITICAL:** This is your private key - keep it SECRET!

**How to get it:**
```bash
# Display your private key
cat ~/.ssh/your-key.pem

# Output looks like:
# -----BEGIN RSA PRIVATE KEY-----
# MIIEpAIBAAKCAQEA2k3Xu...
# ... (many lines) ...
# -----END RSA PRIVATE KEY-----
```

**How to add:**
- Name: `EC2_SSH_KEY`
- Value: **PASTE THE ENTIRE KEY**
  - Include the `BEGIN RSA PRIVATE KEY` line
  - Include the `END RSA PRIVATE KEY` line
  - Include all lines in between
  - ⚠️ Don't add any extra spaces or quotes
- Click **Add secret**

**Verification:**
```bash
# Test locally
ssh -i ~/.ssh/your-key.pem ec2-user@your-ec2-ip
# Should connect without password
```

---

### 7️⃣ EC2_USER
**Purpose:** Default SSH user for your EC2 instance AMI

**Default values by AMI:**
```
Amazon Linux      → ec2-user
Ubuntu            → ubuntu
Debian            → admin
RHEL              → ec2-user
Windows           → Not applicable (use RDP instead)
```

**How to find yours:**
```bash
# Check which user works
ssh -i key.pem ec2-user@10.2.3.4
# OR
ssh -i key.pem ubuntu@10.2.3.4
# OR
ssh -i key.pem admin@10.2.3.4

# The one that connects is your user
```

**How to add:**
- Name: `EC2_USER`
- Value: The correct user for your AMI (e.g., `ec2-user`)
- Click **Add secret**

---

### 8️⃣ EC2_TAG_KEY
**Purpose:** The tag key used to identify EC2 instances

**What is a tag key?**
- Tags are key-value pairs on EC2 instances
- Example tag: `Environment: production`
  - KEY = `Environment`
  - VALUE = `production`

**Common tag keys:**
```
Environment
Application
Name
Type
Department
Owner
```

**What you choose:**
```bash
# If you tagged instances as:
# Environment → production
# Then: EC2_TAG_KEY = "Environment"

# If you tagged as:
# App → load-balancer
# Then: EC2_TAG_KEY = "App"
```

**How to verify your instances' tags:**
```bash
aws ec2 describe-tags \
  --filters "Name=resource-type,Values=instance" \
  --output table
```

**How to add:**
- Name: `EC2_TAG_KEY`
- Value: The tag key you used (e.g., `Environment`)
- Click **Add secret**

---

### 9️⃣ EC2_TAG_VALUE
**Purpose:** The tag value to filter EC2 instances

**What is a tag value?**
- See example above: `Environment: production`
  - VALUE = `production`

**What you choose:**
```bash
# If instances tagged as: Environment = production
# Then: EC2_TAG_VALUE = "production"

# If instances tagged as: Environment = staging
# Then: EC2_TAG_VALUE = "staging"
```

**Must match EC2_TAG_KEY:**
```bash
# Workflow queries:
aws ec2 describe-instances \
  --filters "Name=tag:${EC2_TAG_KEY},Values=${EC2_TAG_VALUE}"

# With your values:
# aws ec2 describe-instances \
#   --filters "Name=tag:Environment,Values=production"
```

**How to add:**
- Name: `EC2_TAG_VALUE`
- Value: The tag value to match (e.g., `production`)
- Click **Add secret**

---

## ✅ Complete Secrets Checklist

Create these 9 secrets in this order:

```
DOCKERHUB_USERNAME       ✓
DOCKERHUB_TOKEN          ✓
AWS_ACCESS_KEY_ID        ✓
AWS_SECRET_ACCESS_KEY    ✓
AWS_REGION              ✓
EC2_SSH_KEY             ✓
EC2_USER                ✓
EC2_TAG_KEY             ✓
EC2_TAG_VALUE           ✓
```

---

## 🔍 Verify All Secrets Are Set

### Via GitHub Web UI
1. Go to Settings → Secrets and variables → Actions
2. Should see all 9 secrets listed
3. Click on each to verify it's not empty

### Via GitHub CLI
```bash
gh secret list --repo your-username/your-repo
```

Should show:
```
DOCKERHUB_USERNAME       Updated Dec 23, 2024
DOCKERHUB_TOKEN          Updated Dec 23, 2024
AWS_ACCESS_KEY_ID        Updated Dec 23, 2024
AWS_SECRET_ACCESS_KEY    Updated Dec 23, 2024
AWS_REGION               Updated Dec 23, 2024
EC2_SSH_KEY              Updated Dec 23, 2024
EC2_USER                 Updated Dec 23, 2024
EC2_TAG_KEY              Updated Dec 23, 2024
EC2_TAG_VALUE            Updated Dec 23, 2024
```

---

## 🔄 Update a Secret

**Steps:**
1. Go to Settings → Secrets and variables → Actions
2. Find the secret to update
3. Click the **pencil icon**
4. Update the value
5. Click **Update secret**

**Common updates:**
- Access key expired → Create new AWS access key
- Changed DockerHub password → Get new access token
- Changed SSH key → Paste new private key
- Changed tagging strategy → Update EC2_TAG_KEY or EC2_TAG_VALUE

---

## 🗑️ Delete a Secret

**Steps:**
1. Go to Settings → Secrets and variables → Actions
2. Find the secret to delete
3. Click the **trash icon**
4. Confirm deletion

**When to delete:**
- Rotating credentials
- Changed AWS IAM user
- Decommissioning this workflow
- Accidentally added wrong value

---

## 🚨 Security Best Practices

### ✅ DO:
- ✓ Use access tokens instead of passwords
- ✓ Store private keys in secrets
- ✓ Rotate credentials periodically (every 90 days)
- ✓ Use specific IAM policies (EC2ReadOnly, not full admin)
- ✓ Review secret access logs
- ✓ Restrict branch access in workflow (if sensitive)

### ❌ DON'T:
- ✗ Commit secrets to Git (use .gitignore)
- ✗ Share credentials in chat/email
- ✗ Use personal credentials in CI/CD
- ✗ Hard-code secrets in workflow files
- ✗ Log or print secrets
- ✗ Use same credential across projects

### 🔒 Secret Scanning

GitHub automatically scans for exposed secrets:
1. If secret detected in commit → GitHub notifies you
2. Partner services are notified
3. Can automatically revoke credentials

**Best practice:** If you ever expose a secret:
1. Delete it immediately
2. Generate new credentials
3. Update GitHub secrets

---

## 🧪 Test Your Secrets

### Quick Verification in Workflow

Create a test workflow file `.github/workflows/test-secrets.yml`:

```yaml
name: Test Secrets

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test DockerHub secrets
        run: |
          echo "✓ DOCKERHUB_USERNAME is set"
          echo "✓ DOCKERHUB_TOKEN is set"

      - name: Test AWS secrets
        run: |
          echo "✓ AWS_ACCESS_KEY_ID is set"
          echo "✓ AWS_SECRET_ACCESS_KEY is set"
          echo "✓ AWS_REGION is set"

      - name: Test EC2 secrets
        run: |
          echo "✓ EC2_SSH_KEY is set"
          echo "✓ EC2_USER is set"
          echo "✓ EC2_TAG_KEY is set"
          echo "✓ EC2_TAG_VALUE is set"
```

If any secret is missing, the step will show an error.

---

## 💡 Tips & Tricks

### Mask Sensitive Output
Workflow automatically masks secret values in logs:
```yaml
echo "Connecting as: ${{ secrets.EC2_USER }}@$IP"
# Output: Connecting as: ec2-user@10.2.3.4
# The IP might be exposed if not in a secret
```

### Debug Secret Issues
```yaml
- name: Debug (remove in production!)
  run: |
    # DON'T do this in production!
    # echo "Key: ${{ secrets.EC2_SSH_KEY }}"
    
    # Instead, check if secret exists:
    if [ -z "${{ secrets.EC2_SSH_KEY }}" ]; then
      echo "ERROR: EC2_SSH_KEY is not set"
      exit 1
    fi
    echo "✓ EC2_SSH_KEY is configured"
```

### Use Separate Secrets per Environment
For staging vs production:
```
Secrets for staging:
  STAGING_AWS_REGION = us-west-2
  STAGING_EC2_TAG_VALUE = staging

Secrets for production:
  PROD_AWS_REGION = us-east-1
  PROD_EC2_TAG_VALUE = production
```

Then use environment variable to select:
```yaml
env:
  ENVIRONMENT: production

run: |
  TAG_VALUE=$(eval echo \$${ENVIRONMENT}_EC2_TAG_VALUE)
  # TAG_VALUE now = production
```

---

## 🆘 Troubleshooting Secrets

### Issue: "Secrets are empty in workflow"
**Possible causes:**
1. Secrets not yet created
2. Secret name mismatch (case-sensitive)
3. Repository requires approval for secrets

**Fix:**
```yaml
# Check if secret is being populated
- name: Check secrets
  run: |
    if [ -z "${{ secrets.DOCKERHUB_USERNAME }}" ]; then
      echo "ERROR: DOCKERHUB_USERNAME is empty"
    else
      echo "✓ DOCKERHUB_USERNAME is set"
    fi
```

### Issue: "Invalid secret characters"
**Possible cause:** Extra spaces or special characters

**Fix:**
```bash
# When adding EC2_SSH_KEY:
# Make sure to paste EVERYTHING exactly as-is
# Don't add extra newlines or spaces before/after
```

### Issue: "Secret revoked by service"
**What happened:** GitHub detected exposed credential

**Fix:**
1. Delete the exposed credential (AWS access key, token, etc.)
2. Create a new one
3. Update the GitHub secret
4. Re-run workflow

---

## 📚 Quick Reference Table

| Secret Name | Type | Length | Expires | Where from |
|---|---|---|---|---|
| DOCKERHUB_USERNAME | Text | 5-20 chars | Never | DockerHub profile |
| DOCKERHUB_TOKEN | Token | ~50 chars | Never | DockerHub settings |
| AWS_ACCESS_KEY_ID | AWS Key | 20 chars | +90 days | AWS IAM console |
| AWS_SECRET_ACCESS_KEY | AWS Key | ~40 chars | +90 days | AWS IAM console |
| AWS_REGION | Text | 10-20 chars | Never | AWS console or CLI |
| EC2_SSH_KEY | Private Key | 1500+ chars | Tied to key | Your .pem file |
| EC2_USER | Text | 5-20 chars | Never | Your AMI type |
| EC2_TAG_KEY | Text | 5-30 chars | Never | Your tagging scheme |
| EC2_TAG_VALUE | Text | 5-30 chars | Never | Your tagging scheme |

---

## ✨ You're all set!

All 9 secrets are now configured. Your CI/CD pipeline can:
✓ Build Docker images
✓ Push to DockerHub
✓ Query AWS for EC2 instances  
✓ Deploy to all instances matching tags
✓ Perform health checks

Ready to push code and trigger the workflow! 🚀
