# Load Balancer App - CI/CD Pipeline with AWS CLI Integration

Complete CI/CD pipeline for building and deploying a Flask Load Balancer application using GitHub Actions and AWS CLI to dynamically fetch EC2 instance IPs.

## 📋 Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Setup Instructions](#setup-instructions)
6. [GitHub Secrets Configuration](#github-secrets-configuration)
7. [AWS EC2 Tagging Strategy](#aws-ec2-tagging-strategy)
8. [Workflow Explanation](#workflow-explanation)
9. [Troubleshooting](#troubleshooting)
10. [Error Resolutions](#error-resolutions)

---

## Overview

This project demonstrates a modern CI/CD approach for container-based deployments:
- **CI Workflow**: Builds Docker images and pushes to DockerHub
- **CD Workflow**: Uses AWS CLI to dynamically discover EC2 instances and deploy to them
- **Key Innovation**: No hardcoded IP addresses! Instances are discovered via AWS tags

### What Makes This Different

The original approach stored EC2 IPs as GitHub Secrets:
```yaml
secrets.EC2_HOST1
secrets.EC2_HOST2
```

**Our approach** uses AWS CLI to query EC2 by tags:
```bash
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[*].Instances[*].PublicIpAddress'
```

This means:
✅ Add new servers → They're automatically discovered by tags
✅ Remove servers → No manual secret updates needed
✅ Rotate IPs → Automatically handled
✅ More scalable → Works with any number of instances

---

## Key Features

- **Automated Build**: Builds Docker image on every push to main branch
- **Multi-registry Support**: Push to DockerHub with multiple tags
- **Dynamic Instance Discovery**: Uses AWS CLI and tags instead of hardcoded IPs
- **Parallel Deployments**: Deploys to all discovered instances simultaneously
- **Health Checks**: Verifies each deployment succeeded
- **Comprehensive Logging**: Detailed output for debugging

---

## Project Structure

```
.
├── .github/
│   └── workflows/
│       ├── ci-docker.yml          # Build & Push workflow
│       └── cd-deploy.yml          # Deploy workflow (AWS CLI)
├── app.py                          # Flask application
├── Dockerfile                      # Container definition
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## Prerequisites

### Local Development
- Docker & Docker Compose
- Python 3.11+
- Git

### AWS Setup
- AWS Account (Free Tier eligible)
- EC2 instances running Docker (tagged appropriately)
- IAM user with EC2 permissions
- SSH key pair for EC2 access

### GitHub
- GitHub repository
- DockerHub account

---

## Setup Instructions

### 1️⃣ Clone & Prepare Repository

```bash
# Clone your repository
git clone https://github.com/YOUR_USERNAME/load-balancer-app.git
cd load-balancer-app

# Create main branch if needed
git checkout -b main
```

### 2️⃣ Set Up AWS EC2 Instances

#### Create/Tag EC2 Instances
```bash
# Tag your instances for discovery
# Example: tag instances with Environment=production

aws ec2 create-tags \
  --resources i-1234567890abcdef0 \
  --tags Key=Environment,Value=production Key=Type,Value=load-balancer
```

Or via AWS Console:
1. Go to EC2 Dashboard → Instances
2. Select your instances
3. Tags → Add/Edit tags
4. Add: `Environment: production` (or your chosen tag)

**Recommended Tags:**
```
Environment: production
Type: load-balancer
Application: flask-app
```

#### Install Docker on EC2
```bash
# SSH into instance
ssh -i your-key.pem ec2-user@instance-ip

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo usermod -a -G docker ec2-user

# Verify Docker is running
docker ps
```

### 3️⃣ Create AWS IAM User (for GitHub Actions)

```bash
# Create new IAM user with EC2 permissions
aws iam create-user --user-name github-actions

# Create access key
aws iam create-access-key --user-name github-actions

# Attach EC2 read-only policy
aws iam attach-user-policy \
  --user-name github-actions \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess
```

### 4️⃣ Set Up GitHub Repository

```bash
# Push code to GitHub
git add .
git commit -m "Initial CI/CD setup with AWS CLI integration"
git push origin main
```

---

## GitHub Secrets Configuration

Add these secrets to your GitHub repository:
**Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

| Secret Name | Example Value | Description |
|---|---|---|
| `DOCKERHUB_USERNAME` | `yourname` | DockerHub username |
| `DOCKERHUB_TOKEN` | `dckr_pat_xxx...` | DockerHub access token |
| `AWS_ACCESS_KEY_ID` | `AKIA...` | AWS IAM access key |
| `AWS_SECRET_ACCESS_KEY` | `xxx...` | AWS IAM secret key |
| `AWS_REGION` | `us-east-1` | AWS region where EC2 instances are |
| `EC2_SSH_KEY` | (contents of .pem file) | **FULL content of your private key** |
| `EC2_USER` | `ec2-user` | Default user for your AMI |
| `EC2_TAG_KEY` | `Environment` | Tag key to query instances |
| `EC2_TAG_VALUE` | `production` | Tag value to match |

### How to Create Secrets

```bash
# Example: Add DockerHub token as secret
# 1. In GitHub UI: Settings → Secrets → New repository secret
# 2. Name: DOCKERHUB_TOKEN
# 3. Value: (paste your token)
# 4. Click "Add secret"

# For EC2_SSH_KEY, paste the entire contents:
cat ~/.ssh/your-key.pem
# Copy the full output (including BEGIN and END lines)
```

### Creating DockerHub Token

1. Go to [DockerHub Settings](https://hub.docker.com/settings/security)
2. Click "New Access Token"
3. Name: `github-actions`
4. Permissions: Read & Write
5. Copy the token and add to GitHub Secrets

### Creating AWS IAM Access Keys

```bash
# After creating IAM user:
aws iam create-access-key --user-name github-actions

# Output will show:
# AccessKeyId: AKIA...
# SecretAccessKey: xxx...

# Add both to GitHub Secrets
```

---

## AWS EC2 Tagging Strategy

### Why Tags Matter

The CD workflow queries EC2 instances using tags:
```bash
aws ec2 describe-instances \
  --filters "Name=tag:${EC2_TAG_KEY},Values=${EC2_TAG_VALUE}"
```

### Tagging Best Practices

**Standard Tags:**
```
Environment: production/staging/development
Application: load-balancer-app
Managed-By: github-actions
Department: platform
Cost-Center: engineering
```

**Check Current Tags:**
```bash
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[*].Instances[*].[InstanceId,Tags[?Key==`Name`].Value|[0],PublicIpAddress]' \
  --output table
```

### Updating Tags via AWS CLI

```bash
# Add/update tags
aws ec2 create-tags \
  --resources i-1234567890abcdef0 \
  --tags Key=Environment,Value=production

# View tags for an instance
aws ec2 describe-tags \
  --filters "Name=resource-id,Values=i-1234567890abcdef0"

# Delete a tag
aws ec2 delete-tags \
  --resources i-1234567890abcdef0 \
  --tags Key=OldTag
```

---

## Workflow Explanation

### CI Workflow (`ci-docker.yml`)

**Trigger:** Push to `main` branch

**Steps:**
1. **Checkout Code** → Get repository files
2. **Set up Docker Buildx** → Enable advanced Docker building
3. **DockerHub Login** → Authenticate with Docker credentials
4. **Build & Push** → Container image with two tags:
   - `latest` → Always points to most recent build
   - `sha` → Git commit hash (trace exact version)
5. **Success Message** → Confirms push completed

**Output:** Docker image on DockerHub ready for deployment

### CD Workflow (`cd-deploy.yml`)

**Trigger:** After CI workflow succeeds on `main` branch

**Steps:**

#### 1. Configure AWS Credentials
```yaml
- Configure AWS CLI with IAM credentials from secrets
- Validates connectivity to AWS
```

#### 2. Query EC2 Instances (The Magic! ✨)
```bash
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[*].Instances[*].PublicIpAddress' \
  --output text
```
**Output:** Space-separated list of all matching public IPs

**Example:**
```
10.2.3.4 10.2.3.5 10.2.3.6
```

#### 3. Set Up SSH
- Creates SSH directory
- Saves private key securely
- Configures SSH to skip host verification

#### 4. Deploy to All Instances
For each IP discovered:
```bash
ssh ec2-user@IP << 'EOF'
  sudo docker pull your-image:latest
  sudo docker stop container || true
  sudo docker rm container || true
  sudo docker run -d -p 80:80 your-image:latest
EOF
```

#### 5. Health Checks
For each instance:
```bash
curl http://IP/health
# Returns 200 if container is running
```

#### 6. Verification
Fetches app info from each instance to confirm deployment

---

## Troubleshooting

### Issue 1: "No instances found with specified tags"

**Cause:** EC2 instances don't have the expected tags

**Solution:**
```bash
# Verify tags on your instances
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,Tags]' \
  --output table

# Ensure tag names EXACTLY match your secrets
# EC2_TAG_KEY must be exact (case-sensitive)
```

### Issue 2: SSH Connection Timeout

**Cause:** Instance not reachable or security group issue

**Solution:**
```bash
# Check instance is running
aws ec2 describe-instances --instance-ids i-xxx

# Verify security group allows inbound SSH (port 22)
aws ec2 describe-security-groups --group-ids sg-xxx

# Test SSH manually
ssh -i your-key.pem ec2-user@IP "echo 'Connected!'"
```

### Issue 3: Docker Pull Fails on EC2

**Cause:** Docker daemon not running or auth issues

**Solution:**
```bash
# SSH to instance and check
ssh -i your-key.pem ec2-user@IP

# Check Docker service
sudo systemctl status docker

# Restart if needed
sudo systemctl restart docker

# Verify permission
docker ps
```

### Issue 4: Health Check Fails (503/502)

**Cause:** Container not fully started or app error

**Solution:**
```bash
# SSH to instance
ssh -i your-key.pem ec2-user@IP

# Check container
sudo docker ps

# View logs
sudo docker logs load-balancer-app

# Verify port is mapped
sudo netstat -tlnp | grep 80
```

### Issue 5: Deployment Hangs

**Cause:** SSH timeout or large Docker image

**Solution:**
- Increase timeout in workflow: `-o ConnectTimeout=30`
- Check DockerHub image size: `docker image ls`
- Optimize Dockerfile to reduce size

---

## Error Resolutions

### 1. Host Key Verification Error

**Error:**
```
Host key verification failed.
```

**Resolution:** Already handled in workflow  with:
```yaml
-o StrictHostKeyChecking=no
-o UserKnownHostsFile=/dev/null
```

### 2. Docker Permission Denied

**Error:**
```
permission denied while trying to connect to the Docker daemon
```

**Resolution:** Use `sudo` before Docker commands:
```bash
sudo docker pull image:tag
sudo docker run ...
```

### 3. SSH Permission Too Open

**Error:**
```
Permissions 0644 for 'deploy_key.pem' are too open
```

**Resolution:** Set correct permissions:
```bash
chmod 600 ~/.ssh/deploy_key.pem
```

### 4. Whitespace in Secrets

**Error:**
```
curl: (6) Could not resolve host
```

**Resolution:** Strip whitespace from secrets:
```bash
HOST=$(echo "${{ secrets.EC2_HOST }}" | tr -d '[:space:]')
```

### 5. AWS CLI Not Installed

**Error:**
```
aws: command not found
```

**Resolution:** AWS CLI comes pre-installed on GitHub Actions runners. If custom runner, install:
```bash
pip install awscli
```

---

## Local Testing

### Build Docker Image Locally

```bash
docker build -t load-balancer-app:latest .
docker run -d -p 8080:80 load-balancer-app:latest
curl http://localhost:8080/health
```

### View Logs

```bash
docker logs -f load-balancer-app
```

### Test API Endpoints

```bash
# Home
curl http://localhost:8080/

# Health check
curl http://localhost:8080/health

# Server info
curl http://localhost:8080/info

# Version
curl http://localhost:8080/api/version
```

---

## Production Checklist

- [ ] AWS IAM user created with minimal required permissions
- [ ] All GitHub Secrets configured
- [ ] EC2 instances tagged appropriately
- [ ] Security groups allow inbound SSH (port 22) and HTTP (port 80)
- [ ] SSH key paired properly
- [ ] DockerHub repository created
- [ ] Test deployment triggered manually
- [ ] Monitor logs for issues
- [ ] Set up GitHub branch protection rules
- [ ] Document your specific tag strategy

---

## Advanced Customization

### Deploy to Multiple Environments

Add separate workflows for staging and production:

```yaml
# secrets for staging
STAGING_TAG_VALUE: staging

# secrets for production
PROD_TAG_VALUE: production
```

### Limit Concurrent Deployments

```bash
for EC2_IP in "${IP_ARRAY[@]}"; do
  # Deploy
  ...
  # Wait X seconds before next
  sleep 10
done
```

### Send Notifications

```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS CLI EC2 describe-instances](https://docs.awsamazon.com/cli/latest/reference/ec2/describe-instances.html)
- [Docker Documentation](https://docs.docker.com/)
- [Docker GitHub Action](https://github.com/docker/build-push-action)
- [AWS Actions for GitHub](https://github.com/aws-actions/configure-aws-credentials)

---

## License

This project is provided as-is for educational purposes.

---

## Summary

You now have a **production-ready CI/CD pipeline** that:
✅ Automatically builds Docker images
✅ Pushes to DockerHub with version tags
✅ Discovers EC2 instances dynamically using AWS tags
✅ Deploys without hardcoded IPs
✅ Performs health checks on all instances
✅ Scales automatically with new instances

The key innovation is using AWS CLI + tags instead of hardcoded secrets!
# DEVOPS_ASSIGNMENT
