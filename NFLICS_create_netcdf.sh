#!/bin/bash

cd /data/CEH_NFLICS

export CONDA_SHLVL=2
export CONDA_EXE=/home/ncas-sat/anaconda3/bin/conda
export CONDA_PREFIX=/home/ncas-sat/anaconda3/envs/NFLICS
export PROJ_LIB=/home/ncas-sat/anaconda3/envs/NFLICS/share/proj
export CONDA_PREFIX_1=/home/ncas-sat/anaconda3
export CONDA_PYTHON_EXE=/home/ncas-sat/anaconda3/bin/python
export CONDA_PROMPT_MODIFIER=(NFLICS)
export PATH=/home/ncas-sat/anaconda3/envs/NFLICS/bin:/home/ncas-sat/anaconda3/condabin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
export CONDA_DEFAULT_ENV=NFLICS
export CONDA_ENVS_PATH=/home/ncas-sat/anaconda3/envs
export _CONDA_ROOT=/home/ncas-sat/anaconda3

DATE=$( date -u -d "15 mins ago" "+%Y%m%d%H$( printf "%02d" $(( $( date -u -d '15 minutes ago' +'%M') / 15 * 15 )) )" )

YYYY=${DATE:0:4}
MM=${DATE:4:2}
DD=${DATE:6:2}

hh=${DATE:8:2}
mm=${DATE:10:2}

python CEH_extract.py /data/eumetcast/afr-1/uncompressed ${YYYY}${MM}${DD} ${hh}${mm}


