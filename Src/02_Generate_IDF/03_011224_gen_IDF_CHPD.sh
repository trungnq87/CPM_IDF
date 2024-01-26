#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_${IDF_VERSION}_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Step 3 : Estimates IDF curves for C-HPD data
# ----------------------------------------------------------------------- #
#
# Supported Python script
r03="R_03_${IDF_VERSION}_IDF_gen.Rscript"
currentdir=`pwd`

# A sub-folder
expname="IDF_CHPD"
mkdir -p ${tmpdir}/${expname}

in03=${outdir}${obs}/sms/ 
out03=${outdir}${obs}/idf/ 

# To fitting
seasons="DJF MAM JJA SON" # Should be "similar" with seasons in $py04
frequency="20,50,100"
alpha="0.05" # To validate p-value of likelihood test
nboot=10000 # For resampling in bootstrap 
#minduration="180,360,540,720,900,1080,1260,1440,1620,1800,1980,2160,2340,2520,2700,2880,3060,3240,3420,3600,3780,3960,4140,4320"

# Should improve this later !
duration="X3h,X6h,X12h,X24h,X48h,X72h"
minduration="180,360,720,1440,2880,4320"

# Make sure that we have output directory
mkdir -p ${out03}

# Now submit jobs to get all files in $outb4
cd ${tmpdir}/${expname} ; test $? -eq 0 || echo "Error: check line "$LINENO

# Make sure no old files
rm -rf r_*.Rscript
rm -rf s_*.script
rm -rf *.error
rm -rf *.out

# One job for each station / each season
# => still good with current speed on Carbonates
c=0
for s in $seasons ; do
    for i in $stause ; do

        # Count files
        c=$((c+1))

        # Get first 12 lines of Rscript
        cp ${currentdir}/${r03} r_${c}.Rscript

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J gev_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=10:00:00

cd ${tmpdir}/${expname}
time Rscript --vanilla r_${c}.Rscript -i ${in03}${i}_${s}.csv -g ${out03}/erl_${i}_${s}.csv -o ${out03}${i}_${s}.csv -a $alpha -b $nboot -f $frequency -d $minduration -c $duration
EOF
        #
        #sbatch s_${c}.script
        #
    done
done
#
echo "You just submitted ${c} jobs, olala !"
#
# Should follow my 5-mins rule
