import argparse
from curses import meta
from datetime import datetime
import enum
import json
from pkgutil import extend_path
from pydoc import classname
import shutil
import markdown
import os
import urllib
import os.path
import re

from python.util import *
from python.html import *


html_dir = 'public'


def html_name(md_filename):
    *filename, ext = md_filename.rsplit('.')
    name = '.'.join(filename)
    return '{}.html'.format(name)


def strip_file_metadata(path):
    file_meta = {'tags': [], 'data': '', 'summary': 'No Summary Provided!'}
    content = ''
    with open(path) as f:
        for line in f:
            if line.startswith('%tags'):
                try:
                    file_meta['tags'] = [i.strip() for i in re.split(r',\s+', line[5:]) if i]
                except (IndexError) as e:
                    raise ValueError('Invalid tag metadata') from e
            elif line.startswith('%date'):
                try:
                    # validate date by parsing
                    file_meta['date'] = datetime.fromisoformat(line[5:]).isoformat()
                except (IndexError, ValueError, TypeError) as e:
                    raise ValueError('Invalid date metadata') from e
            elif line.startswith('%summary'):
                try:
                    file_meta['summary'] = line[len('%summary'):].strip()
                except IndexError as e:
                    raise ValueError("Invalid summary metadata") from e
            else:
                content += line + '\n'

    if 'date' not in file_meta:
        s = os.stat(path)
        file_meta['date'] = datetime.fromtimestamp(s.st_birthtime).isoformat()

    return file_meta, content


def write_index(content):
    with open(os.path.join('private', 'index.html.template')) as f:
        template = f.read()

    with open(os.path.join(html_dir, 'index.html'), 'w') as f:
        f.write(style(template).replace('%{{content}}', content))


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-k', '--keep', action='store_true', help='DO not clean public dir before building')
    return ap.parse_args()


def main():
    options = parse_args()

    if not options.keep:
        print('[*] Cleaning public dir')
        shutil.rmtree(html_dir)
        print('[*] Re-creating public dir')
        os.mkdir(html_dir)

    index_content = ''
    blog_meta = {}
    print('[*] Building HTML files from Markdown')
    listing = os.listdir('source')
    lastidx = len(listing) - 1
    for i, file in enumerate(listing):
        print("\t{} '{}'".format('\u2517' if i == lastidx else '\u2523', file))
        path = os.path.join('source', file)
        blog_meta[file], file_content = strip_file_metadata(path)
        file_content = re.sub(r'\n([^\n])', r'\1', file_content)
        index_content += index_entry(html_name(file), blog_meta[file])
        html = markdown.markdown(file_content, extensions=['fenced_code', 'codehilite', 'toc'])
        with (open(os.path.join(html_dir, html_name(file)), 'w') as f,
                open(os.path.join('private', 'article.html.template')) as g):
            f.write(style(g.read()).replace("%{{content}}", html).replace('%{{title}}', titlify(file)))

    print("[*] Creating index file")
    write_index(index_content)

    print("[*] Serializing metadata")
    serialize(blog_meta, 'public', 'metadata')


if __name__ == '__main__':
    raise SystemExit(main())
