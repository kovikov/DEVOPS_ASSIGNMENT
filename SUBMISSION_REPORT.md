# DevOps Assignment Submission Report

## 1) Student Details
- Name: Rene Fondufe
- Student ID: [Your student ID]
- Module: [Module name/code]
- Tutor: [Tutor name]
- Submission Date: [DD/MM/YYYY]
- Repository URL: https://github.com/kovikov/DEVOPS_ASSIGNMENT.git
- Final Commit Hash: e6b7928

---

## 2) Project Overview
This project implements an end-to-end CI/CD pipeline for a Flask load-balancer application using GitHub Actions, DockerHub, and AWS EC2.

### Objective
Automate build, container image publishing, and deployment to EC2 instances with validation checks.

### Scope
- Continuous Integration: build and push Docker image
- Continuous Deployment: deploy latest image to EC2
- Post-deployment checks: health endpoint and verification

---

## 3) Architecture Summary
### Components
- Source code repository (GitHub)
- CI workflow (GitHub Actions)
- Container registry (DockerHub)
- CD workflow (GitHub Actions + AWS CLI)
- Deployment target (AWS EC2 + Docker)

### Deployment Flow
1. Push to main branch triggers CI workflow.
2. CI builds Docker image and pushes tags to DockerHub.
3. Successful CI triggers CD workflow.
4. CD authenticates to AWS, discovers target EC2 instance, and deploys via SSH.
5. Workflow runs health checks and reports status.

---

## 4) What I Implemented
### CI (Build and Push)
- Configured GitHub Actions workflow to:
  - Check out source
  - Set up Docker Buildx
  - Authenticate to DockerHub via secrets
  - Build and push image with `latest` and commit SHA tags

### CD (Deploy to EC2)
- Configured workflow to:
  - Trigger after successful CI
  - Validate AWS credentials
  - Resolve EC2 target instance
  - Set up SSH key securely from GitHub Secrets
  - Pull latest image and restart container
  - Execute health checks and deployment verification

---

## 5) Secrets and Security
### Secrets Used
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `EC2_SSH_KEY_B64`
- `EC2_USER`
- `EC2_INSTANCE_ID`

### Security Practices Applied
- Stored credentials in GitHub repository secrets (not hardcoded)
- Used SSH key secret for remote deployment
- Avoided exposing sensitive values in logs
- Rotated/replaced any accidentally exposed key material

---

## 6) Validation Evidence
### Successful Pipeline Runs
- CI workflow status: Pass (latest run)
- CD workflow status: Pass (latest run)
- Date/time of successful run: [add exact timestamp from GitHub Actions]

### Runtime Verification
- App endpoint: `http://<EC2_PUBLIC_IP>/`
- Health endpoint: `http://<EC2_PUBLIC_IP>/health`
- Expected health result: HTTP 200

### Attachments (Screenshots)
1. CI workflow successful run
2. CD workflow successful run
3. `/health` endpoint success response

---

## 7) Issue Encountered and Resolution
### Issue
CD deployment failed due to SSH key handling and target host resolution issues during workflow execution.

### Root Cause
The deployment workflow required a properly encoded SSH private key secret and a valid target EC2 instance context. Earlier runs failed before deployment because these prerequisites were not correctly aligned.

### Fix Applied
I updated the workflow and secrets setup to use `EC2_SSH_KEY_B64`, validated key decoding and key format checks in the pipeline, and ensured deployment targeted the correct running EC2 instance.

### Verification
I re-ran the workflows and confirmed CI completed successfully, CD completed successfully, and health checks passed on the deployed application.

---

## 8) Reflection
- What worked well: [short points]
- What I learned: [short points]
- Improvements if extended:
  - Add rollback strategy
  - Add staging environment
  - Add monitoring/alerts

---

## 9) Conclusion
The project successfully demonstrates automated CI/CD for a containerized Flask application, including secure secret handling, automated deployment to EC2, and post-deployment validation.

---

## 10) Final Submission Checklist
- [ ] Student details completed (ID, module, tutor, date)
- [ ] Repository URL and final commit hash verified
- [ ] CI and CD latest successful runs confirmed in GitHub Actions
- [ ] Exact success timestamp added from GitHub Actions
- [ ] Three screenshots attached:
  - [ ] CI success run
  - [ ] CD success run
  - [ ] `/health` endpoint showing success (HTTP 200)
- [ ] Report exported/submitted in required format (PDF/Doc/Markdown as requested)

---

## 11) Demo Script (2–3 Minutes)
Hello, my name is Rene Fondufe. This project demonstrates a full CI/CD pipeline for a Flask load-balancer app using GitHub Actions, DockerHub, and AWS EC2.

First, when I push code to `main`, the CI workflow runs. It checks out the repository, builds the Docker image, and pushes it to DockerHub with both the `latest` tag and a commit-specific tag.

After CI succeeds, the CD workflow is triggered automatically. The CD pipeline validates AWS credentials, identifies the EC2 target, connects over SSH using a secret-managed key, pulls the latest Docker image, and restarts the container.

Then the workflow runs health checks against the deployed app endpoint to confirm the deployment is successful. In the Actions tab, the latest CI and CD runs are both successful.

One issue I encountered was deployment failure due to SSH key/target setup. I fixed this by correcting secret formatting and validation in the pipeline, then re-ran the workflows to confirm successful deployment and health checks.

In summary, the pipeline now provides automated build, deployment, and validation with secure secret handling and repeatable deployment steps.

---

## 12) Declaration
I confirm that this submission reflects my implementation, testing, and understanding of the pipeline presented in the repository.

Signed: Rene Fondufe
Date: [DD/MM/YYYY]
