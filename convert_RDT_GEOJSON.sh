#!/bin/bash

RDT_source_dir="/data/eumetcast/afr-1/uncompressed"
RDT_input_dir="/data/FASTA/ADAGUC-utilities.git/NWCSAF2ADAGUC/RDT/data"
RDT_output_dir="/data/FASTA/ADAGUC-utilities.git/NWCSAF2ADAGUC/RDT/data/adaguc-autowms/RDT-CW/NOW"
convert_dir="/data/FASTA/ADAGUC-utilities.git/NWCSAF2ADAGUC/RDT"

rm -rf ${RDT_input_dir}/*.nc

ln -s ${RDT_source_dir}/S_NWC_RDT-CW_MSG4_global*.nc ${RDT_input_dir}/.

for fil in ${RDT_output_dir}/*.geojson
do
   fil=$( basename ${fil})
   YYYY=${fil:35:4}
   MM=${fil:39:2}
   DD=${fil:41:2}
   hh=${fil:44:2}
   mm=${fil:46:2}

   rm -rf ${RDT_input_dir}/S_NWC_RDT-CW_MSG4_global-VISIR_${YYYY}${MM}${DD}T${hh}${mm}00Z*

done	

source /home/ncas-sat/anaconda3/etc/profile.d/conda.sh
conda activate adaguc

cd ${convert_dir}

python nwcpy_rdt_to_geoJSON.py

conda deactivate

rsync -auvr -e "ssh -i /home/ncas-sat/.ssh/id_rsa" ${RDT_output_dir}/* earajr@see-gw-01.leeds.ac.uk:/nfs/a321/earajr/FASTA/NWCSAF_to_AGADUC/ADAGUC-utilities.git/NWCSAF2ADAGUC/RDT/data/adaguc-autowms/RDT-CW/NOW/.

find ${RDT_output_dir}/. -type f -mmin +360 -delete
