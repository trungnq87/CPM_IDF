#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_${IDF_VERSION}_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Step 1 : Download data of C-HPD
# ----------------------------------------------------------------------- #
#
# Parameters ( I gathered them in one common file, now I separated them)
#
py01="py_01_${IDF_VERSION}_Select_stations.py"
currentdir=`pwd`
#
# 0. File contain station information (ID, lat, lon, ...)
#
# Go to CHPD input folder
cd ${chpdinput} ; test $? -eq 0 || echo "Error: check line "$LINENO
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
cd ${chpdinput} ; test $? -eq 0 || echo "Error: check line "$LINENO
#
for i in `cat $out01 | awk -F',' '{print $2}'` ;
do
  wget ${chpdacce}${i}.csv
done
#
# Should follow my 5-mins rule
# Tue Jan  9 11:23:38 EST 2024
# real	3m45.680s
# user	0m18.982s
# sys	0m11.426s
