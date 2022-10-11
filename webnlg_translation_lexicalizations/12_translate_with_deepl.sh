#!/bin/bash
source translate_utils.sh


SUFFIX="_CZECH_deepl"
VERSION="release_v3.0_ru_test_fixed"
WEBNLG_ROOT="./data/webnlg-dataset"
WORKDIR="data/deepl_translation/"
SPLIT_MAXSIZE=1000000

dump_and_merge $VERSION $WEBNLG_ROOT $WORKDIR

SIZE=$(wc -c < $WORKDIR${VERSION}_ENGLISH.txt)
(( SPLITS=(SIZE+SPLIT_MAXSIZE-1)/SPLIT_MAXSIZE ))

split --numeric-suffixes --additional-suffix=.txt --number=l/$SPLITS $WORKDIR${VERSION}_ENGLISH.txt $WORKDIR${VERSION}_ENGLISH_split.

echo "Now upload the files '$WORKDIR${VERSION}_ENGLISH_split.0X.txt' into the DeepL Pro file translation service"
echo "to create $SPLITS files containing Czech translations with names: '${VERSION}_ENGLISH_split.0X cs.txt'"
echo "Move the files to '$WORKDIR'"
echo "Press ENTER to continue..."
read

cat $WORKDIR${VERSION}_ENGLISH_split.*\ cs.txt > $WORKDIR$VERSION$SUFFIX.txt

check_empty_lines $WORKDIR$VERSION$SUFFIX.txt

translation_into_splits $VERSION $SUFFIX $WORKDIR

# cleanup
dump_and_merge_cleanup $VERSION $WORKDIR
rm $WORKDIR${VERSION}_ENGLISH_split.*
rm $WORKDIR$VERSION$SUFFIX.txt
