import json
import os.path
import urllib.parse
from datetime import datetime


def serialize(metadata, folder, file_prefix):
    if not os.path.isdir(folder):
        os.makedirs(folder)

    with open(os.path.join(folder, '{}.json'.format(file_prefix)), 'w') as f:
        json.dump(metadata, f)


def unserialize(folder, file_prefix):
    with open(os.path.join(folder, '{}.json'.format(file_prefix))) as f:
        return json.load(f)


def birthtime_for_filename(filename: str) -> float:
    with open(os.path.join('source', filename)) as f:
        for line in f:
            if line.startswith('%date'):
                try:
                    d = datetime.fromisoformat(line[6:].strip())
                    break
                except (IndexError, ValueError, TypeError) as e:
                    print(e)
                    print("[❗️] The %date data from file {} is broken using now()".format(filename))
                    d = datetime.now()
                    break
        else:
            d = datetime.now()
            print('[⚠️] No %date directive for {} is missing using now()'.format(filename))

    return d.timestamp()
    # return os.stat(os.path.join('source', filename)).st_birthtime


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


def html_name(md_filename: str) -> str:
    dot_index = md_filename.rindex('.')
    return md_filename[:dot_index] + '.html'


def linkify(title: str) -> str:
    return urllib.parse.quote(title)


def titlify(filename: str) -> str:
    return '.'.join(filename.rsplit('.')[:-1]).title()
