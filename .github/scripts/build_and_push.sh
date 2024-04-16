#!/bin/bash
set -xe

REPO_URL="https://github.com/karpatkey/roles_royce.git"

# pass as environment variables
# GIT_REF= #GITHUB_REF
# DOCKER_REGISTRY="your_registry_url" ${{ secrets.XXX }}
# DOCKER_USERNAME="your_docker_username"
# DOCKER_PASSWORD="your_docker_password"

git clone $REPO_URL repo
cd repo
git checkout $GIT_REF

BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD | sed 's/[^a-zA-Z0-9]/-/g')  # should be the same as GIT_REF
COMMIT_SHA=$(git rev-parse HEAD)

DOCKER_TAG="${DOCKER_IMAGE_NAME}:${BRANCH_NAME}"
DOCKER_TAG_WITH_HASH="${DOCKER_IMAGE_NAME}:${BRANCH_NAME}-${COMMIT_SHA:0:7}"

mkdir -p kaniko/.docker
echo "{\"auths\":{\"$DOCKER_REGISTRY\":{\"username\":\"$DOCKER_USERNAME\",\"password\":\"$DOCKER_PASSWORD\"}}}" > kaniko/.docker/config.json

docker run --rm -v $(pwd):/workspace -v $(pwd)/kaniko/.cache:/cache -v $(pwd)/kaniko/.docker:/kaniko/.docker \
  gcr.io/kaniko-project/executor:latest \
  --context . \
  --dockerfile "$DOCKERFILE" \
  --destination "$DOCKER_TAG" \
  --destination "$DOCKER_TAG_WITH_HASH" \
  --cache=true \
  --cache-dir=/cache \
  --cache-copy-layers \
  --cache-repo="$DOCKER_IMAGE_NAME" \
  --insecure --skip-tls-verify-pull

echo "Image pushed to registry: $DOCKER_TAG"