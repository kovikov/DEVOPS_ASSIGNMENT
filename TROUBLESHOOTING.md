# Troubleshooting & Error Resolutions

This guide includes common errors encountered in the original project and their resolutions, plus additional errors specific to this AWS CLI-based approach.

---

## 🔴 Error: "No instances found with the specified tags"

### Symptoms
```
❌ No instances found with the specified tags!
Tag Key: Environment
Tag Value: production
```

### Root Causes & Solutions

#### ❌ Cause 1: Instances don't have the tag
**Check:**
```bash
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name,Tags]' \
  --output table
```

**Fix:** Add tags to instances
```bash
aws ec2 create-tags \
  --resources i-1234567890abcdef0 \
  --tags Key=Environment,Value=production

# Verify tag was added
aws ec2 describe-tags \
  --filters "Name=resource-id,Values=i-1234567890abcdef0"
```

#### ❌ Cause 2: Wrong tag key/value names
**Your secret says:** `EC2_TAG_KEY=Environment`, `EC2_TAG_VALUE=production`
**Instance tag is:** `env=prod` (different key AND value)

**Fix:** Make them match
```bash
# Option 1: Change instance tags to match secrets
aws ec2 create-tags \
  --resources i-xxx \
  --tags Key=Environment,Value=production

# Option 2: Change secrets to match instance tags
# (Go to GitHub Settings → Secrets → Update EC2_TAG_KEY and EC2_TAG_VALUE)
```

#### ❌ Cause 3: Instance is stopped
**Check:**
```bash
aws ec2 describe-instances \
  --instance-ids i-xxx \
  --query 'Reservations[0].Instances[0].State.Name'
```

**Fix:** Start the instance
```bash
aws ec2 start-instances --instance-ids i-xxx
# Wait 30 seconds for it to fully start
```

#### ❌ Cause 4: Wrong AWS region
Your instances are in `us-west-2` but secret says `us-east-1`

**Fix:** Update AWS_REGION secret to match:
```bash
# Check current instances
aws ec2 describe-instances --region us-east-1

# If no instances show, try other regions
aws ec2 describe-instances --region us-west-2

# Update secret to matching region
```

---

## 🔴 Error: "ssh: connect to host 10.2.3.4 port 22: Connection timed out"

### Symptoms
```
ssh: connect to host 10.2.3.4 port 22: Connection timed out
Deployment failed for 10.2.3.4
```

### Root Causes & Solutions

#### ❌ Cause 1: Security group blocks SSH
**Fix:** Allow inbound SSH on port 22
```bash
# Get security group ID
aws ec2 describe-instances \
  --instance-ids i-xxx \
  --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
  --output text

# Add SSH rule
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# Or via AWS Console:
# 1. EC2 → Instances → Select instance
# 2. Security → Security groups
# 3. Edit inbound rules → Add SSH rule
```

#### ❌ Cause 2: Instance has no public IP
**Check:**
```bash
aws ec2 describe-instances \
  --instance-ids i-xxx \
  --query 'Reservations[0].Instances[0].PublicIpAddress'
```

If null/empty:

**Fix:** Associate Elastic IP or assign public IP
```bash
# Allocate new Elastic IP
aws ec2 allocate-address --domain vpc

# Associate it
aws ec2 associate-address \
  --instance-id i-xxx \
  --allocation-id eipalloc-xxx
```

#### ❌ Cause 3: Wrong SSH key
**Check:** Your GitHub secret has the wrong private key

**Fix:** 
```bash
# Find the correct key for your instance
ls ~/.ssh/

# View the public key from instance metadata
aws ec2 describe-instances \
  --instance-ids i-xxx \
  --query 'Reservations[0].Instances[0].KeyName'

# Gets KeyName (e.g., "my-key-pair")
# Match this with correct .pem file
cat ~/.ssh/my-key-pair.pem

# Update EC2_SSH_KEY secret with full contents
```

#### ❌ Cause 4: EC2_USER is wrong for your AMI
**Different AMIs use different default users:**

| AMI Type | Default User |
|----------|--------------|
| Amazon Linux | `ec2-user` |
| Ubuntu | `ubuntu` |
| Debian | `admin` |
| RHEL | `ec2-user` |
| Windows | N/A (use RDP) |

**Fix:**
```bash
# SSH manually to verify
ssh -i your-key.pem <POTENTIAL_USER>@10.2.3.4

# Works? Update EC2_USER secret to that user
```

#### ❌ Cause 5: Instance is in private subnet
Your instance has no public IP because it's in a private subnet

**Fix:** Either
1. Put instance in public subnet with public IP
2. Deploy from GitHub Actions via Bastion host / VPN
3. Use Systems Manager Session Manager instead of SSH

---

## 🔴 Error: "Docker daemon is not running"

### Symptoms
```
Cannot connect to Docker daemon at unix:///var/run/docker.sock
```

### Root Causes & Solutions

#### ❌ Cause 1: Docker service not started
**Check:**
```bash
ssh -i key.pem ec2-user@10.2.3.4 "sudo systemctl status docker"
```

**Fix:** Start Docker
```bash
ssh -i key.pem ec2-user@10.2.3.4 "sudo systemctl start docker"

# Enable auto-start on reboot
ssh -i key.pem ec2-user@10.2.3.4 "sudo systemctl enable docker"
```

#### ❌ Cause 2: Docker not installed
**Check:**
```bash
ssh -i key.pem ec2-user@10.2.3.4 "docker --version"
# If: command not found
```

**Fix:** Install Docker
```bash
ssh -i key.pem ec2-user@10.2.3.4 << 'EOF'
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
EOF
```

#### ❌ Cause 3: User doesn't have Docker permissions
**Check:**
```bash
ssh -i key.pem ec2-user@10.2.3.4 "docker ps"
# Error: permission denied
```

**Fix:** Add user to docker group
```bash
ssh -i key.pem ec2-user@10.2.3.4 << 'EOF'
sudo usermod -aG docker ec2-user
EOF

# Log out and log back in, OR use sudo for docker commands
```

---

## 🔴 Error: "permission denied while trying to connect to Docker daemon"

### Symptoms
```bash
Got permission denied while trying to connect to the Docker daemon socket at 
unix:///var/run/docker.sock: Post ... connect: permission denied
```

### Solution

**Fix:** All Docker commands need `sudo`

In workflow, change:
```bash
# ❌ This fails
docker pull image:tag
docker run ...

# ✅ Use sudo
sudo docker pull image:tag
sudo docker run ...
```

Our workflow already includes `sudo` for all Docker commands.

---

## 🔴 Error: "Host key verification failed"

### Symptoms
```
Host key verification failed.
The authenticity of host '10.2.3.4' can't be established.
```

### Solution

**This is already handled** in the workflow with:
```yaml
-o StrictHostKeyChecking=no
-o UserKnownHostsFile=/dev/null
```

If still occurring, verify these flags are in your SSH command:
```bash
ssh -T -i ~/.ssh/deploy_key.pem \
  -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null \
  ec2-user@10.2.3.4 << 'EOF'
  # commands
EOF
```

---

## 🔴 Error: "Connection refused" on health check

### Symptoms
```bash
curl: (7) Failed to connect to 10.2.3.4 port 80: Connection refused
```

### Root Causes & Solutions

#### ❌ Cause 1: Container didn't start
**Check:**
```bash
ssh -i key.pem ec2-user@10.2.3.4 "sudo docker ps"
# Shows no running load-balancer-app container
```

**Fix:** Check why it failed
```bash
ssh -i key.pem ec2-user@10.2.3.4 << 'EOF'
# View container logs
sudo docker logs load-balancer-app

# View exited containers
sudo docker ps -a

# Try running manually
sudo docker run -d -p 80:80 \
  your-username/load-balancer-app:latest
EOF
```

#### ❌ Cause 2: Application crashed
**Check logs:**
```bash
ssh -i key.pem ec2-user@10.2.3.4 "sudo docker logs -f load-balancer-app"
```

**Common Flask errors:**
```
ImportError: No module named 'flask'
# → Need to install requirements in Dockerfile

Address already in use
# → Port 80 still used by another container
```

**Fix:** Review Dockerfile and requirements.txt

#### ❌ Cause 3: Port not mapped correctly
**Check:**
```bash
ssh -i key.pem ec2-user@10.2.3.4 "sudo netstat -tlnp | grep 80"
```

Should show:
```
tcp  0  0 0.0.0.0:80  0.0.0.0:*  LISTEN  1234/docker
```

**Fix:** Ensure run command has: `-p 80:80`

#### ❌ Cause 4: Container IP is wrong
**Container may be bound to localhost instead of 0.0.0.0**

**Fix:** In app.py:
```python
# ❌ Wrong - only localhost
app.run(host='127.0.0.1', port=80)

# ✅ Correct - all interfaces
app.run(host='0.0.0.0', port=80)
```

---

## 🔴 Error: "HTTP 200 OK, but response is empty"

### Symptoms
```bash
Status: 200
# But curl returns nothing
```

### Root Causes & Solutions

#### ❌ Cause 1: Whitespace in IP address
**Fix:** As done in workflow:
```bash
HOST=$(echo "${{ secrets.EC2_HOST }}" | tr -d '[:space:]')
```

We've already implemented this in the workflow by trimming IPs from AWS CLI.

#### ❌ Cause 2: Application not returning proper JSON
**Check app.py:**
```python
# ✅ Good
return jsonify({'status': 'running'}), 200

# ❌ Could be problematic
print('status: running')  # Prints to server, not returned
```

---

## 🔴 Error: "No route to host"

### Symptoms
```
No route to host
```

### Causes

1. **Instance is down**
   ```bash
   aws ec2 describe-instances --instance-ids i-xxx
   # Check State: should be 'running'
   ```

2. **Wrong IP format**
   ```bash
   # Make sure it's a valid IP
   echo "10.2.3.4" | grep -E "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$"
   ```

3. **Network ACL blocking traffic**
   Check VPC → Network ACLs → Ensure port 80 is allowed

### Solution

```bash
# Test connectivity
ping 10.2.3.4

# If ping works but curl doesn't, check security group
aws ec2 describe-security-groups --group-ids sg-xxx

# Ensure HTTP (80) and SSH (22) are allowed
```

---

## 🔴 Error: "Failed to pull image from DockerHub"

### Symptoms
```
Error response from daemon: pull access denied for your-username/load-balancer-app
```

### Root Causes & Solutions

#### ❌ Cause 1: Image doesn't exist on DockerHub
The CI workflow failed to push the image

**Check:**
- Go to https://hub.docker.com/r/your-username/load-balancer-app
- If repo doesn't exist, CI failed
- Check Actions tab for CI workflow errors

**Fix:** 
1. Ensure CI workflow ran successfully
2. Check DOCKERHUB_TOKEN secret is valid
3. Re-run CI workflow

#### ❌ Cause 2: Private image without credentials
Image exists but is private and Docker isn't logged in

**Fix:** Log in to DockerHub on EC2
```bash
ssh -i key.pem ec2-user@10.2.3.4 << 'EOF'
# Log in to DockerHub
docker login
# Enter username and password (or token)

# Now try pulling
sudo docker pull your-username/load-balancer-app:latest
EOF
```

#### ❌ Cause 3: Wrong image name/tag
Your workflow pushes as `your-username/load-balancer-app:latest`
But EC2 tries to pull `yourname/flask-app:v1.0`

**Fix:** Make sure image name matches exactly in workflow output

---

## 🔴 Error: "AWS CLI credentials not configured"

### Symptoms
```
Unable to locate credentials
```

### Solution

**Already handled** in workflow with:
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: ${{ secrets.AWS_REGION }}
```

If still failing:
1. Check all 3 secrets are set (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)
2. Verify secrets aren't empty
3. Test IAM user has EC2ReadOnly permissions

---

## 🔴 Error: "Workflow timeout"

### Symptoms
```
The action 'Deploy to EC2 instances' has timed out after 35 minutes
```

### Root Causes

1. **Image is very large**
   - Taking too long to download
   - Size: > 500MB

2. **Network is slow**
   - DockerHub download is slow
   - EC2 connection is slow

3. **Container is hanging**
   - App startup taking too long
   - Stuck at health check wait (20 seconds)

### Solutions

```bash
# Increase wait time in workflow
sleep 30  # Instead of 20

# Optimize Dockerfile to reduce size
FROM python:3.11-slim  # Instead of python:3.11
# Reduces from 800MB to 130MB

# Use multi-stage build
FROM python:3.11-slim as builder
# ... build stage ...
FROM python:3.11-slim
# Copy only what's needed
# Reduces to 50MB
```

---

## 📊 Workflow Monitoring Checklist

When deployment fails, check in this order:

- [ ] **GitHub Actions Log**
  - Go to Actions tab → Workflow run → Failed job
  - Read the red error message

- [ ] **AWS Credentials** (if AWS CLI step failed)
  - Verify all 3 secrets: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
  - Check IAM user exists and has permissions

- [ ] **EC2 Instances** (if instance query failed)
  - Instances exist and are running
  - Instances have correct tags
  - Tags match EC2_TAG_KEY and EC2_TAG_VALUE

- [ ] **SSH Access** (if deployment failed)
  - Security group allows inbound SSH on port 22
  - EC2_SSH_KEY secret has full private key content
  - EC2_USER matches AMI default user

- [ ] **Docker Setup** (if Docker commands failed)
  - Docker installed on instances
  - Docker service running
  - User has Docker permissions

- [ ] **Application** (if health check failed)
  - Docker container started: `sudo docker ps`
  - Check error logs: `sudo docker logs load-balancer-app`
  - App listens on correct port: `sudo netstat -tlnp | grep 80`

---

## 🆘 Still stuck?

1. **Enable debug logging:**
   ```yaml
   env:
     ACTIONS_STEP_DEBUG: true
   ```
   Re-run workflow for verbose output

2. **Test locally:**
   ```bash
   docker build -t test:latest .
   docker run -p 80:80 test:latest
   curl http://localhost/health
   ```

3. **Test AWS CLI:**
   ```bash
   aws configure
   aws ec2 describe-instances
   aws ec2 describe-instances --filters "Name=tag:Environment,Values=production"
   ```

4. **Check GitHub Status:**
   https://www.githubstatus.com/

5. **Contact Support:**
   - GitHub: https://github.com/support
   - AWS: https://console.aws.amazon.com/support/

Good luck! 🚀
