import xml.etree.cElementTree as ET
from collections import defaultdict

import random
from argparse import ArgumentParser
import re
import sys
import os
from pathlib import Path
from glob import glob

from utils import _FILE_GLOBS


def main():
    ap = ArgumentParser(description="Add new lexicalizations to a WebNLG dataset.")
    ap.add_argument(
        "--version",
        type=str,
        choices=_FILE_GLOBS.keys(),
        help="Select the dataset version",
    )
    ap.add_argument(
        "--split",
        type=str,
        choices=["train", "dev", "test"],
        help="Select the dataset split",
    )
    ap.add_argument(
        "--lang",
        type=str,
        help="New language attribute",
    )
    ap.add_argument(
        "--new_root",
        type=str,
        help="Path to the new dataset root",
    )
    ap.add_argument(
        "--lexicalization_files",
        type=str,
        nargs="+",
        help="Text files with the new lexicalizations",
    )
    ap.add_argument(
        "--source_names",
        type=str,
        nargs="+",
        help="What to add to the source attribute",
    )
    ap.add_argument(
        "--root",
        type=str,
        default="webnlg-dataset",
        help="Path to the WebNLG versions",
    )
    ap.add_argument(
        "--add_lang_to_orig",
        type=str,
        default="en",
        help="Add lang attribute to the original lexicalizations",
    )
    args = ap.parse_args()

    # where to find the corpus
    path_to_corpus = os.path.join(args.root, _FILE_GLOBS[args.version][args.split])

    # collect xml files
    files = sorted(glob(path_to_corpus))

    assert files, "the source dir is empty"

    os.makedirs(args.new_root, exist_ok=True)

    # prepare paths to the output xml files
    if args.version == "release_v3.0_en":
        old = os.path.join(args.root, "release_v3.0", "en")
        new = os.path.join(args.new_root, "release_v3.0", "en_" + args.lang)
        new_files = [f.replace(old, new, 1) for f in files]

    elif args.version == "release_v3.0_ru_test_fixed":
        old = os.path.join(args.root, "release_v3.0", "ru_test_fixed")
        new = os.path.join(args.new_root, "release_v3.0", "ru_" + args.lang)

        new_files = [f.replace(old, new, 1) for f in files]
    else:
        raise NotImplementedError("Only release_v3.0_en and release_v3.0_ru_test_fixed are supported")

    assert all(
        file != new_file for file, new_file in zip(files, new_files)
    ), "Modifying the old files not intended"

    # collect lexicalizations
    new_lexes = []
    for lex_file, source_name in zip(args.lexicalization_files, args.source_names):
        with open(lex_file) as f:
            new_lexes.append((lex_file, source_name, iter([line.strip() for line in f.readlines()])))

    # load files
    for file, new_file in zip(files, new_files):
        print("Parsing", file)
        tree = ET.parse(file)
        root = tree.getroot()

        # go through each entry and each lexicalization
        for entry in root.iter("entry"):
            for lex in list(entry.iter("lex")):
                # skip non-english lexicalizations
                # print(lex.attrib.get("lang", "en") != "en")
                if lex.attrib.get("lang", "en") != "en":
                    continue

                if args.add_lang_to_orig:
                    lex.set("lang", args.add_lang_to_orig)
                # go through the translated lexicalizations we want to add
                for lex_file, source_name, new_lex_text_iter in new_lexes:
                    try:
                        new_lex_text = next(new_lex_text_iter)
                    except StopIteration:
                        print("Ran out of lexicalizations in", lex_file)
                        raise

                    new_lex = ET.SubElement(entry, "lex")
                    assert new_lex_text, "New lexicalization text must not be empty"
                    new_lex.text = new_lex_text
                    new_lex.set("lid", lex.attrib["lid"])
                    new_lex.set("lang", args.lang)
                    # new_lex.set("source", os.path.splitext(lex_file)[0])
                    new_lex.set("source", source_name)

        ET.indent(tree)

        print("Writing to", new_file)
        os.makedirs(os.path.dirname(new_file), exist_ok=True)
        tree.write(new_file, encoding="utf-8")


if __name__ == "__main__":
    main()
