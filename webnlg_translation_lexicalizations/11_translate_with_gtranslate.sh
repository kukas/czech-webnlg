#!/bin/bash
source translate_utils.sh


SUFFIX="_CZECH_gtranslate"
VERSION="release_v3.0_ru_test_fixed"
WEBNLG_ROOT="./data/webnlg-dataset"
WORKDIR="data/gtranslate_translation/"

dump_and_merge $VERSION $WEBNLG_ROOT $WORKDIR

python txt_to_xlsx.py $WORKDIR${VERSION}_ENGLISH.txt $WORKDIR${VERSION}_ENGLISH.xlsx

echo "Now upload the file '$WORKDIR${VERSION}_ENGLISH.xlsx' to Google Translate"
echo "get the translated xlsx and rename it to '$WORKDIR$VERSION$SUFFIX.xlsx'"
echo "Press ENTER to continue..."
read

python txt_to_xlsx.py $WORKDIR$VERSION$SUFFIX.xlsx $WORKDIR$VERSION$SUFFIX.txt

check_empty_lines $WORKDIR$VERSION$SUFFIX.txt

translation_into_splits $VERSION $SUFFIX $WORKDIR

# cleanup
dump_and_merge_cleanup $VERSION $WORKDIR
rm $WORKDIR/${VERSION}_ENGLISH.xlsx
rm $WORKDIR/$VERSION$SUFFIX.txt
