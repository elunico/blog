import copy
import os
import shutil
from typing import Callable

import markdown

from ebbuild.builder import Tracker, no_pages, render_template, page_nav, strip_file_meta, add_tags
from ebbuild.fileincluder import FileIncluder
from ebbuild.html import index_entry, tags_for_file
from ebbuild.metadatacategory import MetadataCategory
from ebbuild.util import html_name, birthtime_for_filename, serialize, titlify


class Engine:
    def __init__(self, source_dir: str, private_dir: str, public_dir: str, articles_per_page: int = 10) -> None:
        self.kPageUrlFmt = 'page-{}'
        self.index_content = {}
        self.tag_data = {}
        self.source_dir = source_dir
        self.private_dir = private_dir
        self.public_dir = public_dir
        self.articles_per_page = articles_per_page
        self.metadata: dict[str, dict[str, MetadataCategory]] = {}
        self.meta_categories: list[MetadataCategory] = []
        self.toc_condition: Callable[[str, int, Tracker], bool] = lambda s, i, t: False
        self.includer = FileIncluder()
        self.clean_before_building = True
        self.md_extensions = []
        self.index_template = 'index.html.template'
        self.article_template = 'article.html.template'

    def _build_index(self, content):
        with open(os.path.join(self.private_dir, self.index_template)) as f:
            template = f.read()
        if None in content:
            with open(os.path.join(self.public_dir, 'index.html'), 'w') as f:
                f.write(no_pages(render_template(template, self.includer, content=content[None])))
        else:
            nav = page_nav(content.keys())
            for page_key in content:
                with open(os.path.join(self.public_dir, self.kPageUrlFmt.format(page_key), 'index.html'), 'w') as f:
                    f.write(render_template(template, self.includer, content=content[page_key], page_nav=nav,
                                            page_title=' - Page {}'.format(page_key)))

            with open(os.path.join(self.public_dir, 'index.html'), 'w') as f:
                f.write('<script>window.location = "/blog/page-1"</script>')

    def _produce(self, filename, destination, page=None):
        path = os.path.join(self.source_dir, filename)
        with open(path) as f:
            self.metadata[filename], file_content = strip_file_meta(path, copy.deepcopy(self.meta_categories),
                                                                    self.toc_condition)
            add_tags(self.tag_data, self.metadata[filename], filename, page)
            self.index_content[page] = self.index_content.get(page, '') + index_entry(html_name(filename),
                                                                                      self.metadata[filename], page)
            html = markdown.markdown(file_content, extensions=self.md_extensions)
            with (open(os.path.join(destination, html_name(filename)), 'w') as f,
                  open(os.path.join(self.private_dir, self.article_template)) as g):
                template = g.read()
                meta = self.metadata[filename]
                text = render_template(template, self.includer,
                                       content=html,
                                       title=titlify(filename),
                                       tags=tags_for_file(filename, meta),
                                       published=meta['date'].result)
                f.write(text)

    def _build_articles(self, listing, destination, page=None):
        for i, file in enumerate(listing):
            self._produce(file, destination, page)

    def generate(self):
        if self.clean_before_building:
            print('❗️ Cleaning public dir')
            shutil.rmtree(self.public_dir)
            print('📂 Re-creating public dir')
            os.mkdir(self.public_dir)

        listing = sorted(os.listdir(self.source_dir), key=birthtime_for_filename, reverse=True)

        count = len(listing)

        if count > self.articles_per_page:
            print("⚠️ Too many articles! Rendering {} pages".format(count))
            dir_count = count // self.articles_per_page + (0 if not count % self.articles_per_page else 1)
            self._build_paginated_articles(dir_count, self.kPageUrlFmt, listing)
        else:
            self._build_articles(listing, self.public_dir)

        print("📄 Creating index file")
        self._build_index(self.index_content)

        print("📄 Serializing metadata")
        self._write_metadata()

        print('📄 Writing tag list')
        self._write_tag_files()

        print('📄 Preparing Search Template')
        self._write_search_template()

        print('✅ Build complete!')

    def _write_search_template(self):
        with (open(os.path.join(self.private_dir, 'search.html.template')) as f,
              open(os.path.join(self.public_dir, 'search.html'), 'w') as g):
            g.write(self.includer.fill(f.read()))

    def _write_tag_files(self):
        serialize(list(self.tag_data.keys()), os.path.join(self.public_dir, 'tags'), 'all')
        print('🗂  Writing tag files')
        tags = list(self.tag_data)
        last = tags.pop()
        for tag in tags:
            print("\t┣ Writing tag file for '{}'".format(tag))
            serialize(list(self.tag_data[tag]), os.path.join(self.public_dir, 'tags'), tag)
        print("\t┗ Writing tag file for '{}'".format(last))
        serialize(list(self.tag_data[last]), os.path.join(self.public_dir, 'tags'), last)

    def _write_metadata(self):
        serialize(
            {filename: {key: value.result for key, value in meta.items()} for filename, meta in self.metadata.items()},
            self.public_dir, 'metadata')

    def _build_paginated_articles(self, dir_count, kPageString, listing):
        current_page = 0
        for i in range(dir_count - 1):
            slice = listing[current_page * self.articles_per_page: (current_page + 1) * self.articles_per_page]
            current_page = self._render_paged_article(current_page, i, kPageString, slice)

        self._render_paged_article(current_page, dir_count - 1, kPageString,
                                   listing[current_page * self.articles_per_page:])

        # print("🗂 Rendering page {}".format(dir_count))
        # os.mkdir(os.path.join(self.public_dir, kPageString.format(dir_count)))
        # self.build_articles(listing[current_page * self.articles_per_page:],
        #                     os.path.join(self.public_dir, kPageString.format(dir_count)), dir_count)

    def _render_paged_article(self, current_page, i, kPageString, listing_slice):
        print("🗂 Rendering page {}".format(i + 1))
        page_dir = os.path.join(self.public_dir, kPageString.format(i + 1))
        if not os.path.isdir(page_dir):
            os.mkdir(page_dir)
        self._build_articles(listing_slice, page_dir, i + 1)
        current_page += 1
        return current_page
