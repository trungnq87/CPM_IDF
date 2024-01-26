# ================================================================= #
#
# Update : Wed Jan 10 10:46:58 EST 2024
#
# Every time, start with . ./Setup.sh.
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
workdir=`pwd`    # Your working directory
version='011224' # Version of codes
dev=false        # true # If you are in development step (not recommend)
#
# ================================================================= #
#
# What NOT to touch :
#
# Make "basic" directories
cd $workdir
mkdir -p Input    # All your input
mkdir -p Output   # All your output
mkdir -p Tmp      # Temporary working files (e.g. submitted jobs)
                  # Basically, you can delete "Tmp" anytime, if needed 
#
# Make folders that you know you need for processing IDF curves
# For Github version, this should be replaced by tar -xzvf Src.tar.gz
#
if [ "$dev" = true ] ; then 
    mkdir -p Src      # All your source code
    mkdir -p Src/00_Pre_Process
    mkdir -p Src/01_Bias_Correction
    mkdir -p Src/02_Generate_IDF
    mkdir -p Src/03_Analysis
fi
#
# Note: I try to keep each layer as simple as it can be !
#       e.g. no more than 03 tasks for each layer
#
echo "The folders that you have now :"
ls
ls Src/*
#
# Occam's razor :) Check the version that you are working on.
#
export IDF_VERSION=$version
#
if [[ -n "$IDF_VERSION" ]]; then
    echo "You are using the CPM_IDF version : $IDF_VERSION"
else
    echo "You should export IDF_VERSION :) or things will mess up."
fi
#
# Fix your working directory
#
export wrkdir=${workdir}/ # Remember / or no need ?
echo "Your working directory is : $wrkdir (!)"
#
# ================================================================= #
#
# Fin ! 
#
# ================================================================= #
