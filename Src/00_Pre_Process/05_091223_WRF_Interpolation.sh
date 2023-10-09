#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_081123_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Interpolation WRF output to station location
# Now submit jobs to get all files in ../Output/WRF_*/pre/
# ----------------------------------------------------------------------- #
#
# Supported Python script
py05="py_05_091123_WRF_Interpolation.py"
currentdir=`pwd`

# I/O directories
in05a=${indir}${hist}/
out05a=${outdir}${hist}/pre/ # a/b for hist/rcp85 !

in05b=${indir}${rcp85}/
out05b=${outdir}${rcp85}/pre/

# Make it (if not yet)
mkdir -p ${out05a} ${out05b}

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
    for m in $month ; do

        c=$((c+1))
        cp ${currentdir}/${py05} p_${c}.py

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J int_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=01:00:00

cd $tmpdir
time python p_${c}.py -i ${in05a} -o ${out05a} -sl ${stationlist} -sy ${startyear} -ey ${endyear} -m ${m} -st ${i}
EOF
    # Sorry, you have a limit of 500 jobs (don't do this automatically)
    #sbatch s_${c}.script
    #sleep 300
    # 
    done
done

# ----------------------------------------------------------------------- #
# For future projection RCP 8.5 (case B)
# ----------------------------------------------------------------------- #

# Python start with 0 so i<$nsta
for (( i=0 ; i<$nsta ; i++ )) ; do
    for m in $month ; do

        c=$((c+1))
        cp ${currentdir}/${py05} p_${c}.py

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J int_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=01:00:00

cd $tmpdir
time python p_${c}.py -i ${in05b} -o ${out05b} -sl ${stationlist} -sy ${startrcp} -ey ${endrcp} -m ${m} -st ${i}
EOF
    #
    #sbatch s_${c}.script
    #sleep 300
    # 
    done
done

# ----------------------------------------------------------------------- #
# Time for Connect 4 :)
# ----------------------------------------------------------------------- #
