# AWS CLI Reference Commands

Quick reference for AWS CLI commands used in this project.

## 🏷️ EC2 Tagging Commands

### View all instances with tags
```bash
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name,Tags[?Key==`Name`].Value|[0],Tags]' \
  --output table
```

### Add tags to instances
```bash
aws ec2 create-tags \
  --resources i-1234567890abcdef0 \
  --tags Key=Environment,Value=production Key=Application,Value=load-balancer
```

### Update a tag
```bash
aws ec2 create-tags \
  --resources i-1234567890abcdef0 \
  --tags Key=Environment,Value=staging
```

### View tags on specific instance
```bash
aws ec2 describe-tags \
  --filters "Name=resource-id,Values=i-1234567890abcdef0" \
  --output table
```

### Delete a tag
```bash
aws ec2 delete-tags \
  --resources i-1234567890abcdef0 \
  --tags Key=OldTagKey
```

---

## 🔍 Query Instances by Tags

### Get all IPs for instances with specific tag
```bash
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[*].Instances[*].PublicIpAddress' \
  --output text
```

**Output:**
```
10.2.3.4 10.2.3.5 10.2.3.6
```

### Get private IPs instead
```bash
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[*].Instances[*].PrivateIpAddress' \
  --output text
```

### Get running instances only
```bash
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
            "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].PublicIpAddress' \
  --output text
```

### Get instances with multiple tags (AND filter)
```bash
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
            "Name=tag:Type,Values=load-balancer" \
            "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].PublicIpAddress' \
  --output text
```

### Get instance details (ID, IP, State, Tags)
```bash
aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[*].Instances[*].[InstanceId,PublicIpAddress,State.Name,Tags[?Key==`Name`].Value|[0]]' \
  --output table
```

---

## 🚀 Instance Management

### Start instances
```bash
aws ec2 start-instances --instance-ids i-xyz i-abc

# Wait for them to start
aws ec2 wait instance-running --instance-ids i-xyz
```

### Stop instances
```bash
aws ec2 stop-instances --instance-ids i-xyz i-abc
```

### Terminate instances (delete)
```bash
aws ec2 terminate-instances --instance-ids i-xyz
```

### Get instance status
```bash
aws ec2 describe-instances \
  --instance-ids i-xyz \
  --query 'Reservations[0].Instances[0].[State.Name,PublicIpAddress]' \
  --output table
```

---

## 🔐 Security Group Commands

### View security group rules
```bash
aws ec2 describe-security-groups \
  --group-ids sg-xxxxxxxxx \
  --query 'SecurityGroups[0].IpPermissions' \
  --output table
```

### Allow SSH (port 22)
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0
```

### Allow HTTP (port 80)
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
```

### Allow HTTPS (port 443)
```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

### Revoke rule
```bash
aws ec2 revoke-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0
```

---

## 👤 IAM User Management

### Create IAM user
```bash
aws iam create-user --user-name github-actions
```

### Create access keys
```bash
aws iam create-access-key --user-name github-actions
```

**Output:**
```json
{
  "AccessKey": {
    "AccessKeyId": "AKIA...",
    "SecretAccessKey": "xxxxx...",
    "Status": "Active",
    "CreateDate": "2026-02-23T..."
  }
}
```

### List access keys
```bash
aws iam list-access-keys --user-name github-actions
```

### Delete access key
```bash
aws iam delete-access-key \
  --user-name github-actions \
  --access-key-id AKIA...
```

### Attach policy to user
```bash
# Attach EC2 read-only policy
aws iam attach-user-policy \
  --user-name github-actions \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess

# Attach full EC2 policy
aws iam attach-user-policy \
  --user-name github-actions \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess
```

### List attached policies
```bash
aws iam list-attached-user-policies --user-name github-actions
```

---

## 🌐 Useful Queries

### List all instances in current region
```bash
aws ec2 describe-instances --output table
```

### List all tags in use
```bash
aws ec2 describe-tags \
  --output table
```

### Find instance by name
```bash
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=MyServer" \
  --output table
```

### Count instances by status
```bash
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[].[InstanceId,State.Name]' | grep -c "running"
```

### Export instance list to CSV
```bash
aws ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,PublicIpAddress,State.Name,LaunchTime]' \
  --output csv > instances.csv
```

---

## 🔧 Common Patterns

### Loop through instances and SSH
```bash
INSTANCES=$(aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[*].Instances[*].PublicIpAddress' \
  --output text)

for IP in $INSTANCES; do
  ssh -i your-key.pem ec2-user@$IP "docker ps"
done
```

### Get IPs and run command on all
```bash
INSTANCES=$(aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[*].Instances[*].PublicIpAddress' \
  --output text)

for IP in $INSTANCES; do
  echo "Running on $IP:"
  curl http://$IP/health
done
```

### Update tag on all matching instances
```bash
INSTANCE_IDS=$(aws ec2 describe-instances \
  --filters "Name=tag:Environment,Values=production" \
  --query 'Reservations[*].Instances[*].InstanceId' \
  --output text)

aws ec2 create-tags \
  --resources $INSTANCE_IDS \
  --tags Key=LastDeployed,Value=$(date -u +%Y-%m-%dT%H:%M:%SZ)
```

---

## 📊 Useful Options

### Format output options
```bash
--output json       # JSON format
--output text       # Space-separated values
--output table      # Nice ASCII table
--output csv        # Comma-separated (for Excel)
```

### Filter options
```bash
# Multiple values (OR)
--filters "Name=tag:Environment,Values=production,staging"

# Multiple filters (AND)
--filters "Name=tag:Environment,Values=production" \
          "Name=instance-state-name,Values=running"
```

### Query options (JMESPath)
```bash
# Get specific fields
--query 'Reservations[*].Instances[*].[InstanceId,State.Name]'

# Get values only
--query 'Reservations[*].Instances[*].PublicIpAddress'

# Flatten results
--query 'Reservations[].Instances[].PublicIpAddress'
```

---

## 🆘 Debugging

### Check configured credentials
```bash
aws sts get-caller-identity
```

**Output:**
```json
{
  "UserId": "AIDAI...",
  "Account": "123456789012",
  "Arn": "arn:aws:iam::123456789012:user/github-actions"
}
```

### Check current region
```bash
aws configure get region
```

### List configured profiles
```bash
aws configure list
```

### Test EC2 access
```bash
aws ec2 describe-instances --max-results 5
```

If this works, your credentials are valid!

---

## 📚 Resources

- [AWS EC2 CLI Reference](https://docs.aws.amazon.com/cli/latest/reference/ec2/)
- [AWS CLI JMESPath Queries](https://jmespath.org/)
- [AWS Tagging Best Practices](https://docs.aws.amazon.com/general/latest/gr/aws_tagging.html)
- [EC2 Instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Instances.html)
