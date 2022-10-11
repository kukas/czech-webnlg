#!/bin/bash

set -e

# Add translations to the english v3 version
# python add_lexicalizations.py release_v3.0_en train cs webnlg-dataset-new release_v3.0_en_train_CZECH_deepl.txt release_v3.0_en_train_CZECH_gtranslate.txt release_v3.0_en_train_CZECH_cubbitt.txt
# python add_lexicalizations.py release_v3.0_en dev cs webnlg-dataset-new release_v3.0_en_dev_CZECH_deepl.txt release_v3.0_en_dev_CZECH_gtranslate.txt release_v3.0_en_dev_CZECH_cubbitt.txt
# python add_lexicalizations.py release_v3.0_en test cs webnlg-dataset-new release_v3.0_en_test_CZECH_deepl.txt release_v3.0_en_test_CZECH_gtranslate.txt release_v3.0_en_test_CZECH_cubbitt.txt

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <webnlg-version>"
    exit 1
fi

# version release_v3.0_en
if [[ $1 == "release_v3.0_en" ]]; then
    # Add translations to the english v3 version
    for split in train dev test; do
        python add_lexicalizations.py \
            --root ./data/webnlg-dataset \
            --version release_v3.0_en \
            --split $split --lang cs \
            --new_root data/webnlg-dataset-cz \
            --lexicalization_files data/deepl_translation/release_v3.0_ru_test_fixed_${split}_CZECH_deepl.txt data/gtranslate_translation/release_v3.0_ru_test_fixed_${split}_CZECH_gtranslate.txt data/cubbitt_translation/release_v3.0_ru_test_fixed_${split}_CZECH_cubbitt.txt \
            --source_names deepl gtranslate cubbitt
    done;
fi
if [[ $1 == "release_v3.0_ru_test_fixed" ]]; then
    # Add translations to the russian v3 version
    for split in train dev test; do
        python add_lexicalizations.py \
            --root ./data/webnlg-dataset \
            --version release_v3.0_ru_test_fixed \
            --split $split --lang cs \
            --new_root data/webnlg-dataset-cz \
            --lexicalization_files data/deepl_translation/release_v3.0_ru_test_fixed_${split}_CZECH_deepl.txt data/gtranslate_translation/release_v3.0_ru_test_fixed_${split}_CZECH_gtranslate.txt data/cubbitt_translation/release_v3.0_ru_test_fixed_${split}_CZECH_cubbitt.txt \
            --source_names deepl gtranslate cubbitt
    done;
fi
