# MB-iSTFT-VITS with Multilingual Implementations

<br>
This is an implementation of (https://github.com/misakiudon/MB-iSTFT-VITS-multilingual) to support conversion to various languages. MB-iSTFT-VITS showed 4.1 times faster inference time compared with original VITS! for Dutch Language </br>


- Currently Supported: Dutch
- 


# How to use
Python >= 3.6 (Python == 3.10 is suggested)

## Clone this repository
```sh
git clone git@github.com:PrabalAryal/MB-iSTFT-VITS-multilingual.git
```

## Install requirements
```sh
pip install -r requirements.txt
```
You may need to install espeak first: `apt-get install espeak`

## Create manifest data
### Single speaker
"n_speakers" should be 0 in config.json
```
path/to/XXX.wav|transcript
```
- Example
```
dataset/001.wav|het
```

### Mutiple speakers
Speaker id should start from 0 
```
path/to/XXX.wav|speaker id|transcript
```
- Example
```
dataset/001.wav|0|het
```

## Preprocess
Run hf_to_req_dataset.py if your dataset is in huggingface
then run convert_to_22050.py to convert audio to required '22050Hz / Mono / PCM-16` format

# Single speaker
python preprocess.py --text_index 1 --filelists path/to/filelist_train.txt path/to/filelist_val.txt --text_cleaners 'Duttch_Cleaners'

# Mutiple speakers
python preprocess.py --text_index 2 --filelists path/to/filelist_train.txt path/to/filelist_val.txt --text_cleaners 'Dutch_Cleaners'
```
```

## Build monotonic alignment search
```sh
# Cython-version Monotonoic Alignment Search
cd monotonic_align
mkdir monotonic_align
python setup.py build_ext --inplace
```

## Setting json file in [configs](configs)

| Model | How to set up json file in [configs](configs) | Sample of json file configuration|
| :---: | :---: | :---: |
| iSTFT-VITS | ```"istft_vits": true, ```<br>``` "upsample_rates": [8,8], ``` | ljs_istft_vits.json |
| MB-iSTFT-VITS | ```"subbands": 4,```<br>```"mb_istft_vits": true, ```<br>``` "upsample_rates": [4,4], ``` | ljs_mb_istft_vits.json |
| MS-iSTFT-VITS | ```"subbands": 4,```<br>```"ms_istft_vits": true, ```<br>``` "upsample_rates": [4,4], ``` | ljs_ms_istft_vits.json |

For tutorial, check `config/tsukuyomi_chan.json` for more examples
- If you have done preprocessing, set "cleaned_text" to true. 
- Change `training_files` and `validation_files` to the path of preprocessed manifest files. 
- Select same `text_cleaners` you used in preprocessing step. 

## Train
```sh
# Single speaker
python train_latest.py -c <config> -m <folder>

# Mutiple speakers
python train_latest_ms.py -c <config> -m <folder>
```
In the case of training MB-iSTFT-VITS with Japanese tutorial corpus, run the following script. Resume training from lastest checkpoint is automatic.
```sh
python train_latest.py -c configs/dutch_nl.json -m t<folder>
```

After the training, you can check inference audio using [inference.ipynb](inference.ipynb)

## References

- https://github.com/MasayaKawamura/MB-iSTFT-VITS
- https://github.com/CjangCjengh/vits
- https://github.com/Francis-Komizu/VITS
- https://github.com/misakiudon/MB-iSTFT-VITS-multilingual
