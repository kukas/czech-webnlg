import xml.etree.cElementTree as ET

from argparse import ArgumentParser
import os

from glob import glob

from utils import _FILE_GLOBS


def webnlg_to_dict(entries):
    result = {}
    for entry in entries:
        triples = [triple.text for triple in entry.iter("otriple")]
        key = "+".join(triples)
        result[key] = entry

    return result


def load_trees(paths, corpus_root):
    for path in paths:
        fullpath = os.path.join(corpus_root, path)
        for file in glob(fullpath):
            tree = ET.parse(file)
            yield tree


def iterate_entries(trees):
    for tree in trees:
        root = tree.getroot()
        for entry in root.iter("entry"):
            yield entry


def main():
    ap = ArgumentParser(description="Add missing lexicalizations to the test split of the Russian WebNLG dataset.")
    ap.add_argument(
        "dataset_root",
        type=str,
        help="Path to the original WebNLG **repository** (containing multiple versions)",
    )
    ap.add_argument(
        "new_dataset_path",
        type=str,
        help="Path to the new WebNLG dataset",
    )
    args = ap.parse_args()

    root = args.dataset_root
    webnlg_v2 = webnlg_to_dict(
        iterate_entries(load_trees(_FILE_GLOBS["release_v2"].values(), root))
    )
    webnlg_v21 = webnlg_to_dict(
        iterate_entries(load_trees(_FILE_GLOBS["release_v2.1"].values(), root))
    )
    webnlg_v3en = webnlg_to_dict(
        iterate_entries(load_trees(_FILE_GLOBS["release_v3.0_en"].values(), root))
    )
    webnlg_v3ru_trees = list(load_trees([_FILE_GLOBS["release_v3.0_ru"]["test"]], root))
    webnlg_v3ru_test_tree = webnlg_v3ru_trees[-1]
    webnlg_v3ru = webnlg_to_dict(iterate_entries(webnlg_v3ru_trees))

    total_number = 0
    covered_by_v2 = 0
    covered_by_v21 = 0
    covered_by_v3en = 0
    v2_and_v21_different = 0
    for key, entry in webnlg_v3ru.items():
        total_number += 1
        if key in webnlg_v2:
            covered_by_v2 += 1
        if key in webnlg_v21:
            covered_by_v21 += 1
            for lex in webnlg_v21[key].iter("lex"):
                new_lex_text = lex.text

                new_lex = ET.SubElement(entry, "lex")
                new_lex.text = new_lex_text
                new_lex.set("lid", lex.attrib["lid"])
                new_lex.set("lang", "en")

        if key in webnlg_v2 and key in webnlg_v21:
            v2_lexes = [lex.text for lex in webnlg_v2[key].iter("lex")]
            v21_lexes = [lex.text for lex in webnlg_v21[key].iter("lex")]
            if v2_lexes != v21_lexes:
                v2_and_v21_different += 1
                print(v2_lexes, v21_lexes)

        if key in webnlg_v3en:
            covered_by_v3en += 1

        if key not in webnlg_v2 and key not in webnlg_v21 and key not in webnlg_v3en:
            print("nowhere to be found!!!", key)
            print([lex.text for lex in entry.iter("lex")])

    print(f"total v3.0ru test lexicalizations: {total_number}")
    print(f"covered by v2.0: {covered_by_v2}")
    print(f"covered by v2.1: {covered_by_v21}")
    print(f"covered by v3.0en: {covered_by_v3en}")
    print(f"number of changed samples (at least one lexicalization different) between v2 and v2.1: {v2_and_v21_different}")

    new_file = os.path.join(args.new_dataset_path, "test", "rdf-to-text-generation-test-data-with-refs-ru.xml")
    ET.indent(webnlg_v3ru_test_tree)

    print("Writing to", new_file)
    os.makedirs(os.path.dirname(new_file), exist_ok=True)
    webnlg_v3ru_test_tree.write(new_file, encoding="utf-8")


if __name__ == "__main__":
    main()
