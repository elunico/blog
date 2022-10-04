#!/bin/zsh

echo -n "Enter a commit message: "
read MESSAGE

python build.py && 
  git add . && 
  git commit -m "$MESSAGE" && 
  git push origin main && 
  #   git subtree split --rejoin --prefix public --ignore-joins
  git subtree push --prefix public origin gh-pages
