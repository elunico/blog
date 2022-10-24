import copy
import os
import re
from datetime import datetime
from typing import *

import markdown

from python.html import *
from python.util import *


def generate_representation(cls):
    def debug_repr(self):
        inner = ', '.join(['{}={}'.format(attr, repr(val)) for attr, val in self.__dict__.items()])
        return '{}({})'.format(type(self).__name__, inner)

    setattr(cls, '__repr__', debug_repr)
    return cls


T = TypeVar('collection_type')
Result = TypeVar('result_type')


@generate_representation
class MetadataCategory(Generic[T, Result]):
    def __init__(self, name: str) -> None:
        self.name = name
        self.was_set = False
        self.done = False
        self.result = None

    def line_to_item_transform(self, item: str) -> T:
        '''
        Transforms a line of markdown text into a collection of metadata items in this category
        Generally this method is only called once per category on a line containing all the items for that category
        but it can be called many times if the same metadata directive (such as @tags) appears on many lines
        :param item:
        :return:
        '''
        raise NotImplementedError("Implement this method")

    def _extend_internal(self, item: T) -> None:
        self.was_set = True
        return self.extend(item)

    def extend(self, item: T) -> None:
        '''
        Method which extends the current collection of items to the collection of items for this particular category of metadata
        The collection may take any form and may contain 0 or more elements
        Generally this method is only called once per category on a line containing all the items for that category
        but it can be called many times if the same metadata directive (such as @tags) appears on many lines
        :param item: the new metadata item for this category
        :return: None
        '''
        raise NotImplementedError("Implement this method")

    def final_transform(self, collection: List[T]) -> Result:
        '''
        This method is used to take a collection of metadata items and perform a final processing step.
        This method is called after all lines of the file have been processed
        This method is useful for things like joining a list of items into a single str or similar
        :param collection: all the metadata items in this category
        :return: the result of the final transform
        '''
        raise NotImplementedError("Implement this method")

    def backing_collection(self) -> T:
        '''
        Gives access to the backing collection of this category
        :return: the category's backing collection
        '''
        raise NotImplementedError("Implement this method")

    def finalize(self):
        self.result = self.final_transform(self.backing_collection())
        self.done = True

    @property
    def directive(self):
        return '%{}'.format(self.name)

    def __eq__(self, o: object) -> bool:
        return hasattr(o, 'name') and self.name == o.name

    def __ne__(self, o: object) -> bool:
        return not (self == o)

    def __str__(self) -> str:
        return 'Metadata<{1}>({0})'.format(repr(self.name), type(self.backing_collection()).__name__)

    def __hash__(self) -> int:
        return hash(self.name)


Of = TypeVar('Of')


class BasicListMetadataFactory(MetadataCategory, Generic[Of]):

    def __init__(self, name: str, item_transform: Callable[[str], list[Of]]) -> None:
        super().__init__(name)
        self.contents = []
        self.item_transform = item_transform

    def line_to_item_transform(self, item: str) -> list[Of]:
        return self.item_transform(item)

    def extend(self, item: list[Of]) -> None:
        self.contents.extend(item)

    def final_transform(self, collection: List[List[Of]]) -> Result:
        return self.contents

    def backing_collection(self) -> list[Of]:
        return self.contents


class BasicStrMetadataFactory(MetadataCategory):

    def __init__(self, name: str, item_transform: Callable[[str], str]) -> None:
        super().__init__(name)
        self.contents = ''
        self.item_transform = item_transform

    def line_to_item_transform(self, item: str) -> str:
        return self.item_transform(item)

    def extend(self, item: str) -> None:
        self.contents += item

    def final_transform(self, collection: List[str]) -> Result:
        return self.contents

    def backing_collection(self) -> str:
        return self.contents


class BasicBoolMetadataFactory(MetadataCategory):
    def __init__(self, name: str, item_transform: Callable[[str], bool], init_value: bool = False) -> None:
        super().__init__(name)
        self.item_transform = item_transform
        self.initval = init_value
        self.contents = init_value

    def line_to_item_transform(self, item: str) -> bool:
        return self.item_transform(item)

    def extend(self, item: bool) -> None:
        self.contents = item

    def final_transform(self, collection: List[bool]) -> Result:
        return self.contents

    def backing_collection(self) -> bool:
        return self.contents


Tracker = Dict[str, MetadataCategory]


def strip_file_meta(path: str,
                    metas: list[MetadataCategory],
                    toc_condition: Callable[[str, int, Tracker], bool] = lambda *a: False) -> tuple[Tracker, str]:
    track: dict[str, MetadataCategory] = {m.name: m for m in metas}
    content = ''
    sections = 0
    title_set = False
    with open(path) as f:
        for line in f:
            was_meta = False
            for meta in metas:
                if line.startswith(meta.directive):
                    try:
                        track[meta.name]._extend_internal(meta.line_to_item_transform(line[len(meta.directive):]))
                        was_meta = True
                    except (IndexError, AttributeError, ValueError, TypeError) as e:
                        raise ValueError("Failed to process directive {}".format(meta.directive)) from e
            if not was_meta:
                content += line + '\n'
                if re.match(r'#[^#]', line):
                    if title_set:
                        raise ValueError("Too Many Level 1 Headings: '{}'".format(line))
                    content += '%{{TOC_EMBED}}'
                    title_set = True
                elif line.startswith('##'):
                    sections += 1

    if 'date' not in track or not track['date'].was_set:
        s = os.stat(path)
        track['date'].extend(datetime.fromtimestamp(s.st_birthtime).isoformat())

    if toc_condition(content, sections, track):
        content = content.replace('%{{TOC_EMBED}}', '\n[TOC]\n')
    else:
        content = content.replace('%{{TOC_EMBED}}', '')

    for (name, obj) in track.items():
        obj.finalize()

    # the markdown library has trouble with single new lines, so we need to clean things up for them
    # it should take 2 new lines in MD to create a <p> element, a single blank line should not be semantically
    # meaningful
    content = re.sub(r'\n([^\n])', r'\1', content)

    return track, content


def include_suffix(extension: str) -> str:
    if extension.endswith('.partial'):
        extension = extension[:extension.rindex('.partial')]

    if extension == 'html' or extension == 'htm':
        return ''
    else:
        return '-{}'.format(extension)


@generate_representation
class FileIncluder:
    def __init__(self, base_dir='./private'):
        self.substitutions = []
        self.base_dir = os.path.realpath(base_dir)

    def add_pattern(self, file_extension: str, include_transform: Callable[[str], str] = lambda a: a) -> 'FileIncluder':
        self.substitutions.append((file_extension, include_transform))
        return self

    def _file_replacer(self, match: re.Match, extension: str, transform: Callable[[str], str]):
        try:
            name_prefix = match.group(1)
        except (AttributeError, IndexError) as e:
            raise ValueError("Invalid @include directive '{}'".format(match)) from e

        filename = '{}.{}'.format(name_prefix, extension)
        try:
            with open(os.path.join(self.base_dir, filename)) as f:
                return transform(f.read())
        except FileNotFoundError as e:
            raise ValueError("Invalid @include directive '{}': File not found".format(match.group())) from e
        except OSError as e:
            raise ValueError("Invalid @include directive '{}'. Could not access file".format(match.group())) from e

    def fill(self, text: str) -> str:
        for extension, transform in self.substitutions:
            pattern = r'@include{}\s+(\w+)'.format(re.escape(include_suffix(extension)))
            matcher = lambda match: self._file_replacer(match, extension, transform)
            text = re.sub(pattern, matcher, text)

        return text


def render_template(template: str, file_includer: Optional[FileIncluder], **kwargs):
    """
    Renders the text of a template using all specified file include directives and filling in all specified variables
    with their given values.

    This function takes text from a templated file. This can be any file of any kind as long as its text. It will
    then attempt to perform two rounds of rendering:

        First, it will use file_includer to find @include-* directives in the file and replace them with the content
        of the files specified in the file. It will *only* search for @include directives specified by the patterns
        using the add_pattern method of FileIncluder. If the files are not found, then an error is raised. If @include
        directives exist that are not covered by the given FileIncluder, they are ignored

        Second, it will attempt to substitute all variable arguments with the values. Any key word argument, key,
        is formatted according to the substitution rules yielding %{{key}}. instances of this string are then replaced
        with the value specified along with the keyword argument throughout the file. Any %{{str}} patterns not covered
        are ignored. Any specified keys that cannot be found in the file *are also ignored*

        Notice the distinction. @include directives substitute files off teh file-system and fail when attempting to
        fill a file that does not exist. %{{str}} var directives ignore cases where a variable substitution is
        attempted but does not happen. Both ignore directives in a file that are not specifically given as arguments to the
        function. This allows composition so that later in the pipeline these can be handled without prior steps
        having to account for them.

    The fully rendered text is returned to the caller.

    :param template: the template text to render
    :param file_includer: the FileIncluder instance to use to include files. Can be none if no file including is needed/desired
    :param kwargs: the list of %{{var}} substitutions to make in the template
    :return: the rendered template string
    """

    template = file_includer.fill(template) if file_includer is not None else template
    for key in kwargs:
        template = template.replace('%{{' + str(key) + '}}', kwargs[key])
        if '_' in str(key):
            skey = key.replace('_', '-')
            template = template.replace('%{{' + str(skey) + '}}', kwargs[key])

    return template


def html_name(md_filename):
    *filename, ext = md_filename.rsplit('.')
    name = '.'.join(filename)
    return '{}.html'.format(name)


def add_tags(tags: dict[str, list[any]], meta: dict[str, MetadataCategory], file: str, page: int):
    for tag in meta['tags'].result:
        lst = tags.get(tag, [])
        lst.append({'link': linkify(html_name(file)), 'title': titlify(file),
                    'internal_content': index_entry(html_name(file), meta, page)})
        tags[tag] = lst


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


class EngineBuilder:
    def __init__(self, source_dir: str, private_dir: str, public_dir: str, articles_per_page: int = 10) -> None:
        self.source_dir = source_dir
        self.private_dir = private_dir
        self.public_dir = public_dir
        self.articles_per_page = articles_per_page
        self.meta_categories: list[MetadataCategory] = []
        self.toc_condition: Callable[[str, int, Tracker], bool] = lambda s, i, t: False
        self.includer = FileIncluder()

    def add_includer_pattern(self, file_extension: str,
                             include_transform: Callable[[str], str] = lambda a: a) -> 'EngineBuilder':
        self.includer.add_pattern(file_extension, include_transform)
        return self

    def add_metadata_category(self, metadata_category: MetadataCategory) -> 'EngineBuilder':
        self.meta_categories.append(metadata_category)
        return self

    def set_toc_condition(self, predicate: Callable[[str, int, Tracker], str]) -> 'EngineBuilder':
        self.toc_condition = predicate
        return self

    def build(self):
        e = Engine(self.source_dir, self.private_dir, self.public_dir, self.articles_per_page)
        for f, i in self.includer.substitutions:
            e.includer.add_pattern(f, i)
        e.toc_condition = self.toc_condition
        e.meta_categories = copy.deepcopy(self.meta_categories)
        return e


class Engine:
    def __init__(self, source_dir: str, private_dir: str, public_dir: str, articles_per_page: int = 10) -> None:
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

    # def add_includer_pattern(self, file_extension: str,
    #                          include_transform: Callable[[str], str] = lambda a: a) -> 'Engine':
    #     self.includer.add_pattern(file_extension, include_transform)
    #     return self
    #
    # def add_metadata_category(self, metadata_category: MetadataCategory) -> 'Engine':
    #     self.meta_categories.append(metadata_category)
    #     return self
    #
    # def set_toc_condition(self, predicate: Callable[[str, int, Tracker], str]) -> 'Engine':
    #     self.toc_condition = predicate
    #     return self

    def build_index(self, content):
        with open(os.path.join('private', 'index.html.template')) as f:
            template = f.read()
        if None in content:
            with open(os.path.join(self.public_dir, 'index.html'), 'w') as f:
                f.write(no_pages(render_template(template, self.includer, content=content[None])))
        else:
            nav = page_nav(content.keys())
            for page_key in content:
                with open(os.path.join(self.public_dir, 'page-{}'.format(page_key), 'index.html'), 'w') as f:
                    f.write(render_template(template, self.includer, content=content[page_key], page_nav=nav,
                                            page_title=' - Page {}'.format(page_key)))

            with open(os.path.join(self.public_dir, 'index.html'), 'w') as f:
                f.write('<script>window.location = "/blog/page-1"</script>')

    def produce(self, filename, destination, page=None):
        path = os.path.join(self.source_dir, filename)
        with open(path) as f:
            self.metadata[filename], file_content = strip_file_meta(path, copy.deepcopy(self.meta_categories),
                                                                    self.toc_condition)
            add_tags(self.tag_data, self.metadata[filename], filename, page)
            self.index_content[page] = self.index_content.get(page, '') + index_entry(html_name(filename),
                                                                                      self.metadata[filename], page)
            html = markdown.markdown(file_content, extensions=['fenced_code', 'codehilite', 'toc'])
            with (open(os.path.join(destination, html_name(filename)), 'w') as f,
                  open(os.path.join('private', 'article.html.template')) as g):
                template = g.read()
                meta = self.metadata[filename]
                text = render_template(template, self.includer,
                                       content=html,
                                       title=titlify(filename),
                                       tags=tags_for_file(filename, meta),
                                       published=meta['date'].result)
                f.write(text)

    def build_articles(self, listing, destination, page=None):
        for i, file in enumerate(listing):
            self.produce(file, destination, page)

    def generate(self):
        listing = sorted(os.listdir('source'), key=birthtime_for_filename, reverse=True)
        kPageString = 'page-{}'

        count = len(listing)

        if count > self.articles_per_page:
            print("⚠️ Too many articles! Rendering {} pages".format(count))
            dir_count = count // self.articles_per_page + (0 if not count % self.articles_per_page else 1)
            self.build_paginated_articles(dir_count, kPageString, listing)
        else:
            self.build_articles(listing, self.public_dir)

        print("📄 Creating index file")
        self.build_index(self.index_content)

        print("📄 Serializing metadata")
        self.write_metadata()

        print('📄 Writing tag list')
        self.write_tag_files()

        print('📄 Preparing Search Template')
        self.write_search_template()

        print('✅ Build complete!')

    def write_search_template(self):
        with (open(os.path.join('private', 'search.html.template')) as f,
              open(os.path.join('public', 'search.html'), 'w') as g):
            g.write(self.includer.fill(f.read()))

    def write_tag_files(self):
        serialize(list(self.tag_data.keys()), os.path.join('public', 'tags'), 'all')
        print('🗂  Writing tag files')
        tags = list(self.tag_data)
        last = tags.pop()
        for tag in tags:
            print("\t┣ Writing tag file for '{}'".format(tag))
            serialize(list(self.tag_data[tag]), os.path.join('public', 'tags'), tag)
        print("\t┗ Writing tag file for '{}'".format(last))
        serialize(list(self.tag_data[last]), os.path.join('public', 'tags'), last)

    def write_metadata(self):
        serialize(
            {filename: {key: value.result for key, value in meta.items()} for filename, meta in self.metadata.items()},
            'public', 'metadata')

    def build_paginated_articles(self, dir_count, kPageString, listing):
        current_page = 0
        for i in range(dir_count - 1):
            slice = listing[current_page * self.articles_per_page: (current_page + 1) * self.articles_per_page]
            current_page = self.render_paged_article(current_page, i, kPageString, slice)

        self.render_paged_article(current_page, dir_count - 1, kPageString,
                                  listing[current_page * self.articles_per_page:])

        # print("🗂 Rendering page {}".format(dir_count))
        # os.mkdir(os.path.join(self.public_dir, kPageString.format(dir_count)))
        # self.build_articles(listing[current_page * self.articles_per_page:],
        #                     os.path.join(self.public_dir, kPageString.format(dir_count)), dir_count)

    def render_paged_article(self, current_page, i, kPageString, listing_slice):
        print("🗂 Rendering page {}".format(i + 1))
        page_dir = os.path.join(self.public_dir, kPageString.format(i + 1))
        if not os.path.isdir(page_dir):
            os.mkdir(page_dir)
        self.build_articles(listing_slice, page_dir, i + 1)
        current_page += 1
        return current_page
