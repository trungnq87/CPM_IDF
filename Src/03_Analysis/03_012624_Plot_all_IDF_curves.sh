#!/bin/bash
#
# Firstly, load common variables
# Use this ?
#. ../AA_${IDF_VERSION}_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# Working directory 
currentdir=`pwd`

# Data directory
outdir=${wrkdir}Output/

# Temporary directory (where you create and submit jobs)
tmpdir=${wrkdir}/Tmp/

# Store all figures
pngdir=${outdir}/PNG/

# Make sure that we have output directory (and temporary one)
mkdir -p ${pngdir}
mkdir -p ${tmpdir}

# Cases for outputs
obs="CHPD"
hist="WRF_hi"
rcp85="WRF_85"
rcp45="WRF_45"

# Supported Python script
py01="py_03_012624_IDF_curves_plot.py"

# Need the stationlist
stationlist=${outdir}${obs}/pre/Stations_list.csv

# I/O directories
inobs=${outdir}${obs}/idf/ 
inhist=${outdir}${hist}/idf/
inrcp85=${outdir}${rcp85}/idf/
inrcp45=${outdir}${rcp45}/idf/

# Once upon a time
#set -x

# A sub-folder
expname="All_IDF"
mkdir -p ${tmpdir}/${expname}
mkdir -p ${pngdir}/${expname}
# Now submit jobs to get outputs
cd ${tmpdir}/${expname} ; test $? -eq 0 || echo "Error: check line "$LINENO

# Make sure no old files
rm -rf p_idf.py
rm -rf s_idf.script
rm -rf *.error
rm -rf *.out

# Copy python file (redundant?)
cp ${currentdir}/${py01} p_idf.py

# Create and submit jobs
#
# This is the sbatch script file
cat <<EOF >> s_idf.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J idf_plot
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=04:00:00

cd ${tmpdir}/${expname}
time python p_idf.py -sl ${stationlist} -o ${pngdir}/${expname}/ -a ${inobs} -b ${inhist} -c ${inrcp45} -d ${inrcp85} -na Observation -nb "Historical WRF" -nc "RCP 4.5" -nd "RCP 8.5" -th 10
EOF

# And, submit it >.<
sbatch s_idf.script

# Should follow my 5-mins rule
