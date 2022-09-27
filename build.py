import argparse
from datetime import datetime
import math
import shutil
import markdown
import os
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
    file_meta = {'tags': [], 'data': '', 'summary': 'No Summary Provided!', "needs_toc": False}
    content = ''
    sections = 0
    title_set = False
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
                if re.match(r'#[^#]', line):
                    if title_set:
                        raise ValueError("Too Many Level 1 Headings: '{}'".format(line))
                    content += '{TOC_EMBED}'
                    title_set = True
                elif line.startswith('##'):
                    sections += 1

    if 'date' not in file_meta:
        s = os.stat(path)
        file_meta['date'] = datetime.fromtimestamp(s.st_birthtime).isoformat()

    if sections > 4:
        file_meta['needs_toc'] = True
        content = content.format(TOC_EMBED='[TOC]')
    else:
        content = content.format(TOC_EMBED='')

    return file_meta, content


def write_index(content):
    with open(os.path.join('private', 'index.html.template')) as f:
        template = f.read()

    with open(os.path.join(html_dir, 'index.html'), 'w') as f:
        f.write(fill_includes(style(template).replace('%{{content}}', content)))


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-k', '--keep', action='store_true', help='DO not clean public dir before building')
    return ap.parse_args()


def add_tags(tags, meta, file):
    for tag in meta['tags']:
        lst = tags.get(tag, [])
        lst.append({'link': linkify(html_name(file)), 'title': titlify(file), 'internal_content': index_entry(html_name(file), meta)})
        tags[tag] = lst


def fill_includes(text):
    def file_replacer(match):
        try:
            name_prefix = match.group(1)
        except (AttributeError, IndexError) as e:
            raise ValueError("Invalid @include directive '{}'".format(match)) from e

        filename = '{}.html.partial'.format(name_prefix)
        try:
            with open(os.path.join('private', filename)) as f:
                return f.read()
        except (FileNotFoundError) as e:
            raise ValueError("Invalid @include directive '{}': File not found".format(match.group())) from e
        except OSError as e:
            raise ValueError("Invalid @include directive '{}'. Could not access file".format(match.group())) from e

    text = re.sub(r'@include\s+(\w+)', file_replacer, text)
    return text


def fill_template(template, file, content, meta):
    text = (style(template)
            .replace("%{{content}}", content)
            .replace('%{{title}}', titlify(file))
            .replace('%{{tags}}', tags_for_file(file, meta))
            )

    text = fill_includes(text)
    return text


def main():
    options = parse_args()

    if not options.keep:
        print('[*] Cleaning public dir')
        shutil.rmtree(html_dir)
        print('[*] Re-creating public dir')
        os.mkdir(html_dir)

    index_content = ''
    blog_meta = {}
    tag_data = {}
    print('[*] Building HTML files from Markdown')
    listing = os.listdir('source')
    lastidx = len(listing) - 1
    for i, file in enumerate(listing):
        print("\t{} '{}'".format('\u2517' if i == lastidx else '\u2523', file))
        path = os.path.join('source', file)
        blog_meta[file], file_content = strip_file_metadata(path)
        add_tags(tag_data, blog_meta[file], file)
        file_content = re.sub(r'\n([^\n])', r'\1', file_content)
        index_content += index_entry(html_name(file), blog_meta[file])
        html = markdown.markdown(file_content, extensions=['fenced_code', 'codehilite', 'toc'])
        with (open(os.path.join(html_dir, html_name(file)), 'w') as f,
                open(os.path.join('private', 'article.html.template')) as g):
            text = fill_template(g.read(), file, html, blog_meta[file])
            f.write(text)

    print("[*] Creating index file")
    write_index(index_content)

    print("[*] Serializing metadata")
    serialize(blog_meta, 'public', 'metadata')

    print('[*] Writing tag database')
    serialize(tag_data, 'public', 'tags')

    print('[*] Preparing Search Template')
    with (open(os.path.join('private', 'search.html.template')) as f,
          open(os.path.join('public', 'search.html'), 'w') as g):
        g.write(fill_includes(style(f.read())))


if __name__ == '__main__':
    raise SystemExit(main())
