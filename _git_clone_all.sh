#!/bin/bash

source ./_git_repos.sh

gitroot="https://gitlab.com/exo-one"
if [[ -n "$SVST_DEV" ]]; then
  gitroot="git@gitlab.com:exo-one"
fi

for repo in ${repos[@]}; do
  git clone "$gitroot/$repo"
  if [[ -n "$CI_BUILD_REF_NAME" ]]; then
    echo "ls-ing in $(pwd)"
    ls
    cd "$repo"
    echo "ls-ing in $(pwd)"
    ls
    echo "Checking out $CI_BUILD_REF_NAME based on env variable CI_BUILD_REF_NAME"
    echo "THIS IS NOT GUARENTEED TO BE THE SAME BRANCH!!! AND MAY FAIL IN FUTURE"
    git checkout "$CI_BUILD_REF_NAME"
    cd ..
    echo "ls-ing in $(pwd)"
    ls
  fi
done
