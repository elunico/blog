from multiprocessing import ProcessError
from os import pathconf
import os.path
import re
from typing import Dict, Generic, Mapping, TypeVar
from typing_extensions import Self


R = TypeVar('R')


class Rendered(Generic[R]):
    def content(self) -> R:
        raise NotImplementedError()


class RenderedText(Rendered):
    def __init__(self, text: str) -> None:
        self.text = text

    def content(self) -> str:
        return self.text


class RenderedFile(Rendered):
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def content(self) -> str:
        with open(self.filename) as f:
            return f.read()


T = TypeVar('T')


class Template(Generic[T]):
    def __init__(self, content: T, base_path=os.path.join(os.getcwd(), 'private')):
        self._content: T = content
        self.base_path = base_path

    def style(self, filename='stylesheet.css') -> Self:
        with open(os.path.join(self.base_path, filename)) as f:
            self._content = self._content.replace('@css-content {}', f.read())
        return self

    def fill_includes(self) -> Self:

        def file_replacer(match):
            try:
                name_prefix = match.group(1)
            except (AttributeError, IndexError) as e:
                raise ValueError("Invalid @include directive '{}'".format(match)) from e

            filename = '{}.html.partial'.format(name_prefix)
            try:
                with open(os.path.join(self.base_path, filename)) as f:
                    return f.read()
            except (FileNotFoundError) as e:
                raise ValueError("Invalid @include directive '{}': File not found".format(match.group())) from e
            except OSError as e:
                raise ValueError("Invalid @include directive '{}'. Could not access file".format(match.group())) from e

        self._content = re.sub(r'@include\s+(\w+)', file_replacer, self._content)

        return self

    def render_template(self, **kwargs: Dict[str, Rendered]) -> Self:
        self._content = self.style().fill_includes()
        for key in kwargs:
            self._content = self._content.replace('@{{' + str(kwargs[key]) + '}}')

        return self

    @property
    def content(self) -> T:
        return self._content


class TemplateFile(Template):
    def __init__(self, *path_components):
        with open(os.path.join(*path_components)) as f:
            super().__init__(f.read())
