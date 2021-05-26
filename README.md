# brl_data_tools
Tools for handling un-labeled training images for Angelina Braille Reader

## Requirements

- Linux Ubuntu or CygWin (other: not tested)
- Git + Git LFS
- Python 3.8


## setup
substitute `python` with your system's Python3.8 command (may be `python3`, `py3`, etc).
```shell script
git clone --recursive https://github.com/braille-systems/brl_data_tools.git
cd brl_data_tools
mkdir data
wget -O data/ref.zip http://azuev.ddns.net/~valera/brl_public/ref.zip && unzip data/ref.zip -d data
wget -O data/1_raw.zip http://azuev.ddns.net/~valera/brl_public/1_raw.zip && unzip data/1_raw.zip -d data
wget -O AngelinaReader/weights/model.t7 http://angelina-reader.ovdv.ru/retina_chars_eced60.clr.008

python -m pip install --upgrade pip
python -m pip install virtualenv
python -m venv env
source env/bin/activate # CygWin: source env/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
## processing data
### renaming and cropping
```shell script
python scripts/rename.py
python scripts/crop.py
```

### pseudolabeling
```shell script
source env/bin/activate # CygWin: source env/Scripts/activate
python AngelinaReader/run_local.py data/2_renamed data/3_pseudolabeled -l EN -o --save_dev
```

### pre-processing text files for alignment
```shell script
python scripts/preprocess_text.py
python scripts/find_regions_of_interest.py
```

### performing alignment & calculating statistics
```shell script
python scripts/needleman_wunsch.py
python scripts/postprocess_text.py
```

## semi-supervised learning
### setup
```shell script
cd AngelinaReader
git clone --recursive https://github.com/braille-systems/brl_ocr.git
cd ..
```
### naive SSL
```shell script
source env/bin/activate # CygWin: source env/Scripts/activate
python scripts/split_test_train.py
cd AngelinaReader
# you may want to tweak `batch_size` in model/params.py
python model/train.py
```
