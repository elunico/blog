import copy
from typing import Callable

from ebbuild.builder import Tracker
from ebbuild.engine import Engine
from ebbuild.fileincluder import FileIncluder
from ebbuild.metadatacategory import MetadataCategory
from ebbuild.util import autorepr, logger,EBLogLevel


@autorepr
@logger
class EngineBuilder:
    def __init__(self) -> None:
        self.log_level = EBLogLevel.INFO
        self.article_template = 'article.html.template'
        self.index_template = 'index.html.template'
        self.md_extensions = []
        self.source_dir = '../source'
        self.private_dir = '../private'
        self.public_dir = '../public'
        self.clean_before_building = True
        self.articles_per_page = 10
        self.meta_categories: list[MetadataCategory] = []
        self.toc_condition: Callable[[str, int, Tracker], bool] = lambda s, i, t: False
        self.includer = FileIncluder()

    def set_articles_per_page(self, count: int) -> "EngineBuilder":
        self.articles_per_page = count
        return self

    def set_source_dir(self, source_dir) -> "EngineBuilder":
        self.source_dir = source_dir
        return self

    def set_private_dir(self, private_dir) -> "EngineBuilder":
        self.private_dir = private_dir
        return self

    def set_public_dir(self, public_dir) -> "EngineBuilder":
        self.public_dir = public_dir
        return self

    def add_includer_pattern(self, file_extension: str,
                             include_transform: Callable[[str], str] = lambda a: a) -> 'EngineBuilder':
        self.includer.add_pattern(file_extension, include_transform)
        return self

    def add_metadata_category(self, metadata_category: MetadataCategory) -> 'EngineBuilder':
        self.meta_categories.append(metadata_category)
        return self

    def set_toc_condition(self, predicate: Callable[[str, int, Tracker], str]) -> 'EngineBuilder':
        self.md_extensions.append('toc')
        self.toc_condition = predicate
        return self

    def set_log_level(self, level: EBLogLevel) -> 'EngineBuilder':
        self.log_level = level
        return self

    def build(self):
        e = Engine(self.source_dir, self.private_dir, self.public_dir, self.articles_per_page)
        for f, i, pat in self.includer.substitutions:
            e.includer.add_pattern(f, i)
        e.toc_condition = self.toc_condition
        e.meta_categories = copy.deepcopy(self.meta_categories)
        e.clean_before_building = self.clean_before_building
        e.md_extensions = copy.copy(self.md_extensions)
        e.index_template = self.index_template
        e.article_template = self.article_template
        e.log_level = self.log_level
        return e

    def clean_public_dir_before_building(self, value) -> "EngineBuilder":
        self.clean_before_building = value
        return self

    def add_markdown_extension(self, *extensions) -> "EngineBuilder":
        self.md_extensions.extend(extensions)
        return self
