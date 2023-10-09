# ================================================================= #
#
# Update : Wed Aug  9 11:34:44 EDT 2023
#
# Every time, start with Setup.sh.
# This script just creates folders for your study.
#
# Although this is not recommended for HPC server
# with separate Data Center (you know, you will have 
# three layers of storage : home / personal work / shared project)
#
# I used to find a panacea for all kind of set-up.
# But I haven't found it, so far. Let's stay with this set up now.
# For the study of IDF curves.
#
# ================================================================= #
#
# What to MODIFY (or not)
#
workdir=`pwd`
#
# ================================================================= #
# What NOT to touch :
#
# Make "basic" directories
cd $workdir
mkdir -p Input    # All your input
mkdir -p Output   # All your output
mkdir -p Src      # All your source code
mkdir -p Tmp      # Temporary working files (e.g. submitted jobs)
                  # Basically, you can delete "Tmp" anytime, if needed 
#
# Make folders that you know you need for processing IDF curves
mkdir -p Src/00_Pre_Process
mkdir -p Src/01_Bias_Correction
mkdir -p Src/02_Generate_IDF
mkdir -p Src/03_Analysis
# Note: I try to keep each layer as simple as it can be !
#       e.g. no more than 03 tasks for each layer
#
echo "The folders that you have now :"
ls
ls Src/* 
#
# ================================================================= #
# Fin ! 
# ================================================================= #
