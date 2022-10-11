from argparse import ArgumentParser
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from utils import _FILE_GLOBS, expand_paths, load_webnlg
import re
from collections import defaultdict
import sys
from tqdm import tqdm
from difflib import SequenceMatcher


def main():
    ap = ArgumentParser(
        description="Retrieve Lexicalizations from WebNLG by searching for resource"
    )
    ap.add_argument(
        "lang",
        type=str,
        help="Show lexicalizations with this language",
    )
    ap.add_argument(
        "resource",
        type=str,
        help="Subject/Property/Object to search for",
    )
    ap.add_argument(
        "--size",
        type=int,
        help="Filter by tripleset size",
    )
    args = ap.parse_args()

    root = "./webnlg-dataset-new"
    paths = expand_paths(_FILE_GLOBS["release_v3.0_ru_cs"].values(), root)
    webnlg = list(load_webnlg(paths))

    CRED = "\033[91m"
    CEND = "\033[0m"

    for entry in webnlg:
        if args.size and entry["size"] != args.size:
            continue

        triples = [mtriple for mtriple in entry["modifiedtripleset"]] + [
            otriple
            for otripleset in entry["originaltripleset"]
            for otriple in otripleset
        ]
        for triple in triples:
            if args.resource in triple.to_list():
                for l in entry["lex"]:
                    if l["lang"] == args.lang:
                        resource = args.resource.replace("_", " ")
                        lex_txt = l["text"]
                        s = SequenceMatcher(None, lex_txt, resource)
                        match = s.find_longest_match()
                        print(triple, "\t", end="")
                        if match.size > 3:
                            print(lex_txt[: match.a], end="")
                            print(CRED, end="")
                            print(lex_txt[match.a : match.a + match.size], end="")
                            print(CEND, end="")
                            print(lex_txt[match.a + match.size :])
                        else:
                            print(lex_txt)


if __name__ == "__main__":
    main()
