#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_081123_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Step 4 : Fix IDF curves of C-HPD data
# ----------------------------------------------------------------------- #
#
# Supported Python script
r04="R_04_Fix_IDF.Rscript"
currentdir=`pwd`

in04=${outdir}${obs}/idf/ 
out04=${outdir}${obs}/fix/ 

# To fixing
seasons="DJF MAM JJA SON"

# Make sure that we have output directory
mkdir -p ${out04}

# Now submit jobs to get all files in $outb4
cd ${tmpdir} ; test $? -eq 0 || echo "Error: check line "$LINENO

# Make sure no old files
rm -rf r_*.Rscript
rm -rf p_*.py # more clean
rm -rf s_*.script
rm -rf *.error
rm -rf *.out

# Count jobs (for all cases)
# One job for each station / each season
# =>still good with current speed on Carbonates
c=0

# ----------------------------------------------------------------------- #
# For C-HPD observation data (case 0)
# ----------------------------------------------------------------------- #

for s in $seasons ; do
    for i in $stause ; do

        # Count files
        c=$((c+1))

        # Copy src R script
        cp ${currentdir}/${r04} r_${c}.Rscript

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J fix_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=01:00:00

cd $tmpdir
echo ${i} ${s}
time Rscript --vanilla r_${c}.Rscript -i ${in04}${i}_${s}.csv -o ${out04}${i}_${s}.csv
EOF
        #
        sbatch s_${c}.script
        #
    done
done

echo "You just submitted ${c} jobs, olala !"
#
# Should follow my 5-mins rule
