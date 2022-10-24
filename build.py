import argparse
import os
import os.path
import re
import shutil
from datetime import datetime

from builder import BasicListMetadataFactory, BasicStrMetadataFactory, strip_file_meta, FileIncluder, render_template, \
    Engine, EngineBuilder
from python.html import *
from python.html import titlify, tags_for_file
from python.util import *

kBuildDirRoot = 'public'


def html_name(md_filename):
    *filename, ext = md_filename.rsplit('.')
    name = '.'.join(filename)
    return '{}.html'.format(name)


def clean(tag):
    return ''.join(i for i in tag if i.isalnum() or i == ' ')


def strip_file_metadata(path):
    metas = [
        BasicListMetadataFactory('tags', lambda s: [clean(i.strip()) for i in re.split(r',\s+', s)]),
        BasicStrMetadataFactory('date', lambda s: datetime.fromisoformat(s.strip()).isoformat()),
        BasicStrMetadataFactory('summary', lambda s: s.strip())
    ]

    return strip_file_meta(path, metas, lambda _1, sections, _2: sections > 4)


def no_pages(template):
    return render_template(template, None, page_nav="", page_title="")


def page_nav(page_list):
    with open(os.path.join('private', 'page-nav.html.partial')) as f:
        partial_content = f.read()

    content = '{}'
    inside = ''
    for page in page_list:
        inside += render_template(partial_content, None, page_num=str(page))
    return content.format(inside)


def write_index(content):
    with open(os.path.join('private', 'index.html.template')) as f:
        template = f.read()
    if None in content:
        with open(os.path.join(kBuildDirRoot, 'index.html'), 'w') as f:
            f.write(no_pages(render_template(template, includer, content=content[None])))
    else:
        nav = page_nav(content.keys())
        for page_key in content:
            with open(os.path.join(kBuildDirRoot, 'page-{}'.format(page_key), 'index.html'), 'w') as f:
                f.write(render_template(template, includer, content=content[page_key], page_nav=nav,
                                        page_title=' - Page {}'.format(page_key)))

        with open(os.path.join(kBuildDirRoot, 'index.html'), 'w') as f:
            f.write('<script>window.location = "/blog/page-1"</script>')


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-k', '--keep', action='store_true', help='DO not clean public dir before building')
    return ap.parse_args()


def add_tags(tags, meta, file, page):
    for tag in meta['tags']:
        lst = tags.get(tag, [])
        lst.append({'link': linkify(html_name(file)), 'title': titlify(file),
                    'internal_content': index_entry(html_name(file), meta, page)})
        tags[tag] = lst


def identity(arg):
    return arg


includer = FileIncluder().add_pattern('html.partial').add_pattern('css', lambda s: '<style>{}</style>'.format(s))


def kDefaultTemplateArgs(content, file, meta): return {
    'content': content,
    'title': titlify(file),
    'tags': tags_for_file(file, meta)
}


def main():
    options = parse_args()
    kArticlesPerPage = 10

    if not options.keep:
        print('❗️ Cleaning public dir')
        shutil.rmtree(kBuildDirRoot)
        print('📂 Re-creating public dir')
        os.mkdir(kBuildDirRoot)

    print('🚗 Building Engine')
    e = EngineBuilder('source', 'private', 'public')
    e.add_includer_pattern('html.partial').add_includer_pattern('css', lambda s: '<style>{}</style>'.format(s))
    e.add_metadata_category(BasicListMetadataFactory('tags', lambda s: [clean(i.strip()) for i in re.split(r',\s+', s)]))
    e.add_metadata_category(BasicStrMetadataFactory('date', lambda s: datetime.fromisoformat(s.strip()).isoformat()))
    e.add_metadata_category(BasicStrMetadataFactory('summary', lambda s: s.strip()))
    e.set_toc_condition(lambda _1, sections, _2: sections > 4)

    engine = e.build()
    engine.generate()


    # print('🗂  Building HTML files from Markdown')
    # index_content = {}
    # blog_meta = {}
    # tag_data = {}
    #
    # def build_article_pages(listing, destination, page=None):
    #     nonlocal index_content, blog_meta, tag_data
    #     lastidx = len(listing) - 1
    #     for i, file in enumerate(listing):
    #         print("\t{} '{}'".format('\u2517' if i == lastidx else '\u2523', file))
    #         path = os.path.join('source', file)
    #         blog_meta[file], file_content = strip_file_metadata(path)
    #         add_tags(tag_data, blog_meta[file], file, page)
    #         index_content[page] = index_content.get(page, '') + index_entry(html_name(file), blog_meta[file], page)
    #         html = markdown.markdown(file_content, extensions=['fenced_code', 'codehilite', 'toc'])
    #         with (open(os.path.join(destination, html_name(file)), 'w') as f,
    #               open(os.path.join('private', 'article.html.template')) as g):
    #             template = g.read()
    #             meta = blog_meta[file]
    #             text = render_template(template, includer,
    #                                    content=html,
    #                                    title=titlify(file),
    #                                    tags=tags_for_file(file, meta),
    #                                    published=meta['date'])
    #             f.write(text)
    #
    # listing = sorted(os.listdir('source'), key=birthtime_for_filename, reverse=True)
    #
    # count = len(listing)
    #
    # if count > kArticlesPerPage:
    #     print("⚠️ Too many articles! Rendering {} pages".format(count))
    #     dir_count = count // kArticlesPerPage + (0 if not count % kArticlesPerPage else 1)
    #     current_page = 0
    #     for i in range(dir_count - 1):
    #         print("🗂 Rendering page {}".format(i + 1))
    #         page_dir = os.path.join(kBuildDirRoot, kPageString.format(i + 1))
    #         if not os.path.isdir(page_dir):
    #             os.mkdir(page_dir)
    #         build_article_pages(listing[current_page * kArticlesPerPage: (current_page + 1) * kArticlesPerPage],
    #                             page_dir, i + 1)
    #         current_page += 1
    #
    #     print("🗂 Rendering page {}".format(dir_count))
    #     os.mkdir(os.path.join(kBuildDirRoot, kPageString.format(dir_count)))
    #     build_article_pages(listing[current_page * kArticlesPerPage:],
    #                         os.path.join(kBuildDirRoot, kPageString.format(dir_count)), dir_count)
    # else:
    #     build_article_pages(listing, kBuildDirRoot)
    #
    # print("📄 Creating index file")
    # write_index(index_content)
    #
    # print("📄 Serializing metadata")
    # serialize(blog_meta, 'public', 'metadata')
    #
    # print('📄 Writing tag list')
    # serialize(list(tag_data.keys()), os.path.join('public', 'tags'), 'all')
    # print('🗂  Writing tag files')
    # tags = list(tag_data)
    # last = tags.pop()
    # for tag in tags:
    #     print("\t┣ Writing tag file for '{}'".format(tag))
    #     serialize(list(tag_data[tag]), os.path.join('public', 'tags'), tag)
    #
    # print("\t┗ Writing tag file for '{}'".format(last))
    # serialize(list(tag_data[last]), os.path.join('public', 'tags'), last)
    #
    # print('📄 Preparing Search Template')
    # with (open(os.path.join('private', 'search.html.template')) as f,
    #       open(os.path.join('public', 'search.html'), 'w') as g):
    #     g.write(includer.fill(f.read()))
    #
    # print('✅ Build complete!')


if __name__ == '__main__':
    raise SystemExit(main())
