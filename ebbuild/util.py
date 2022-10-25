import json
import os.path
import urllib.parse


def serialize(metadata, folder, file_prefix):
    if not os.path.isdir(folder):
        os.makedirs(folder)

    with open(os.path.join(folder, '{}.json'.format(file_prefix)), 'w') as f:
        json.dump(metadata, f)


def unserialize(folder, file_prefix):
    with open(os.path.join(folder, '{}.json'.format(file_prefix))) as f:
        return json.load(f)


def birthtime_for_filename(filename):
    return os.stat(os.path.join('source', filename)).st_birthtime


def autorepr(cls):
    def debug_repr(self):
        inner = ', '.join(['{}={}'.format(attr, repr(val)) for attr, val in self.__dict__.items()])
        return '{}({})'.format(type(self).__name__, inner)

    setattr(cls, '__repr__', debug_repr)
    return cls


def include_suffix(extension: str) -> str:
    if extension.endswith('.partial'):
        extension = extension[:extension.rindex('.partial')]

    if extension == 'html' or extension == 'htm':
        return ''
    else:
        return '-{}'.format(extension)


def html_name(md_filename):
    *filename, ext = md_filename.rsplit('.')
    name = '.'.join(filename)
    return '{}.html'.format(name)


def linkify(title):
    return urllib.parse.quote(title)


def titlify(filename):
    return '.'.join(filename.rsplit('.')[:-1]).title()
