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

BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD) # should be the same as GIT_REF
COMMIT_SHA=$(git rev-parse HEAD)

DOCKER_TAG="${DOCKER_IMAGE_NAME}:${BRANCH_NAME}"
DOCKER_TAG_WITH_HASH="${DOCKER_IMAGE_NAME}:${BRANCH_NAME}-${COMMIT_SHA:0:7}"

docker build  --tag "${DOCKER_TAG}" --tag "${DOCKER_TAG_WITH_HASH}" --file "${DOCKERFILE}" .

echo "$DOCKER_PASSWORD" | docker login $DOCKER_REGISTRY --username "$DOCKER_USERNAME" --password-stdin

docker push "${DOCKER_TAG_WITH_HASH}"
docker push "${DOCKER_TAG}"
