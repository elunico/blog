.PHONY: serve

deploy: build
	git add .
	git commit -m "Updating site with Makefile"
	git subtree push --prefix public origin gh-pages

build: *.py
	python3 build.py

serve:
	python3 -m http.server -p 8000 ./public
