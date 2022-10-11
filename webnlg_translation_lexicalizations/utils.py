import xml.etree.cElementTree as ET

import os
from glob import glob

class Triple:
    def __init__(self, s, p, o):
        self.s = s
        self.p = p
        self.o = o

    def __repr__(self):
        return f"{self.s} | {self.p} | {self.o}"
    
    def to_list(self):
        return [self.s, self.p, self.o]

    def from_string(string):
        s, p, o = string.split(" | ")
        return Triple(s, p, o)

# From https://huggingface.co/datasets/web_nlg/blob/main/web_nlg.py
_FILE_GLOBS = {
    "release_v1": {
        "full": "release_v1/xml/*triples/*.xml",
    },
    "release_v2": {
        "train": "release_v2/xml/train/*triples/*.xml",
        "dev": "release_v2/xml/dev/*triples/*.xml",
        "test": "release_v2/xml/test/*triples/*.xml",
    },
    "release_v2.1": {
        "train": "release_v2.1/xml/train/*triples/*.xml",
        "dev": "release_v2.1/xml/dev/*triples/*.xml",
        "test": "release_v2.1/xml/test/*triples/*.xml",
    },
    "release_v3.0_en": {
        "train": "release_v3.0/en/train/*triples/*.xml",
        "dev": "release_v3.0/en/dev/*triples/*.xml",
        "test": "release_v3.0/en/test/rdf-to-text-generation-test-data-with-refs-en.xml",
    },
    "release_v3.0_ru": {
        "train": "release_v3.0/ru/train/*triples/*.xml",
        "dev": "release_v3.0/ru/dev/*triples/*.xml",
        "test": "release_v3.0/ru/test/rdf-to-text-generation-test-data-with-refs-ru.xml",
    },
    "release_v3.0_ru_test_fixed": {
        "train": "release_v3.0/ru_test_fixed/train/*triples/*.xml",
        "dev": "release_v3.0/ru_test_fixed/dev/*triples/*.xml",
        "test": "release_v3.0/ru_test_fixed/test/rdf-to-text-generation-test-data-with-refs-ru.xml",
    },
    "release_v3.0_en_cs": {
        "train": "release_v3.0/en_cs/train/*triples/*.xml",
        "dev": "release_v3.0/en_cs/dev/*triples/*.xml",
        "test": "release_v3.0/en_cs/test/rdf-to-text-generation-test-data-with-refs-en.xml",
    },
    "release_v3.0_ru_cs": {
        "train": "release_v3.0/ru_cs/train/*triples/*.xml",
        "dev": "release_v3.0/ru_cs/dev/*triples/*.xml",
        "test": "release_v3.0/ru_cs/test/rdf-to-text-generation-test-data-with-refs-en.xml",
    },
}


def expand_paths(paths, corpus_root):
    for path in paths:
        fullpath = os.path.join(corpus_root, path)
        for file in glob(fullpath):
            yield file


def load_webnlg(xml_paths):
    def _parse_tripleset(tripleset, triple):
        return [Triple.from_string(t.text) for t in tripleset.iter(triple)]

    def _parse_lex(lex):
        attrib = lex.attrib.copy()
        attrib["text"] = lex.text
        return attrib

    for xml_file in xml_paths:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for entry in root.iter("entry"):
            yield {
                "eid": entry.attrib["eid"],
                "category": entry.attrib["category"],
                "size": int(entry.attrib["size"]),
                "originaltripleset": [
                    _parse_tripleset(ts, "otriple")
                    for ts in entry.iter("originaltripleset")
                ],
                "modifiedtripleset": _parse_tripleset(
                    entry.find("modifiedtripleset"), "mtriple"
                ),
                "lex": [_parse_lex(lex) for lex in entry.iter("lex")],
            }
