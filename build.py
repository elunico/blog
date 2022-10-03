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


kBuildDirRoot = 'public'


def html_name(md_filename):
    *filename, ext = md_filename.rsplit('.')
    name = '.'.join(filename)
    return '{}.html'.format(name)


def clean(tag):
    return ''.join(i for i in tag if i.isalnum() or i == ' ')


def strip_file_metadata(path):
    file_meta = {'tags': [], 'data': '', 'summary': 'No Summary Provided!', "needs_toc": False}
    content = ''
    sections = 0
    title_set = False
    with open(path) as f:
        for line in f:
            if line.startswith('%tags'):
                try:
                    file_meta['tags'] = [clean(i.strip()) for i in re.split(r',\s+', line[5:]) if i]
                except (IndexError) as e:
                    raise ValueError('Invalid tag metadata') from e
            elif line.startswith('%date'):
                try:
                    # validate date by parsing
                    file_meta['date'] = datetime.fromisoformat(line[5:].strip()).isoformat()
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
                    content += '@{{TOC_EMBED}}'
                    title_set = True
                elif line.startswith('##'):
                    sections += 1

    if 'date' not in file_meta:
        s = os.stat(path)
        file_meta['date'] = datetime.fromtimestamp(s.st_birthtime).isoformat()

    if sections > 4:
        file_meta['needs_toc'] = True
        content = content.replace('@{{TOC_EMBED}}', '\n[TOC]\n')
    else:
        content = content.replace('@{{TOC_EMBED}}', '')

    return file_meta, content


def no_pages(template):
    return template.replace('@{{page-nav}}', '').replace('@{{page-title}}', '')


def page_nav(page_list):
    with open(os.path.join('private', 'page-nav.html.partial'))as f:
        partial_content = f.read()

    content = '{}'
    inside = ''
    for page in page_list:
        inside += partial_content.replace('@{{page-num}}', str(page))
    return content.format(inside)


def write_index(content):
    with open(os.path.join('private', 'index.html.template')) as f:
        template = f.read()
    if None in content:
        with open(os.path.join(kBuildDirRoot, 'index.html'), 'w') as f:
            f.write(no_pages(fill_includes(style(template).replace('%{{content}}', content[None]))))
    else:
        nav = page_nav(content.keys())
        for page_key in content:
            with open(os.path.join(kBuildDirRoot, 'page-{}'.format(page_key), 'index.html'), 'w') as f:
                f.write(fill_includes(style(template).replace('%{{content}}', content[page_key])).replace('@{{page-nav}}', nav).replace('@{{page-title}}', ' - Page {}'.format(page_key)))

        with open(os.path.join(kBuildDirRoot, 'index.html'), 'w') as f:
            f.write('<script>window.location = "/blog/page-1"</script>')


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-k', '--keep', action='store_true', help='DO not clean public dir before building')
    return ap.parse_args()


def add_tags(tags, meta, file, page):
    for tag in meta['tags']:
        lst = tags.get(tag, [])
        lst.append({'link': linkify(html_name(file)), 'title': titlify(file), 'internal_content': index_entry(html_name(file), meta, page)})
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


def kDefaultTemplateArgs(content, file, meta): return {
    'content': content,
    'title': titlify(file),
    'tags': tags_for_file(file, meta)
}


def render_template(template, **kwargs):
    text = style(template)
    for key in kwargs:
        text = text.replace('%{{' + str(key) + '}}', kwargs[key])

    text = fill_includes(text)


def fill_template(template, file, content, meta):
    text = (style(template)
            .replace("%{{content}}", content)
            .replace('%{{title}}', titlify(file))
            .replace('%{{tags}}', tags_for_file(file, meta))
            )

    text = fill_includes(text)
    return text


def birthtime_for_filename(filename):
    return os.stat(os.path.join('source', filename)).st_birthtime


def main():
    options = parse_args()
    kArticlesPerPage = 10
    kPageString = 'page-{}'

    if not options.keep:
        print('❗️ Cleaning public dir')
        shutil.rmtree(kBuildDirRoot)
        print('📂 Re-creating public dir')
        os.mkdir(kBuildDirRoot)

    print('🗂  Building HTML files from Markdown')
    index_content = {}
    blog_meta = {}
    tag_data = {}

    def build_article_pages(listing, destination, page=None):
        nonlocal index_content, blog_meta, tag_data
        lastidx = len(listing) - 1
        for i, file in enumerate(listing):
            print("\t{} '{}'".format('\u2517' if i == lastidx else '\u2523', file))
            path = os.path.join('source', file)
            blog_meta[file], file_content = strip_file_metadata(path)
            add_tags(tag_data, blog_meta[file], file, page)
            file_content = re.sub(r'\n([^\n])', r'\1', file_content)
            index_content[page] = index_content.get(page, '') + index_entry(html_name(file), blog_meta[file], page)
            html = markdown.markdown(file_content, extensions=['fenced_code', 'codehilite', 'toc'])
            with (open(os.path.join(destination, html_name(file)), 'w') as f,
                    open(os.path.join('private', 'article.html.template')) as g):
                text = fill_template(g.read(), file, html, blog_meta[file])
                f.write(text)

    listing = sorted(os.listdir('source'), key=birthtime_for_filename, reverse=True)

    count = len(listing)

    if count > kArticlesPerPage:
        print("⚠️ Too many articles! Rendering {} pages".format(count))
        dir_count = count // kArticlesPerPage + (0 if not count % kArticlesPerPage else 1)
        current_page = 0
        for i in range(dir_count - 1):
            print("🗂 Rendering page {}".format(i + 1))
            page_dir = os.path.join(kBuildDirRoot, kPageString.format(i + 1))
            if not os.path.isdir(page_dir):
                os.mkdir(page_dir)
            build_article_pages(listing[current_page * kArticlesPerPage: (current_page + 1) * kArticlesPerPage], page_dir, i + 1)
            current_page += 1

        print("🗂 Rendering page {}".format(dir_count))
        os.mkdir(os.path.join(kBuildDirRoot, kPageString.format(dir_count)))
        build_article_pages(listing[current_page * kArticlesPerPage:], os.path.join(kBuildDirRoot, kPageString.format(dir_count)), dir_count)
    else:
        build_article_pages(listing, kBuildDirRoot)

    print("📄 Creating index file")
    write_index(index_content)

    print("📄 Serializing metadata")
    serialize(blog_meta, 'public', 'metadata')

    print('📄 Writing tag list')
    serialize(list(tag_data.keys()), os.path.join('public', 'tags'), '.all')
    print('🗂  Writing tag files')
    tags = list(tag_data)
    last = tags.pop()
    for tag in tags:
        print("\t┣ Writing tag file for '{}'".format(tag))
        serialize(list(tag_data[tag]), os.path.join('public', 'tags'), tag)

    print("\t┗ Writing tag file for '{}'".format(last))
    serialize(list(tag_data[last]), os.path.join('public', 'tags'), last)

    print('📄 Preparing Search Template')
    with (open(os.path.join('private', 'search.html.template')) as f,
          open(os.path.join('public', 'search.html'), 'w') as g):
        g.write(fill_includes(style(f.read())))

    print('✅ Build complete!')


if __name__ == '__main__':
    raise SystemExit(main())
