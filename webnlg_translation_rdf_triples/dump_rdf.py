from argparse import ArgumentParser
from SPARQLWrapper import SPARQLWrapper, JSON, SPARQLExceptions
from utils import _FILE_GLOBS, expand_paths, load_webnlg
import re
from collections import defaultdict, OrderedDict
import sys
import csv
from tqdm import tqdm
import random
import editdistance


def get_all_resource_identifiers(webnlg):
    identifiers = set()
    for entry in webnlg:
        mtripleset = entry["modifiedtripleset"]
        for mtriple in mtripleset:
            identifiers.add(mtriple.s)
            identifiers.add(mtriple.p)
            identifiers.add(mtriple.o)

    return identifiers


def main():
    ap = ArgumentParser(description="Dump all RDF identifiers from WebNLG")
    args = ap.parse_args()

    root = "./webnlg-dataset-new"
    paths = expand_paths(_FILE_GLOBS["release_v3.0_ru_cs"].values(), root)
    webnlg = list(load_webnlg(paths))

    resources = get_all_resource_identifiers(webnlg)

    # print all resources
    for resource in resources:
        print(resource)


if __name__ == "__main__":
    main()
