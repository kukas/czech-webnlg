# Tools for translating the WebNLG corpus

Czech translation of the [WebNLG corpus](https://gitlab.com/shimorina/webnlg-dataset).

## How to reproduce

First you must obtain the WebNLG data by cloning the dataset repository.

```
git clone git@gitlab.com:shimorina/webnlg-dataset.git ../webnlg-dataset
```

### Translate WebNLG v3 Russian version (based on WebNLG v2)

To translate this version follow the same steps as with english with one difference. As a first step, create a modified version of this dataset using the script `00_add_english_lex_to_v3_ru.sh`. This creates a copy of the russian set with english lexicalizations for the test set as well (they are missing in the russian version).

```
./00_add_english_lex_to_v3_ru.sh
./10_translate_with_cubbitt.sh
./11_translate_with_gtranslate.sh
./12_translate_with_deepl.sh
./20_add_lexicalizations.sh release_v3.0_ru_test_fixed
```

### WebNLG v3 English version

Copy the release v3.0 to the data dir. Modify and run scripts `1X_translate_with_*.sh` to create the translations of the english lexicalizations. 

Then run the `20_add_lexicalizations.sh` script to create new version of the WebNLG corpus with the translated lexicalizations included.

```
cp ../webnlg-dataset/release_v3.0/en ./data/webnlg-dataset/release_v3.0/en
./10_translate_with_cubbitt.sh
./11_translate_with_gtranslate.sh
./12_translate_with_deepl.sh
./20_add_lexicalizations.sh release_v3.0_en
```