import argparse
import re
from datetime import datetime

from ebbuild import EngineBuilder, BasicListMetadataFactory, BasicStrMetadataFactory
from ebbuild.metadatacategory import BasicBoolMetadataFactory
from ebbuild.util import EBLogLevel


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-k",
        "--keep",
        action="store_true",
        help="DO not clean public dir before building",
    )
    return ap.parse_args()


def clean(tag):
    return "".join(i for i in tag if i.isalnum() or i == " ")


def main():
    options = parse_args()
    tag_pat = re.compile(r",\s+")

    e = EngineBuilder()
    e.set_log_level(EBLogLevel.INFO)
    e.log("🚗 Building Engine")
    e.set_public_dir("public")
    e.set_private_dir("private")
    e.set_source_dir("source")

    if options.keep:
        e.clean_public_dir_before_building(False)

    e.add_includer_pattern("html.partial")
    e.add_includer_pattern("css", lambda s: "<style>{}</style>".format(s))
    e.add_markdown_extension("fenced_code", "codehilite")
    e.add_metadata_category(
        BasicListMetadataFactory(
            "tags", lambda s: [clean(i.strip()) for i in tag_pat.split(s)]
        )
    )
    e.add_metadata_category(
        BasicStrMetadataFactory(
            "date", lambda s: datetime.fromisoformat(s.strip()).isoformat()
        )
    )
    e.add_metadata_category(BasicStrMetadataFactory("summary", lambda s: s.strip()))
    e.add_metadata_category(BasicBoolMetadataFactory("raw", lambda s: bool(s)))
    e.set_toc_condition(lambda _1, sections, _2: sections > 4)

    e.build().generate()


if __name__ == "__main__":
    raise SystemExit(main())
