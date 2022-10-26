import os
import re
from typing import Callable

from ebbuild.util import autorepr, include_suffix


@autorepr
class FileIncluder:
    def __init__(self, base_dir='./private'):
        self.substitutions = []
        self.base_dir = os.path.realpath(base_dir)

    def add_pattern(self, file_extension: str, include_transform: Callable[[str], str] = lambda a: a) -> 'FileIncluder':
        pattern = re.compile(r'@include{}\s+(\w+)'.format(re.escape(include_suffix(file_extension))))
        self.substitutions.append((file_extension, include_transform, pattern))
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
        for extension, transform, pattern in self.substitutions:
            matcher = lambda match: self._file_replacer(match, extension, transform)
            text = pattern.sub(matcher, text)

        return text
