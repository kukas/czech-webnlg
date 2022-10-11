import csv
from glob import glob
import pandas

# https://stackoverflow.com/questions/69544464/python-iterating-n-items-of-array-at-a-time
def chunks(arr: list, n: int):
    """
    Yield successive n-sized chunks from arr.
    :param arr
    :param n
    :return generator
    """
    for i in range(0, len(arr), n):
        yield arr[i : i + n]


human_feedback = []


# First round of feedback
for csvfile in glob("WebNLG Překlad *"):
    with open(csvfile) as f:
        csv_reader = csv.reader(f)

        engine = next(csv_reader)[3]
        print(csvfile, engine)
        next(csv_reader)
        for row in csv_reader:
            if row[0] and row[1]:
                translation = row[3]
                adequacy = float(row[0].replace(",", "."))
                fluency = float(row[1].replace(",", "."))
                human_feedback.append(
                    {
                        "engine": engine,
                        "adequacy": adequacy,
                        "fluency": fluency,
                        "rdf": "",
                        "lex": lex,
                        "translation": translation,
                    }
                )
            else:
                lex = row[3]

# Second round of feedback
for csvfile in glob("WebNLG překlad 2 *"):
    with open(csvfile) as f:
        csv_reader = csv.reader(f)

        engine = next(csv_reader)[4]
        print(csvfile, engine)
        next(csv_reader)
        # for rdf_row, lex_row, trans_row in chunks(list(csv_reader), 3):
        #     print(rdf_row, lex_row, trans_row)
        #     rdf = rdf_row[3][len("RDF triples:  ") :]
        #     lex = lex_row[3][len("Lexicalisation: ") :]
        #     translation = trans_row[3][len("Translation:  ") :]
        #     adequacy = float(trans_row[0])
        #     fluency = float(trans_row[1])
        #     print(adequacy, fluency, rdf, lex, translation)
        for row in csv_reader:
            if row[3].startswith("RDF"):
                rdf = row[3][len("RDF triples:  ") :]
            if row[3].startswith("Lexicalisation"):
                lex = row[3][len("Lexicalisation: ") :]
            if row[3].startswith("Translation"):
                translation = row[3][len("Translation:  ") :]
                adequacy = float(row[0]) if row[0] else None
                fluency = float(row[1]) if row[1] else None
                human_feedback.append(
                    {
                        "engine": engine,
                        "adequacy": adequacy,
                        "fluency": fluency,
                        "rdf": rdf,
                        "lex": lex,
                        "translation": translation,
                    }
                )

pandas.DataFrame(human_feedback).to_csv("webnlg_translation_human_feedback.csv")
