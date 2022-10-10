#! /usr/bin/env python3
import datetime
from fileinput import filename
import shutil
import os
import os.path
import sys
import urllib.parse
import re

def filename_from_link(link):
    parts = urllib.parse.urlsplit(link).path.split('/')
    file = parts[-1]
    file = urllib.parse.unquote(file)
    return file


def md_from_link(link):
    return filename_from_link(link).removesuffix('.html') + '.md'


def html_from_link(link):
    return filename_from_link(link)


def main():
    title = input("Enter the title of the post to create: ").strip()
    title = re.sub(r'[^a-zA-Z0-9.,+_-]', '-', title)

    destination = os.path.join('source', '{}.md'.format(title))
    if os.path.exists(destination):
        confirm = input("Article exists! Overwrite? (y/n) ").strip().lower()
        if not confirm.startswith('y'):
            print("Abort!")
            return

    if len(sys.argv) <= 1 or (len(sys.argv) > 1 and sys.argv[1] != '-q'):
        tags = input("Enter comma separated tags: ")
        summary = input("Enter article summary: ")
    else:
        tags = summary = ''

    with open(os.path.join('private', 'article.md.template')) as f:
        template = f.read()

    template = (template.replace('@{{title}}', title.title())
                .replace('@{{tags}}', tags)
                .replace('@{{summary}}', summary)
                .replace('@{{date}}', datetime.datetime.now().isoformat())
                )

    with open(destination, 'w') as g:
        g.write(template)

    print('Created "{}"'.format(destination))


if __name__ == '__main__':
    raise SystemExit(main())
