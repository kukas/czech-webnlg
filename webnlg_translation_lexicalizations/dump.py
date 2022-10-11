import xml.etree.cElementTree as ET
from collections import defaultdict, OrderedDict

import random
from argparse import ArgumentParser
import re
import sys
import os

from glob import glob

from utils import _FILE_GLOBS
import logging
logger = logging.getLogger(__name__)

def main():
    ap = ArgumentParser(
        description="Dump lexicalizations from WebNLG corpus into a text file"
    )
    ap.add_argument(
        "version",
        type=str,
        choices=_FILE_GLOBS.keys(),
        help="Select the dataset version",
    )
    ap.add_argument(
        "split",
        type=str,
        choices=["train", "dev", "test"],
        help="Select the dataset split",
    )
    ap.add_argument(
        "--dump",
        type=str,
        default="lexicalizations",
        choices=["lexicalizations", "mtriple", "otriple"],
        help="Select the dataset split",
    )
    ap.add_argument(
        "--lang",
        type=str,
        default=["en"],
        nargs="+",
        help="Which lexicalizations to dump",
    )
    ap.add_argument(
        "--root",
        type=str,
        default="./webnlg-dataset",
        help="Path to dataset",
    )
    args = ap.parse_args()

    # where to find the corpus
    path_to_corpus = os.path.join(args.root, _FILE_GLOBS[args.version][args.split])

    # collect xml files
    files = sorted(glob(path_to_corpus))

    # if we dump the english lexicalizations we look for the empty string as well
    select_langs = set(args.lang)

    # dump lexicalizations
    for file in files:
        tree = ET.parse(file)
        root = tree.getroot()

        # go through each entry and each lexicalization
        for entry in root.iter("entry"):
            eid = entry.attrib["eid"]
            if args.dump == "lexicalizations":
                lexicalizations = OrderedDict()
                for lex in entry.iter("lex"):
                    lid = lex.attrib.get("lid")
                    lang = lex.attrib.get("lang", "en")
                    source = lex.attrib.get("source", "original")
                    text = lex.text

                    if lid not in lexicalizations:
                        lexicalizations[lid] = OrderedDict()
                    if lang not in lexicalizations[lid]:
                        lexicalizations[lid][lang] = OrderedDict()
                    lexicalizations[lid][lang][source] = text

                for lid, lexes in lexicalizations.items():
                    for lang in select_langs:
                        if lang not in lexes:
                            logger.warning(f"Missing lexicalization for language {lang} in {file}, entry: {eid}")
                            continue
                        for source, text in lexes[lang].items():
                            assert text, f"Empty lexicalization in {file}, entry: {eid}"
                            print(text)
            elif args.dump == "mtriple" or args.dump == "otriple":
                triples = [triple.text for triple in entry.iter(args.dump)]
                print("[" + ("] + [".join(triples)) + "]")


if __name__ == "__main__":
    main()
