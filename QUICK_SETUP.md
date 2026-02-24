# Quick Setup Guide

## 🚀 5-Minute Setup

### 1. GitHub Secrets (5 minutes)
Go to **Settings → Secrets and variables → Actions** and add:

```
DOCKERHUB_USERNAME=your_dockerhub_username
DOCKERHUB_TOKEN=dckr_pat_xxxxx
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=xxxxx
AWS_REGION=us-east-1
EC2_SSH_KEY=[contents of your .pem file]
EC2_USER=ec2-user
EC2_TAG_KEY=Environment
EC2_TAG_VALUE=production
```

### 2. AWS EC2 Setup
Tag your running instances:
```bash
aws ec2 create-tags \
  --resources i-xxxxx \
  --tags Key=Environment,Value=production
```

### 3. Push to GitHub
```bash
git add .
git commit -m "Add CI/CD pipeline"
git push origin main
```

### 4. Monitor Deployment
- Go to **Actions** tab in GitHub
- Watch CI workflow build
- Watch CD workflow deploy

### 5. Verify
```bash
# Get instance IPs
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[*].Instances[*].PublicIpAddress' \
  --output text

# Test the app
curl http://[IP]/health
curl http://[IP]/
```

---

## 🔑 Getting Your Secrets

### DockerHub Token
1. Go to https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Name it `github-actions`
4. Copy the token

### AWS Access Keys
```bash
aws iam create-access-key --user-name github-actions

# Shows:
# {
#     "AccessKey": {
#         "AccessKeyId": "AKIA...",
#         "SecretAccessKey": "xxxxx..."
#     }
# }
```

### EC2 Private Key
```bash
# Show contents
cat ~/.ssh/your-key.pem

# Copy EVERYTHING including BEGIN and END lines
```

---

## 🧪 Test Workflow

### 1. Test CI (Build)
```bash
git commit --allow-empty -m "Trigger CI"
git push origin main

# Watch Actions tab
# Should see "CI - Build and Push Docker Image" running
```

### 2. Test CD (Deploy)
CD runs automatically after CI succeeds
- Watch "Actions" tab
- Should see "CD - Deploy to EC2 using AWS CLI" running
- Check instance `/health` endpoint returns 200

### 3. Verify Deployment
```bash
# Get IPs from AWS
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[*].Instances[*].PublicIpAddress' \
  --output text

# Test each IP
curl http://10.2.3.4/
curl http://10.2.3.5/
```

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| "No instances found" | Check EC2_TAG_KEY and EC2_TAG_VALUE match your instance tags |
| SSH timeout | Verify security group allows SSH (port 22) |
| Docker pull fails | Ensure Docker is running on EC2 (`sudo systemctl start docker`) |
| Health check fails | Check container logs: `sudo docker logs load-balancer-app` |

---

## 📋 Checklist

- [ ] DockerHub account created
- [ ] AWS IAM user created
- [ ] EC2 instances have tags
- [ ] EC2 instances have Docker installed
- [ ] GitHub repository created
- [ ] All 9 secrets added
- [ ] Code pushed to main branch
- [ ] Actions completed successfully

---

## 🎯 How It Works

```
Code Push to main
    ↓
CI: Build & Push Docker Image to DockerHub ✓
    ↓
CD: (triggered on CI success)
    ├─ Configure AWS Credentials
    ├─ Query EC2 by Tag (Environment=production)
    ├─ SSH into Each Instance
    ├─ Pull Latest Image
    ├─ Stop Old Container
    ├─ Run New Container
    ├─ Health Check
    └─ Verify Deployment ✓
```

---

## 📞 Need Help?

1. Check GitHub Actions **Logs** for detailed error messages
2. Verify all 9 secrets are present (no typos)
3. Test AWS CLI locally: `aws ec2 describe-instances`
4. SSH to instance manually: `ssh -i key.pem ec2-user@ip`
5. Check Docker on instance: `sudo docker ps`

Good luck! 🚀
