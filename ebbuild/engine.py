import copy
import os
import shutil
from datetime import datetime
from typing import Callable

import markdown

from ebbuild.builder import Tracker, no_pages, render_template, page_nav, strip_file_meta, add_tags
from ebbuild.fileincluder import FileIncluder
from ebbuild.html import index_entry, tags_for_file
from ebbuild.metadatacategory import MetadataCategory
from ebbuild.util import html_name, birthtime_for_filename, serialize, titlify, logger, EBLogLevel


def metadata_date_key(metadata, pair):
    fromisoformat = datetime.fromisoformat(metadata[pair[0]].get('date', datetime.now().isoformat()))
    return fromisoformat


class EngineBuildError(RuntimeError):
    pass


@logger
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
            nav = page_nav(content.keys(), self.private_dir)
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
                                       tags=tags_for_file(meta),
                                       published=meta['date'].result)
                f.write(text)

    def _build_articles(self, listing, destination, page=None):
        for i, file in enumerate(listing):
            self._produce(file, destination, page)

    def file_guard(self, fn, *args, action_description='', **kwargs):
        try:
            fn(*args, **kwargs)
        except OSError as e:
            message = '‼️ ERROR while {}: {}'.format(action_description, e)
            self.log(message, level=EBLogLevel.ERROR)
            raise EngineBuildError(message) from e

    def generate(self):

        if self.clean_before_building:
            self.log('❗️ Cleaning public dir')
            self._clean_build_dir()

        listing = sorted(os.listdir(self.source_dir), key=birthtime_for_filename, reverse=True)

        article_count = len(listing)
        page_count = article_count // self.articles_per_page + (0 if not article_count % self.articles_per_page else 1)

        if article_count > self.articles_per_page:
            self.log(f"⚠️ Too many articles! {article_count} articles will be broken up into {page_count} pages ",
                     level=EBLogLevel.WARN)
            self.file_guard(self._build_paginated_articles, page_count, self.kPageUrlFmt, listing,
                            action_description='building paginated articles')
        else:
            self.file_guard(self._build_articles, listing, self.public_dir, action_description='building articles')

        self.log("📄 Creating index file")
        self.file_guard(self._build_index, self.index_content, action_description='building index')
        # self._build_index(self.index_content)

        self.log("📄 Serializing metadata")
        self.file_guard(self._write_metadata, action_description='serializing metadata')

        self.log('📄 Writing tag list')
        self.file_guard(self._write_tag_files, action_description='writing tag list')

        self.log('📄 Preparing Search Template')
        self.file_guard(self._write_search_template, action_description='writing search template')

        self.log('✅ Build complete!')

    def _clean_build_dir(self):
        if os.path.exists(self.public_dir) and not os.path.isdir(self.public_dir):
            raise EngineBuildError('‼️ specified public director "{}" is not a directory'.format(self.public_dir))
        if not os.path.exists(self.public_dir):
            self.log('⚠️ Cleaning public dir specified, but no public dir found', level=EBLogLevel.WARN)
        else:
            self.file_guard(shutil.rmtree, self.public_dir, action_description='removing existing files')
        self.log('📂 Re-creating public dir')
        self.file_guard(os.mkdir, self.public_dir, action_description='Re-creating public dir')

    def _write_search_template(self):
        with (open(os.path.join(self.private_dir, 'search.html.template')) as f,
              open(os.path.join(self.public_dir, 'search.html'), 'w') as g):
            g.write(self.includer.fill(f.read()))

    def _write_tag_files(self):
        serialize(list(self.tag_data.keys()), os.path.join(self.public_dir, 'tags'), 'all')
        self.log('🗂  Writing tag files')
        tags = list(self.tag_data)
        last = tags.pop()
        for tag in tags:
            self.log("\t┣ Writing tag file for '{}'".format(tag))
            serialize(list(self.tag_data[tag]), os.path.join(self.public_dir, 'tags'), tag)
        self.log("\t┗ Writing tag file for '{}'".format(last))
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

    def _render_paged_article(self, current_page, i, kPageString, listing_slice):
        self.log("🗂 Rendering page {}".format(i + 1))
        page_dir = os.path.join(self.public_dir, kPageString.format(i + 1))
        if not os.path.isdir(page_dir):
            os.mkdir(page_dir)
        self._build_articles(listing_slice, page_dir, i + 1)
        current_page += 1
        return current_page
