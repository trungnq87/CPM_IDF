#!/bin/bash
#
# ----------------------------------------------------------------------- #
# Bias correction of WRF output
# ----------------------------------------------------------------------- #
#
# Firstly, load common variables
#
. ../AA_${IDF_VERSION}_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO

# Your experiments
explist=( "WRF_hi" "WRF_85" "WRF_45" )
method=( "QM" "CDFt" "CDFt" )

# We have input files here
inobs=${outdir}/${obs}/agg/ 
inhist=${outdir}/${hist}/agg/ 

# Supported Python script
r01="R_01_${IDF_VERSION}_BiasCorr_WRF.Rscript"
currentdir=`pwd`

cc=0
# Loop for all experiments
for j in "${!explist[@]}"; do

    # Now submit jobs
    mkdir -p ${tmpdir}/bc_${explist[j]}
    cd ${tmpdir}/bc_${explist[j]} ; test $? -eq 0 || echo "Error: check line "$LINENO

    # Make sure no old files
    rm -rf r_*.Rscript
    rm -rf s_*.script
    rm -rf *.error
    rm -rf *.out

    # Data location
    in01=${outdir}/${explist[j]}/agg/ 
    out01=${outdir}/${explist[j]}/bc/

    # Make sure that we have output directory
    mkdir -p ${out01}

    # One job for each station / each season
    # => still good with current speed on Carbonates
    c=0
    for i in $stause ; do
        for m in $month ; do

            # Count files
            c=$((c+1))

            # Copy Rscript
            cp ${currentdir}/${r01} r_${c}.Rscript

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J ${explist[j]}_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=01:00:00

cd ${tmpdir}/bc_${explist[j]}
time Rscript --vanilla r_${c}.Rscript -o ${inobs}${i}_${m}.csv -s ${inhist}${i}_${m}.csv -p ${in01}${i}_${m}.csv -b ${out01}${i}_${m}.csv -v ${out01}stat_${i}_${m}.csv -t ${method[j]}
EOF
        #
        #sbatch s_${c}.script
        #
        done
    done

cc=$((cc+c))
#
done
#
echo "You just submitted ${cc} jobs, olala !"
#
# ----------------------------------------------------------------------- #
# How to train your dragon :)
# ----------------------------------------------------------------------- #
