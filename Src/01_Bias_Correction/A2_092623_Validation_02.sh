#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_081123_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Bias correction of WRF output
# Now submit jobs to get all files in ../Output/WRF_*/bc/
# ----------------------------------------------------------------------- #
#

# Supported Python script
r01="R_A2_092623_Validation_02.Rscript"
currentdir=`pwd`

# I/O directories
inobs=${outdir}${obs}/agg/ 
inwrf=${outdir}${hist}/agg/
outwrf=${outdir}${hist}/bc/

# Make it (if not yet)
mkdir -p ${outwrf}

# Still go to temporary folder to work
cd ${tmpdir} ; test $? -eq 0 || echo "Error: check line "$LINENO

# Make sure no old files
rm -rf p_*.py
rm -rf r_*.Rscript
rm -rf s_*.script
rm -rf *.error
rm -rf *.out

# Count jobs (for all cases)
c=0

# ----------------------------------------------------------------------- #
# For historical simulation (only case for validation step)
# ----------------------------------------------------------------------- #

for i in $stause ; do
    for m in $month ; do

        c=$((c+1))
        cp ${currentdir}/${r01} r_${c}.Rscript

        # For historical period: like Quantile Mapping
cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J bc_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=36:00:00

cd $tmpdir
time Rscript --vanilla r_${c}.Rscript -o ${inobs}${i}_${m}.csv -m ${inwrf}${i}_${m}.csv -v ${outwrf}a2_${i}_${m}.csv
EOF
    # Don't do this due to limit of no. of submit jobs
    #sbatch s_${c}.script
    # 
    done
done

echo "You just submitted ${c} jobs, olala !"
# ----------------------------------------------------------------------- #
# How to train your dragon :)
# ----------------------------------------------------------------------- #
