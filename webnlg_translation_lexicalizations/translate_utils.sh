#!/bin/bash

function dump_and_merge {
    VERSION=$1
    ROOT=$2
    WORKDIR=$3

    mkdir -p $WORKDIR

    python dump.py --root $ROOT $VERSION train > $WORKDIR/${VERSION}_train_ENGLISH.txt
    python dump.py --root $ROOT $VERSION dev > $WORKDIR/${VERSION}_dev_ENGLISH.txt
    python dump.py --root $ROOT $VERSION test > $WORKDIR/${VERSION}_test_ENGLISH.txt

    cat $WORKDIR/${VERSION}_train_ENGLISH.txt $WORKDIR/${VERSION}_dev_ENGLISH.txt $WORKDIR/${VERSION}_test_ENGLISH.txt > $WORKDIR/${VERSION}_ENGLISH.txt
    check_empty_lines $WORKDIR/${VERSION}_ENGLISH.txt
}

function check_empty_lines {
    FILE=$1
    if grep -q '^$' $FILE; then
        echo "ERROR: Empty lines found in $FILE"
        exit 1
    fi
}

function dump_and_merge_cleanup {
    VERSION=$1
    WORKDIR=$2
    rm $WORKDIR/${VERSION}_train_ENGLISH.txt
    rm $WORKDIR/${VERSION}_dev_ENGLISH.txt
    rm $WORKDIR/${VERSION}_test_ENGLISH.txt
    rm $WORKDIR/${VERSION}_ENGLISH.txt
}

function translation_into_splits {
    VERSION=$1
    SUFFIX=$2
    WORKDIR=$3

    train_lines=$(wc -l < $WORKDIR/${VERSION}_train_ENGLISH.txt)
    dev_start_line=$(( $train_lines + 1))
    dev_lines=$(wc -l < $WORKDIR/${VERSION}_dev_ENGLISH.txt)
    test_start_line=$(( $dev_lines + 1))
    test_lines=$(wc -l < $WORKDIR/${VERSION}_test_ENGLISH.txt)

    # create the top of file: 
    head -n $train_lines $WORKDIR/${VERSION}$SUFFIX.txt > $WORKDIR/${VERSION}_train$SUFFIX.txt
    tail -n +$dev_start_line $WORKDIR/${VERSION}$SUFFIX.txt > $WORKDIR/${VERSION}_tail$SUFFIX.txt

    head -n $dev_lines $WORKDIR/${VERSION}_tail$SUFFIX.txt > $WORKDIR/${VERSION}_dev$SUFFIX.txt
    tail -n +$test_start_line $WORKDIR/${VERSION}_tail$SUFFIX.txt > $WORKDIR/${VERSION}_test$SUFFIX.txt

    # check if the number of english test lexicalizations match the number of czech test lexicalizations
    test_lines2=$(wc -l < $WORKDIR/${VERSION}_test$SUFFIX.txt)
    if [ $test_lines -ne $test_lines2 ]; then
        echo "ERROR: Number of lines in the test file does not match the number of lines in the test file"
        exit 1
    fi

    rm $WORKDIR/${VERSION}_tail$SUFFIX.txt
}
