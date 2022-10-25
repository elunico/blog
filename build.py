import argparse
import re
from datetime import datetime

from ebbuild import EngineBuilder, BasicListMetadataFactory, BasicStrMetadataFactory


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-k', '--keep', action='store_true', help='DO not clean public dir before building')
    return ap.parse_args()


def clean(tag):
    return ''.join(i for i in tag if i.isalnum() or i == ' ')


def main():
    options = parse_args()

    print('🚗 Building Engine')
    e = EngineBuilder()
    e.set_public_dir('public')
    e.set_private_dir('private')
    e.set_source_dir('source')

    if not options.keep:
        e.clean_public_dir_before_building(True)

    tag_pat = re.compile(r',\s+')
    (e.add_includer_pattern('html.partial')
     .add_includer_pattern('css', lambda s: '<style>{}</style>'.format(s))
     .add_markdown_extension('fenced_code', 'codehilite')
     .add_metadata_category(BasicListMetadataFactory('tags', lambda s: [clean(i.strip()) for i in tag_pat.split(s)]))
     .add_metadata_category(BasicStrMetadataFactory('date', lambda s: datetime.fromisoformat(s.strip()).isoformat()))
     .add_metadata_category(BasicStrMetadataFactory('summary', lambda s: s.strip())))

    e.set_toc_condition(lambda _1, sections, _2: sections > 4)

    engine = e.build()
    engine.generate()


if __name__ == '__main__':
    raise SystemExit(main())
