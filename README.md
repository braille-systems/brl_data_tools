# brl_data_tools
Tools for handling un-labeled training images for Angelina Braille Reader

## setup
```shell script
git clone --recursive https://github.com/braille-systems/brl_data_tools.git
wget -O data/1_raw.zip http://azuev.ddns.net/~valera/brl_public/1_raw.zip
gzip -dS .zip data/1_raw.zip

cd AngelinaReader
python -m pip install --upgrade pip
python -m pip install virtualenv
python -m venv env
source env/bin/activate # CygWin: source env/Scripts/activate
wget -O weights/model.t7 http://angelina-reader.ovdv.ru/retina_chars_eced60.clr.008
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cd ..
```
## processing data
### renaming
```shell script
python scripts/rename.py
```

### pseudolabeling
```shell script
source AngelinaReader/env/bin/activate # CygWin: source AngelinaReader/env/Scripts/activate
python AngelinaReader/run_local.py data/2_renamed data/3_pseudolabeled -l EN -o --save_dev
```
