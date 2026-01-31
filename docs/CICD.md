# CI/CD with GitHub Actions

## Overview
Automatic Docker image building and pushing to Docker Hub using GitHub Actions.

## Workflow Triggers

The CI/CD pipeline triggers on:

1. **Push to main branch** - When code changes are pushed
2. **Pull Request** - When a PR is created
3. **Manual Trigger** - Via workflow_dispatch in GitHub Actions UI

### Files that trigger the workflow:
- `Dockerfile`
- `docker-compose.yml`
- `src/**` (any source code changes)
- `requirements.txt`
- `.github/workflows/docker-build.yml`

## Setup Instructions

### 1. Create Docker Hub Account

1. Sign up at https://hub.docker.com/
2. Create an access token (recommended):
   - Go to Account Settings → Security
   - Click "New Access Token"
   - Description: `github-actions`
   - Access permissions: `Read, Write, Delete`

### 2. Configure GitHub Repository

#### Add GitHub Variable (DOCKER_USERNAME)
1. Go to repository Settings → Secrets and variables → Actions
2. Click "Variables" tab
3. Click "New repository variable"
4. Name: `DOCKER_USERNAME`
5. Value: Your Docker Hub username
6. Click "Add variable"

#### Add GitHub Secret (DOCKER_PASSWORD)
1. Go to repository Settings → Secrets and variables → Actions
2. Click "Secrets" tab
3. Click "New repository secret"
4. Name: `DOCKER_PASSWORD`
5. Value: Your Docker Hub access token (or password)
6. Click "Add secret"

### 3. Update Image Name (Optional)

If your Docker Hub username is different from the default, update the workflow:

```yaml
# In .github/workflows/docker-build.yml
env:
  DOCKER_IMAGE: your-custom-name  # Change from 'news-alert'
```

### 4. Push to GitHub

```bash
# Add remote if not exists
git remote add origin https://github.com/your-username/news-alert.git

# Push changes
git push origin main
```

## Workflow Outputs

### Image Tags

The workflow generates multiple tags:

| Tag | Description | Example |
|-----|-------------|---------|
| `latest` | Latest build from main branch | `username/news-alert:latest` |
| `main-<sha>` | Commit SHA for tracking | `username/news-alert:main-abc1234` |
| `pr-<number>` | Pull request builds | `username/news-alert:pr-42` |

### Example Build URL

```
https://github.com/your-username/news-alert/actions
```

## Docker Hub Usage

### Pull the image

```bash
docker pull your-username/news-alert:latest
```

### Use in docker-compose

```yaml
services:
  news-alert:
    image: your-username/news-alert:latest
    # ... rest of configuration
```

## Local Testing

Before pushing, test the Docker build locally:

```bash
# Build image
docker build -t news-alert:test .

# Test run
docker run --rm --env-file .env news-alert:test

# If working, push manually
docker tag news-alert:test your-username/news-alert:latest
docker push your-username/news-alert:latest
```

## Troubleshooting

### Build fails with "unauthorized"

**Problem:** Docker credentials incorrect

**Solution:**
1. Verify `DOCKER_USERNAME` variable is correct
2. Regenerate Docker Hub token
3. Update `DOCKER_PASSWORD` secret

### Push fails with "denied"

**Problem:** No permission to push to repository

**Solution:**
1. Create the repository on Docker Hub first
2. Or ensure your token has Write permissions

### Workflow not triggering

**Problem:** Workflow doesn't run on push

**Solution:**
1. Check if file paths match trigger conditions
2. Verify workflow file is in `.github/workflows/` directory
3. Check Actions tab for errors

### Image tags not updating

**Problem:** `latest` tag not updating

**Solution:**
1. Check if push happened to `main` branch
2. Verify `DOCKER_USERNAME` variable matches your Docker Hub username
3. Check build logs for errors

## Workflow Status Badge

Add to your README.md:

```markdown
[![Docker Build](https://github.com/your-username/news-alert/actions/workflows/docker-build.yml/badge.svg)](https://github.com/your-username/news-alert/actions/workflows/docker-build.yml)
```

## Docker Pull Badge

Add to README.md:

```markdown
[![Docker Pulls](https://img.shields.io/docker/pulls/your-username/news-alert)](https://hub.docker.com/r/your-username/news-alert)
```

## Security Best Practices

1. **Use Access Tokens**: Never use actual password, use access tokens
2. **Rotate Tokens**: Regularly rotate Docker Hub tokens
3. **Limit Permissions**: Give tokens only necessary permissions
4. **Monitor Logs**: Check GitHub Actions logs for suspicious activity
5. **Private Images**: Use private repos for sensitive images

## Advanced: Multi-Platform Builds

To support multiple architectures (amd64, arm64), update the workflow:

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64
    push: true
    # ... rest of config
```

## Related Files

- [`.github/workflows/docker-build.yml`](../.github/workflows/docker-build.yml) - Workflow definition
- [`Dockerfile`](../Dockerfile) - Container image definition
- [`docker-compose.yml`](../docker-compose.yml) - Local development
- [`.env.example`](../.env.example) - Environment variables template
