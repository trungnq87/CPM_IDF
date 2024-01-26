#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_${IDF_VERSION}_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Step 2 : Aggregation of WRF data to SMS
# ----------------------------------------------------------------------- #
#
# Supported Python script
py02="py_02_${IDF_VERSION}_WRF_to_SMS.py"
currentdir=`pwd`

# A sub-folder
expname="SMS_WRF"
mkdir -p ${tmpdir}/${expname}

# Aggregation for WRF
wrf1sthour=1
wrfinterval=1
ndura=24       # Working with 24 durations: 3 hours to 3 days (72h)

# Hum, look ugly, right? I should write a Loop later
# I/O directories
in02a=${outdir}${hist}/bc/
out02a=${outdir}${hist}/sms/ # a/b for hist/rcp85 !

in02b=${outdir}${rcp85}/bc/
out02b=${outdir}${rcp85}/sms/

in02c=${outdir}${rcp45}/bc/
out02c=${outdir}${rcp45}/sms/

# Make it (if not yet)
mkdir -p ${out02a} ${out02b} ${out02c}

# Now submit jobs to get all files in $outb4
cd ${tmpdir}/${expname} ; test $? -eq 0 || echo "Error: check line "$LINENO

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
        cp ${currentdir}/${py02} p_${c}.py

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J wrfams_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=04:00:00

cd ${tmpdir}/${expname}
time python p_${c}.py -sl ${stationlist} -i ${in02a} -o ${out02a} -sy ${startyear} -ey ${endyear} -j ${i}
EOF
    #
#    sbatch s_${c}.script
    # 
done

# ----------------------------------------------------------------------- #
# For future projection RCP 8.5 (case B)
# ----------------------------------------------------------------------- #

# Python start with 0 so i<$nsta
for (( i=0 ; i<$nsta ; i++ )) ; do

        c=$((c+1))
        cp ${currentdir}/${py02} p_${c}.py

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J wrfams_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=04:00:00

cd ${tmpdir}/${expname}
time python p_${c}.py -sl ${stationlist} -i ${in02b} -o ${out02b} -sy ${startrcp} -ey ${endrcp} -j ${i}
EOF
    #
#    sbatch s_${c}.script
    # 
done

# ----------------------------------------------------------------------- #
# For future projection RCP 4.5 (case C)
# ----------------------------------------------------------------------- #

# Python start with 0 so i<$nsta
for (( i=0 ; i<$nsta ; i++ )) ; do

        c=$((c+1))
        cp ${currentdir}/${py02} p_${c}.py

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J wrfams_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=04:00:00

cd ${tmpdir}/${expname}
time python p_${c}.py -sl ${stationlist} -i ${in02c} -o ${out02c} -sy ${startrcp} -ey ${endrcp} -j ${i}
EOF
    #
    #sbatch s_${c}.script
    # 
done

echo "You just submitted ${c} jobs, olala !"
# ----------------------------------------------------------------------- #
# Time for Connect 4 :)
# ----------------------------------------------------------------------- #
