#!/bin/zsh

echo -n "Enter a commit message: "
read MESSAGE

python build.py && git subtree push --prefix public origin gh-pages && git add . && git commit -m "$MESSAGE" && git push origin main
