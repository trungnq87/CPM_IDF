#!/bin/bash
#
# Step 00 : set environments and common variables for "all" steps
#
# ----------------------------------------------------------------------- #
# AA - Path to directories
# ----------------------------------------------------------------------- #
#
# Working directory (the only thing that you might need to change)
wrkdir="/N/project/pfec_climo/trqnguye/14_09Aug2023_IDF/"
# In/Out directory
indir=${wrkdir}Input/
outdir=${wrkdir}Output/
# Temporary directory (where you create and submit jobs)
tmpdir=${wrkdir}Tmp/
# Store all figures
pngdir=${outdir}PNG/
# Code directory (each step inside)
srcdir=${wrkdir}Src/

# Cases for outputs
obs="CHPD"
hist="WRF_hi"
rcp85="WRF_85"

# Study domain and period
states="IL IN OH KY"
startyear=1980
endyear=2022

# Future projection
startrcp=2058
endrcp=2100

#
# ----------------------------------------------------------------------- #
# BB - Set-up for C-HPD data
# ----------------------------------------------------------------------- #
# 

# 01. For downloading C-HPD data
chpdinput=${indir}CHPD
chpdlink="https://www.ncei.noaa.gov/data/coop-hourly-precipitation/v2"
chpdacce=${chpdlink}/access/
chpdvers="HPD_v02r02_stationinv_c20221129.csv" # <=== CHANGE THE VERSION !!!
chpdinfo=${chpdlink}/station-inventory/${chpdvers}
out01="HPD_v02r02_States.csv" # Select stations in your study domain

# 02. For re-formatting C-HPD data
a=`wc -l ${chpdinput}/${out01} | awk '{print $1}'`
nline=$((a-1))   # Number of stations of C-HPD data
ptask=1          # Number of stations to process for each task

# 03. Check data availability and get list of selected stations
stationlist=${outdir}${obs}/pre/Stations_list.csv

# 04. For aggregating data (use for both C-HPD and WRF Interpolation)
a=`wc -l $stationlist | awk '{print $1}'`
nsta=$((a-1))  # Number of stations that will be analyzed

#
# ----------------------------------------------------------------------- #
# CC - Work with WRF output
# ----------------------------------------------------------------------- #
# 

# 01. WRF interpolation (diff for Hist and RCP85)
# For submitting job for each month (it's faster!)
month="1 2 3 4 5 6 7 8 9 10 11 12"

# 02. Use in bias correction step
stause=`cat $stationlist | awk -F',' '{print $1}'`

# 
# ----------------------------------------------------------------------- #
# DD - I hope that you don't need to touch lines below
# ----------------------------------------------------------------------- #
# 
# All the IO directories (keep here for clear vision)
#
# For C-HPD
mkdir -p ${pngdir} 
mkdir -p ${chpdinput} # Where you downloaded the C-HPD data
mkdir -p ${outdir}${obs} 
# For WRF
mkdir -p ${indir}${hist} 
mkdir -p ${outdir}${hist} 
mkdir -p ${indir}${rcp85} 
mkdir -p ${outdir}${rcp85} 

#
# ----------------------------------------------------------------------- #
# Appendix - Linking WRF outputs from Lauer (2023)
# ----------------------------------------------------------------------- #
# 
# Link it as you wish
linkfile=false  # true
# Link the WRF output files
if $linkfile; then
# Historical simulations
cd ${indir}${hist}
for (( y=1980 ; y<=2005 ; y++ )) ; do
    ln -s /N/project/pfec_climo/BASELINE/PRECIP/PRECIP_${y}.nc .
done
for (( y=2006 ; y<=2022 ; y++ )) ; do
    ln -s /N/project/pfec_climo/RCP8.5/PRECIP/PRECIP_${y}.nc .
done
# Future projection RCP 8.5
cd ${indir}${rcp85}
for (( y=2023 ; y<=2100 ; y++ )) ; do
    ln -s /N/project/pfec_climo/RCP8.5/PRECIP/PRECIP_${y}.nc .
done
cd ${wrkdir} 
# Already linked
else
   echo "The WRF outputs are already linked."
fi
#
# ----------------------------------------------------------------------- #
# Should follow my 5-mins rule ! 
# ----------------------------------------------------------------------- #
