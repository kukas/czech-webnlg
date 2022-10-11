#!/bin/bash
source translate_utils.sh

CUBBIT_MODEL="en-cs"
SUFFIX="_CZECH_cubbitt"
VERSION="release_v3.0_ru_test_fixed"
WEBNLG_ROOT="./data/webnlg-dataset"
WORKDIR="data/cubbitt_translation/"

dump_and_merge $VERSION $WEBNLG_ROOT $WORKDIR

transl_dir="$WORKDIR/cubbitt_translations-$VERSION$SUFFIX"
mkdir -p $transl_dir

split --numeric-suffixes --additional-suffix=.txt --number=l/53 $WORKDIR/${VERSION}_ENGLISH.txt $transl_dir/${VERSION}_ENGLISH_split.

for file in $transl_dir/${VERSION}_ENGLISH_split.*
do
    new_file="$transl_dir/${VERSION}_CZECH${file#$transl_dir/${VERSION}_ENGLISH}"
    echo $new_file

    # try fetching the translation until the translation is not empty
    while true; do
        curl -X POST -F input_text=@$file "https://lindat.mff.cuni.cz/services/translation/api/v2/models/$CUBBIT_MODEL?src=en&tgt=cs" -H  "accept: text/plain" >  $new_file
        # check if the $new_file is empty
        if [ -s $new_file ]; then
            break
        fi
    done

    

    # Remove the last empty line (added by the lindat service)
    sed -i '$ d' $new_file
done

cat $transl_dir/${VERSION}_CZECH_split.*.txt > $WORKDIR/$VERSION$SUFFIX.txt

check_empty_lines $WORKDIR$VERSION$SUFFIX.txt

translation_into_splits $VERSION $SUFFIX $WORKDIR

# cleanup
dump_and_merge_cleanup $VERSION $WORKDIR
rm $transl_dir/${VERSION}_ENGLISH_split.*
rm $WORKDIR/$VERSION$SUFFIX.txt
