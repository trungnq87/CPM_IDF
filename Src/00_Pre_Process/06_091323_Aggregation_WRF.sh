#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_081123_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Step 06 : Aggregation of WRF data to all durations
# ----------------------------------------------------------------------- #
#
# Supported Python script
py06="py_06_091323_Aggregation_WRF.py"
currentdir=`pwd`

# Aggregation for WRF
wrf1sthour=1
wrfinterval=1
ndura=24       # Working with 24 durations: 3 hours to 3 days (72h)

# I/O directories
in06a=${outdir}${hist}/pre/
out06a=${outdir}${hist}/agg/ # a/b for hist/rcp85 !

in06b=${outdir}${rcp85}/pre/
out06b=${outdir}${rcp85}/agg/

# Make it (if not yet)
mkdir -p ${out06a} ${out06b}

# Still go to temporary folder to work
cd ${tmpdir} ; test $? -eq 0 || echo "Error: check line "$LINENO

# Make sure no old files
rm -rf p_*.py
rm -rf s_*.script
rm -rf *.error
rm -rf *.out

# Count jobs (for all cases)
c=0

# ----------------------------------------------------------------------- #
# For historical simulation (case A)
# ----------------------------------------------------------------------- #

# Python start with 0 so i<$nsta
for (( i=0 ; i<$nsta ; i++ )) ; do

        c=$((c+1))
        cp ${currentdir}/${py06} p_${c}.py

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J agg_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=04:00:00

cd $tmpdir
time python p_${c}.py -i ${in06a} -o ${out06a} -sl ${stationlist} -sy ${startyear} -ey ${endyear} -st ${i} -fh ${wrf1sthour} -iv ${wrfinterval} -nd ${ndura}
EOF
    #
    sbatch s_${c}.script
    # 
done

# ----------------------------------------------------------------------- #
# For future projection RCP 8.5 (case B)
# ----------------------------------------------------------------------- #

# Python start with 0 so i<$nsta
for (( i=0 ; i<$nsta ; i++ )) ; do

        c=$((c+1))
        cp ${currentdir}/${py06} p_${c}.py

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J agg_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=04:00:00

cd $tmpdir
time python p_${c}.py
time python p_${c}.py -i ${in06b} -o ${out06b} -sl ${stationlist} -sy ${startrcp} -ey ${endrcp} -st ${i} -fh ${wrf1sthour} -iv ${wrfinterval} -nd ${ndura}
EOF
    #
    sbatch s_${c}.script
    # 
done

echo "You just submitted ${c} jobs, olala !"
# ----------------------------------------------------------------------- #
# Time for Connect 4 :)
# ----------------------------------------------------------------------- #
