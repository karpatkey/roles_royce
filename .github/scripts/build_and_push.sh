#!/bin/bash
set -xe

REPO_URL="https://github.com/karpatkey/roles_royce.git"

# pass as environment variables
# GIT_REF= #GITHUB_REF
# DOCKER_REGISTRY="your_registry_url" ${{ secrets.XXX }}
# DOCKER_USERNAME="your_docker_username"
# DOCKER_PASSWORD="your_docker_password"

mkdir -p kaniko/.docker
echo "{\"auths\":{\"$DOCKER_REGISTRY\":{\"username\":\"$DOCKER_USERNAME\",\"password\":\"$DOCKER_PASSWORD\"}}}" > kaniko/.docker/config.json

git clone $REPO_URL repo
cd repo
git checkout $GIT_REF

BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD | sed 's/[^a-zA-Z0-9]/-/g')  # should be the same as GIT_REF
COMMIT_SHA=$(git rev-parse HEAD)

DOCKER_TAG="${DOCKER_IMAGE_NAME}:${BRANCH_NAME}"
DOCKER_TAG_WITH_HASH="${DOCKER_IMAGE_NAME}:${BRANCH_NAME}-${COMMIT_SHA:0:7}"

# docker pull $DOCKER_TAG || true
# docker build --cache-from=$DOCKER_TAG --tag "${DOCKER_TAG}" --tag "${DOCKER_TAG_WITH_HASH}" --file "${DOCKERFILE}" .

# echo "$DOCKER_PASSWORD" | docker login $DOCKER_REGISTRY --username "$DOCKER_USERNAME" --password-stdin

# docker push "${DOCKER_TAG_WITH_HASH}"
# docker push "${DOCKER_TAG}"

docker run --rm -v $(pwd):/workspace \
  -v /path/to/kaniko/.cache:/cache \ 
  -v kaniko/.docker:/kaniko/.docker \ 
  gcr.io/kaniko-project/executor:latest \
  --context "$CONTEXT_DIR" \
  --dockerfile "$DOCKERFILE" \
  --destination "$DOCKER_TAG_WITH_HASH" \
  --destination "$DOCKER_TAG" \
  --cache=true \
  --cache-dir=/cache \
  --cache-repo="$DOCKER_REGISTRY" \
  --cache-tag="$DOCKER_TAG" \
  --insecure --skip-tls-verify-pull

echo "Image pushed to registry: $REGISTRY_URL/$IMAGE_NAME:$IMAGE_TAG"