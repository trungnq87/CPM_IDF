#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_081123_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Step 04 : Aggregation of C-HPD data to all durations
# ----------------------------------------------------------------------- #
#
# Supported Python script
py04="py_04_090823_Aggregation_CHPD.py"
currentdir=`pwd`
in04=${outdir}${obs}/pre/ 
out04=${outdir}${obs}/agg/ 

# Aggregation to seasonal maximum series
ndura=24       # Working with 24 durations: 3 hours to 3 days (72h)
firsthour=3
interval=3
#
# ----------------------------------------------------------------------- #
#
# Make sure that we have output directory
mkdir -p ${out04}

# Now submit jobs to get all files in $outb4
cd ${tmpdir} ; test $? -eq 0 || echo "Error: check line "$LINENO

# Make sure no old files
rm -rf p_*.py
rm -rf s_*.script
rm -rf *.error
rm -rf *.out

# Create and submit jobs
#
for (( i=0 ; i<=$nsta ; i+=$ptask )) ; do

    cp ${currentdir}/${py04} p_${i}.py

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
#SBATCH -J agg_${i}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=04:00:00

cd $tmpdir
time python p_${i}.py -sl ${stationlist} -i ${in04} -o ${out04} -sy ${startyear} -ey ${endyear} -sk ${i} -nr ${k} -fh ${firsthour} -iv ${interval} -nd ${ndura}
EOF

    # And, submit it >.<
    #
    sbatch s_${i}.script
    # 
done
#
# Should follow my 5-mins rule
