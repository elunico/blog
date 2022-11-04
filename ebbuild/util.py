import json
import os.path
import sys
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


# TODO: I think all metadata should be processed so files can be sorted, then build the index and the pages
# currently, you cannot sort index articles after reading metadata bc pages are built concurrently
# you have to know the metadata, sort, build the index page, but currenlty it is sort, build meta and index concurrently
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


class EBLogLevel:
    DEBUG = 1 << 0
    INFO = 1 << 1
    WARN = 1 << 2
    STOP = 1 << 3
    ERROR = 1 << 4
    FATAL = 1 << 5
    OFF = 1 << 31


def logger(cls):
    def log(self, *messages, file=sys.stdout, sep=' ', end='\n', level=EBLogLevel.INFO):
        if level >= self.log_level:
            print(*messages, file=file, sep=sep, end=end)

    if not hasattr(cls, 'log_level') or getattr(cls, 'log_level', None) is None:
        setattr(cls, 'log_level', EBLogLevel.INFO)

    setattr(cls, 'log', log)
    return cls
