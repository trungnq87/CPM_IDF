#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_${IDF_VERSION}_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Step 2 : Pre-process (or re-format) C-HPD data
# ----------------------------------------------------------------------- #
#
# Supported Python script
py02="py_02_${IDF_VERSION}_Preprocess_CHPD.py"
currentdir=`pwd`

# Output
out02=${outdir}${obs}/pre/
mkdir -p ${out02}

# Now, I want a sub-folder for each tests (saving for Paper Review Process)
expname="PreProc_CHPD"
mkdir -p ${tmpdir}/${expname}

# Now submit jobs to get all files in $out02
cd ${tmpdir}/${expname} ; test $? -eq 0 || echo "Error: check line "$LINENO

# Make sure no old files
rm -rf p_*.py
rm -rf s_*.script

# Create and submit jobs
for (( i=0 ; i<=$nline ; i+=$ptask )) ; do

    # Is it the story of memory access ?
    cp ${currentdir}/${py02} p_${i}.py

    j=$(( $i + $ptask )) 
    if (( $j < $nline )) ; then
       k=${ptask}
    else : 
       k=$(($nline - $i))
    fi

# This is the sbatch script file
cat <<EOF >> s_${i}.script
#!/bin/bash
#SBATCH -J chpd_${i}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=04:00:00
#SBATCH -A r00199

cd ${tmpdir}/${expname}
time python p_${i}.py -sl ${chpdinput}/${out01} -i ${chpdinput}/ -o ${out02} -sy ${startyear} -ey ${endyear} -sk ${i} -nr ${k}
EOF
#
# And, submit it >.<
    #
    sbatch s_${i}.script
    # 
done
#
# Should follow my 5-mins rule
# Check
# Thu Mar  9 13:02:43 EST 2023
# Each job from 1 min to 35(?) mins 
