#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_081123_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Keeping analysis step here
# ----------------------------------------------------------------------- #
#
# Supported Python script
currentdir=`pwd`
py01="py_01_100323_Analysis_01.py"

# I/O directories
in01obs=${outdir}${obs}/idf/ 
in01hist=${outdir}${hist}/idf/
in01rcp=${outdir}${rcp85}/idf/

# Plot IDF curves at one station nearest to Bloomington, IN
# Found issue with isotonic regression => move to quantile selection algorithm
#
#time python ${py01} -sl ${stationlist} -o ${pngdir} -a ${in01obs} -b ${in01rcp} -na C-HPD -nb RCP85
#time python ${py01} -sl ${stationlist} -o ${pngdir} -a ${in01obs} -b ${in01hist} -na C-HPD -nb Hist-WRF

# Keep looking change factors

#
# Should follow my 5-mins rule
