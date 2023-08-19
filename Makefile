.PHONY: serve

deploy: pmain
	git subtree push --prefix public origin gh-pages

pmain: build
	git add .
	git commit -m "Updating with Makefile"
	git push origin main

build: *.py
	python3 build.py

serve:
	python3 -m http.server -p 8000 -d ./public
