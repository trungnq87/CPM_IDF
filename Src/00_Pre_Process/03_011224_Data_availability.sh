#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_${IDF_VERSION}_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Step 03 : Check data availability
# ----------------------------------------------------------------------- #
#
# Supported Python script
py03="py_03_${IDF_VERSION}_Data_availability.py"
currentdir=`pwd`
in03=${outdir}${obs}/pre/ # It's ${out02}

# A sub-folder
expname="Data_Availability"
mkdir -p ${tmpdir}/${expname}

# Check for duration of 72 h
duration=72

# Allow only stations with > 90 % non-NaN data
threshold=90

# With color-level for plotting map
bf="0 10 50 90 100"
ba="90 92 94 96 98 100"

# Still go to temporary folder to work
cd ${tmpdir}/${expname} ; test $? -eq 0 || echo "Error: check line "$LINENO

# Make sure no old files
rm -rf da.py
rm -rf da.script

# Just one file
cp ${currentdir}/${py03} da.py

# This is the sbatch script file
cat <<EOF >> da.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J da
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=04:00:00

cd ${tmpdir}/${expname}
time python da.py -sl ${chpdinput}/${out01} -i ${in03} -o ${pngdir} -sy ${startyear} -ey ${endyear} -bf ${bf} -ba ${ba} -du ${duration} -th ${threshold}
EOF

# And, submit it >.<
sbatch da.script

#
# Should follow my 5-mins rule
