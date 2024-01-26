#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_${IDF_VERSION}_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Step 1 : Aggregation of C-HPD data to SMS
# ----------------------------------------------------------------------- #
#
# Supported Python script
py01="py_01_${IDF_VERSION}_CHPD_to_SMS.py"
currentdir=`pwd`
in01=${outdir}${obs}/pre/ 
out01=${outdir}${obs}/sms/ 

# A sub-folder
expname="SMS_CHPD"
mkdir -p ${tmpdir}/${expname}

# Aggregation to seasonal maximum series
ndura=24       # Working with 24 durations: 3 hours to 3 days (72h)
firsthour=3
interval=3

# Make sure that we have output directory
mkdir -p ${out01}

# Now submit jobs to get all files in $outb4
cd ${tmpdir}/${expname} ; test $? -eq 0 || echo "Error: check line "$LINENO

# Make sure no old files
rm -rf p_*.py
rm -rf s_*.script
rm -rf *.error
rm -rf *.out

# Create and submit jobs
#
for (( i=0 ; i<=$nsta ; i+=$ptask )) ; do

    cp ${currentdir}/${py01} p_${i}.py

    j=$(( $i + $ptask )) 
    if (( $j < $nsta )) ; then
       k=${ptask}
    else : 
       k=$(($nsta - $i))
    fi

# This is the sbatch script file
cat <<EOF >> s_${i}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J sms_${i}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=04:00:00

cd ${tmpdir}/${expname}
time python p_${i}.py -sl ${stationlist} -i ${in01} -o ${out01} -sy ${startyear} -ey ${endyear} -sk ${i} -nr ${k} -fh ${firsthour} -iv ${interval} -nd ${ndura}
EOF

# And, submit it >.<
    #
    sbatch s_${i}.script
    # 
done
#
# Should follow my 5-mins rule
# Check
#Thu Mar  9 20:38:11 EST 2023
