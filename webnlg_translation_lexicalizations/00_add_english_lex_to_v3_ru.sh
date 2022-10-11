#!/bin/bash
mkdir -p ./data/webnlg-dataset/release_v3.0/ru_test_fixed
cp -r ../webnlg-dataset/release_v3.0/ru/* ./data/webnlg-dataset/release_v3.0/ru_test_fixed/

python add_english_lex_to_v3_ru.py ../webnlg-dataset/ ./data/webnlg-dataset/release_v3.0/ru_test_fixed