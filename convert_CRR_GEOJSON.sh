#!/bin/bash

CRR_source_dir="/data/eumetcast/afr-1/uncompressed"
CRR_output_dir="/data/FASTA/CRR_geojson"

input_fil=$( ls -lthr ${CRR_source_dir}/S_NWC_CRR_* | tail -1 | awk '{ print $9 }' )

source /home/ncas-sat/anaconda3/etc/profile.d/conda.sh
conda activate adaguc

python /opt/scripts/convert_CRR_GEOJSON.py ${input_fil}

conda deactivate

rsync -auvr -e "ssh -i /home/ncas-sat/.ssh/id_rsa" ${CRR_output_dir}/* earajr@see-gw-01.leeds.ac.uk:/nfs/a321/earajr/FASTA/CRR_conversion/geojson/.

find ${CRR_output_dir}/. -type f -mmin +360 -delete
