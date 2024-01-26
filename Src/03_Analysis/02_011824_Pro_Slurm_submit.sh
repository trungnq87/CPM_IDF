#!/bin/bash

# Ok, you reach the limit of Slurm jobs on your server?
# You are lazy to run on multiple servers?
# Each job only lasts few minutes ?
# Here you are :)

# $1 for total jobs
# $2 for number of jobs to submit once
# $3 for "n" times you try :)
# Well, I will write "help" function later

total=$1
each=$2
try=$3

n=$(( try*each ))
j=$(( n - each + 1 )) 

for (( i=$j ; i<=$n ; i++ )) ; do

    sbatch s_${i}.script

    if [[ $i -ge $total ]] ; then
       break
    fi

done
