#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_${IDF_VERSION}_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Step 4 : Estimates IDF curves from WRF data
# ----------------------------------------------------------------------- #
#
# Supported Python script
r05="R_03_${IDF_VERSION}_IDF_gen.Rscript" # Same as r03 :)
currentdir=`pwd`

# A sub-folder
expname="IDF_WRF"
mkdir -p ${tmpdir}/${expname}

# I should write a LOOP later :)
# I/O directories
in05a=${outdir}${hist}/sms/
out05a=${outdir}${hist}/idf/ # a/b for hist/rcp85 !

in05b=${outdir}${rcp85}/sms/
out05b=${outdir}${rcp85}/idf/

in05c=${outdir}${rcp45}/sms/
out05c=${outdir}${rcp45}/idf/

# Make sure that we have output directory
mkdir -p ${out05a} ${out05b} ${out05c}

# To fitting
seasons="DJF MAM JJA SON" # Should be "similar" with seasons in $py04
frequency="20,50,100"
alpha="0.05" # To validate p-value of likelihood test
nboot=10000 # For resampling in bootstrap 
#minduration="180,360,540,720,900,1080,1260,1440,1620,1800,1980,2160,2340,2520,2700,2880,3060,3240,3420,3600,3780,3960,4140,4320"

# Should improve this later !
duration="X3h,X6h,X12h,X24h,X48h,X72h"
minduration="180,360,720,1440,2880,4320"

# Now submit jobs to get all files in $out05a & $out05b
cd ${tmpdir}/${expname} ; test $? -eq 0 || echo "Error: check line "$LINENO

# Make sure no old files
rm -rf r_*.Rscript
rm -rf s_*.script
rm -rf *.error
rm -rf *.out

# Count jobs (for all cases)
# One job for each station / each season 
# => still good with current speed on Carbonates
c=0

# ----------------------------------------------------------------------- #
# For historical simulation (case A)
# ----------------------------------------------------------------------- #

for s in $seasons ; do
    for i in $stause ; do

        # Count files
        c=$((c+1))

        # Copy src Rscript
        cp ${currentdir}/${r05} r_${c}.Rscript

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J wrfgev_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=10:00:00

cd ${tmpdir}/${expname}
time Rscript --vanilla r_${c}.Rscript -i ${in05a}${i}_${s}.csv -g ${out05a}/erl_${i}_${s}.csv -o ${out05a}${i}_${s}.csv -a $alpha -b $nboot -f $frequency -d $minduration -c $duration
EOF
        #
        #sbatch s_${c}.script
        #
    done
done

# ----------------------------------------------------------------------- #
# For future projection RCP 8.5 (case B)
# ----------------------------------------------------------------------- #

for s in $seasons ; do
    for i in $stause ; do

        # Count files
        c=$((c+1))

        # Copy src Rscript
        cp ${currentdir}/${r05} r_${c}.Rscript

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J wrfgev_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=10:00:00

cd ${tmpdir}/${expname}
time Rscript --vanilla r_${c}.Rscript -i ${in05b}${i}_${s}.csv -g ${out05b}/erl_${i}_${s}.csv -o ${out05b}${i}_${s}.csv -a $alpha -b $nboot -f $frequency -d $minduration -c $duration
EOF
        #
        #sbatch s_${c}.script
        #
    done
done

# ----------------------------------------------------------------------- #
# For future projection RCP 4.5 (case C)
# ----------------------------------------------------------------------- #

#echo "RCP 4.5 start $((c+1))"

for s in $seasons ; do
    for i in $stause ; do

        # Count files
        c=$((c+1))

        # Copy src Rscript
        cp ${currentdir}/${r05} r_${c}.Rscript

cat <<EOF >> s_${c}.script
#!/bin/bash
#SBATCH -A r00199
#SBATCH -J wrfgev_${c}
#SBATCH -o %j.out
#SBATCH -e %j.error
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=10:00:00

cd ${tmpdir}/${expname}
time Rscript --vanilla r_${c}.Rscript -i ${in05c}${i}_${s}.csv -g ${out05c}/erl_${i}_${s}.csv -o ${out05c}${i}_${s}.csv -a $alpha -b $nboot -f $frequency -d $minduration -c $duration
EOF
        #
        #sbatch s_${c}.script
        #
    done
done

echo "You just submitted ${c} jobs, olala !"
#
# Should follow my 5-mins rule
