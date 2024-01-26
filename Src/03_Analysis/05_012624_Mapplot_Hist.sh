#!/bin/bash
#
# Firstly, load common variables
#
. ../AA_${IDF_VERSION}_Common_Variables.sh ; test $? -eq 0 || echo "Error: check line "$LINENO
#
# ----------------------------------------------------------------------- #
# Keeping analysis step here
# ----------------------------------------------------------------------- #
#
# Supported Python script
currentdir=`pwd`

py01="py_05_012624_Mapplot_Hist.py"

# I/O directories
in01obs=${outdir}${obs}/idf/ 
in01hist=${outdir}${hist}/idf/
in01rcp85=${outdir}${rcp85}/idf/
in01rcp45=${outdir}${rcp45}/idf/

# ===== Boxplot WRF-hist vs C-HPD ===== #

outnow="Mapplot_Relative_Errors"
mkdir -p ${pngdir}/${outnow}

time python ${py01} -sl ${stationlist} -o ${pngdir}/${outnow}/ -a ${in01obs} -b ${in01hist} -na C-HPD -nb Hist-WRF

#
# Should follow my 5-mins rule
