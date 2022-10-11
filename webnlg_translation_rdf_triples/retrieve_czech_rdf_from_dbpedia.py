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
    subjects = OrderedDict()
    properties = OrderedDict()
    objects = OrderedDict()
    aliases = defaultdict(set)
    examples = defaultdict(str)
    for entry in webnlg:
        otriplesets = entry["originaltripleset"]
        mtripleset = entry["modifiedtripleset"]
        # assure that all triplesets have the correct size
        assert (
            all(len(tripleset) == entry["size"] for tripleset in otriplesets)
            and len(mtripleset) == entry["size"]
        )
        # add entries to dict under the mtriple keys
        for mtriple in mtripleset:
            subjects.setdefault(mtriple.s, []).append(entry)
            properties.setdefault(mtriple.p, []).append(entry)
            objects.setdefault(mtriple.o, []).append(entry)

        # add aliases
        # we add aliases only from entries with one originaltripleset
        # because the triple order is unambiguous there
        if len(otriplesets) == 1:
            best_otripleset = otriplesets[0]
            for otriple, mtriple in zip(best_otripleset, mtripleset):
                aliases[mtriple.s].add(otriple.s)
                aliases[mtriple.p].add(otriple.p)
                aliases[mtriple.o].add(otriple.o)

        if entry["size"] == 1:
            examples[mtriple.s] = str(mtriple) + " = " + entry["lex"][0]["text"]
            examples[mtriple.p] = str(mtriple) + " = " + entry["lex"][0]["text"]
            examples[mtriple.o] = str(mtriple) + " = " + entry["lex"][0]["text"]

        # todo? matching the triplesets?
        # for otripleset in otriplesets:
        #     best_otripleset = min(otriplesets_with_distance, key=lambda: x[1])
        # sorted_otripleset = []
        # for mtriple in mtripleset:
        #     otriples_with_distance = []
        #     for otriple in otripleset:
        #         s = editdistance.eval(str(otriple.s), str(mtriple.s))
        #         p = editdistance.eval(str(otriple.p), str(mtriple.p))
        #         o = editdistance.eval(str(otriple.o), str(mtriple.o))
        #         otriples_with_distance.append((otriple, s + p + o))
        #     most_similar_otriple, distance = min(
        #         otriples_with_distance, key=lambda x: x[1]
        #     )
        #     sorted_otripleset.append(most_similar_otriple)
        #     if str(mtriple) != str(most_similar_otriple):
        #         print(mtriple, "===", most_similar_otriple)

    return {
        "subjects": subjects,
        "properties": properties,
        "objects": objects,
        "aliases": aliases,
        "examples": examples,
    }


def query(q, sparql):
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    try:
        qq = sparql.query()
    except SPARQLExceptions.QueryBadFormed as err:
        print(err.args[0].replace("\\n", "\n"), file=sys.stderr)
        return None
        # raise
    results = qq.convert()
    return results["results"]["bindings"]


def main():
    ap = ArgumentParser(description="Retrieve Czech labels from dbpedia")
    ap.add_argument(
        "resource",
        type=str,
        choices=["subjects", "properties", "objects"],
        help="Export the selected resources from all RDF triples",
    )
    args = ap.parse_args()

    root = "./webnlg-dataset-new"
    paths = expand_paths(_FILE_GLOBS["release_v3.0_ru_cs"].values(), root)
    webnlg = list(load_webnlg(paths))

    resources = get_all_resource_identifiers(webnlg)

    aliases = resources["aliases"]
    examples = resources["examples"]
    # for mresource, resource_aliases in aliases.items():
    #     if len(resource_aliases) == 1 and mresource == next(iter(resource_aliases)):
    #         continue
    #     print(mresource, resource_aliases)

    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    selected_resource = resources[args.resource]
    print(args.resource, len(selected_resource), file=sys.stderr)
    print(
        "subject object overlap",
        len(set(resources["objects"]).intersection(set(resources["subjects"]))),
        file=sys.stderr,
    )

    tsv_writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
    tsv_writer.writerow(["resource", "label_en", "label_cs"])
    for resource, entries in tqdm(selected_resource.items()):
        # filter some resources (mainly for objects)
        # if '"' in resource:
        #     print(resource, file=sys.stderr)
        #     continue
        # if re.match(r"^([\d]+[Ee\-+.]*\s*)+$", resource):
        #     print(resource, file=sys.stderr)
        #     continue
        # if resource.startswith("<") and resource.endswith(">"):
        #     print(resource, file=sys.stderr)
        #     continue
        # if " " in resource:
        #     print(resource, file=sys.stderr)
        #     continue

        if args.resource == "subjects":

            # uri = "http://dbpedia.org/resource/" + resource
            # qqq = (
            #     """
            #     SELECT ?label ?label_cs ?abstract ?sameas
            #     WHERE{
            #     <"""
            #     + uri
            #     + """> rdfs:label ?label FILTER (lang(?label) = "en") .
            #     OPTIONAL {<"""
            #     + uri
            #     + """> dbo:abstract ?abstract FILTER (lang(?abstract) = "en") .}
            #     OPTIONAL {<"""
            #     + uri
            #     + """> rdfs:label ?label_cs FILTER (lang(?label_cs) = "cs") .}
            #     OPTIONAL {<"""
            #     + uri
            #     + """> owl:sameAs ?sameas FILTER strstarts(str(?sameas),"http://cs.dbpedia.org/resource/") .}
            #     }
            # """
            # )
            # bindings = query(
            #     qqq,
            #     sparql,
            # )
            bindings = []

            label = ""
            label_cs = ""
            if bindings:
                b = bindings[0]
                label = b["label"]["value"] if "label" in b else ""
                label_cs = b["label_cs"]["value"] if "label_cs" in b else ""

            resource_aliases = aliases[resource]
            resource_examples = examples[resource]

            tsv_writer.writerow(
                [resource, resource_aliases, resource_examples, label, label_cs]
            )
            # assert len(bindings) == 1

        if args.resource == "objects":
            resource_aliases = aliases[resource]

            # if resource_aliases:
            #     uri = "http://dbpedia.org/resource/" + next(iter(resource_aliases))
            #     qqq = (
            #         """
            #         SELECT ?label ?label_cs ?abstract ?sameas
            #         WHERE{
            #         <"""
            #         + uri
            #         + """> rdfs:label ?label FILTER (lang(?label) = "en") .
            #         OPTIONAL {<"""
            #         + uri
            #         + """> dbo:abstract ?abstract FILTER (lang(?abstract) = "en") .}
            #         OPTIONAL {<"""
            #         + uri
            #         + """> rdfs:label ?label_cs FILTER (lang(?label_cs) = "cs") .}
            #         OPTIONAL {<"""
            #         + uri
            #         + """> owl:sameAs ?sameas FILTER strstarts(str(?sameas),"http://cs.dbpedia.org/resource/") .}
            #         }
            #     """
            #     )
            #     bindings = query(
            #         qqq,
            #         sparql,
            #     )
            # else:
            #     bindings = []
            bindings = []

            label = ""
            label_cs = ""
            if bindings:
                b = bindings[0]
                label = b["label"]["value"] if "label" in b else ""
                label_cs = b["label_cs"]["value"] if "label_cs" in b else ""

            resource_examples = examples[resource]

            tsv_writer.writerow(
                [resource, resource_aliases, resource_examples, label, label_cs]
            )

        if args.resource == "properties":
            # uri = "http://dbpedia.org/ontology/" + resource
            # qqq = (
            #     """
            #     SELECT ?label ?comment
            #     WHERE{
            #     <"""
            #     + uri
            #     + """> rdfs:label ?label FILTER (lang(?label) = "en") .
            #     OPTIONAL {<"""
            #     + uri
            #     + """> rdfs:comment ?comment FILTER (lang(?abstract) = "en") .}
            #     }
            # """
            # )
            # bindings = query(
            #     qqq,
            #     sparql,
            # )

            label = ""
            comment = ""

            # bindings = []
            # if bindings:
            #     b = bindings[0]
            #     label = b["label"]["value"] if "label" in b else ""
            #     comment = b["comment"]["value"] if "comment" in b else ""

            resource_aliases = aliases[resource]

            allLexs = []
            minSize = min(e["size"] for e in entries)
            for e in entries:
                if e["size"] == minSize:
                    for lex in e["lex"]:
                        if lex["lang"] in ["", "en"]:
                            allLexs.append(lex["text"])
            randomEntry = random.sample(allLexs, min(3, len(allLexs)))
            tsv_writer.writerow([resource, resource_aliases, randomEntry])


if __name__ == "__main__":
    main()
