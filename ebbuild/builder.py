import os
import re
from datetime import datetime
from typing import *

from pyfunctional import alwaysfalse

from ebbuild.fileincluder import FileIncluder
from ebbuild.html import index_entry
from ebbuild.metadatacategory import MetadataCategory
from ebbuild.util import html_name, linkify, titlify

Tracker = Dict[str, MetadataCategory]

kMDLineFixerPattern = re.compile(r'\n([^\n])')


def strip_file_meta(path: str,
                    metas: list[MetadataCategory],
                    toc_condition: Callable[[str, int, Tracker], bool] = alwaysfalse) -> tuple[Tracker, str]:
    track: dict[str, MetadataCategory] = {m.name: m for m in metas}
    content = ''
    sections = 0
    title_set = False
    with open(path) as f:
        for line in f:
            was_meta = False
            for meta in metas:
                s = line[:len(meta.directive)]
                if meta.directive == s:
                    try:
                        track[meta.name]._extend_internal(meta.line_to_item_transform(line[len(meta.directive):]))
                        was_meta = True
                    except (IndexError, AttributeError, ValueError, TypeError) as e:
                        raise ValueError("Failed to process directive {}".format(meta.directive)) from e
            if not was_meta:
                content += line + '\n'
                if line[0] == '#' and line[1] != '#':
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
    content = kMDLineFixerPattern.sub(r'\1', content)

    return track, content


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


def add_tags(tags: dict[str, list[any]], meta: dict[str, MetadataCategory], file: str, page: int):
    for tag in meta['tags'].result:
        lst = tags.get(tag, [])
        lst.append({'link': linkify(html_name(file)), 'title': titlify(file),
                    'internal_content': index_entry(html_name(file), meta, page)})
        tags[tag] = lst


def no_pages(template):
    return render_template(template, None, page_nav="", page_title="")


def page_nav(page_list, private_dir):
    with open(os.path.join(private_dir, 'page-nav.html.partial')) as f:
        partial_content = f.read()

    content = '{}'
    inside = ''
    for page in page_list:
        inside += render_template(partial_content, None, page_num=str(page))
    return content.format(inside)
