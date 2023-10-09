#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_081123_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Step 1 : Download data of C-HPD
# ----------------------------------------------------------------------- #
#
# Parameters ( I gathered them in one common file, now I separated them)
#
py01="py_01_080923_Select_stations.py"
currentdir=`pwd`
#
# 0. File contain station information (ID, lat, lon, ...)
#
# Go to CHPD input folder
cd ${chpdinput}
# Download info file
wget ${chpdinfo}
# !!! Remember !!! File name of CSV file will be changed by time 
# (update c20221129 to whatever day that they currently have)
#
# 1. Select only stations from IL, IN, OH, KY and download them
#
cd ${currentdir} ; test $? -eq 0 || echo "Error: check line "$LINENO
time python ${py01} -i ${chpdinput}/${chpdvers} -o ${chpdinput}/${out01} -s $states 
test $? -eq 0 || echo "Error: check line "$LINENO
#
# 2. Now download only selected stations
#
# Go to CHPD input folder
cd ${chpdinput}
#
for i in `cat $out01 | awk -F',' '{print $2}'` ;
do
  wget ${chpdacce}${i}.csv
done
#
# Should follow my 5-mins rule
# Yes : 1st try
# Fri Aug 11 14:23:26 EDT 2023
# real	2m10.383s
# user	0m18.546s
# sys	0m9.968s
