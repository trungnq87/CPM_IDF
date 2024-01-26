# To make the table of the list of 74 stations in the Supplements
latextable="../../Output/PNG/Table_S1_List74stations.txt"
# Start
#echo "\begin{table*}[ht]" > $latextable # This cleans everything :)
#echo "\begin{center}" >> $latextable

# Hum, we need a "longtable"
echo "\clearpage" > $latextable
echo "\onecolumn" >> $latextable

echo "\begin{longtable}[h!]{ ccccccc }" >> $latextable
echo "\caption{List of 74 selected stations}" >> $latextable

# This command
#head -n 1 ../../Input/CHPD/HPD_v02r02_stationinv_c20221129.csv
# give you the idea of column names
#StnID,Lat,Lon,Elev,State/Province,Name,WMO_ID,Sample_Interval (min),UTC_Offset,POR_Date_Range,PCT_POR_Good,Last_Half_POR,PCT_Last_Half_Good,Last_Qtr_POR,PCT_Last_Qtr_Good

#echo "\begin{tabular}{ c c c c c c c c c c }" >> $latextable
echo "\\\\" >> $latextable 
echo "\hline" >> $latextable

#echo "\textbf{No.} & \textbf{Station ID} & \textbf{Latitude} & \textbf{Longitude} & \textbf{Elevation} & \textbf{State} & \textbf{Name} & \textbf{Period of record} \\\\" >> $latextable
echo "\textbf{No.} & \textbf{Station ID} & \textbf{Latitude} & \textbf{Longitude} & \textbf{Elevation} & \textbf{State} & \textbf{Name} \\\\" >> $latextable
echo "\hline" >> $latextable

# Now the content
c=0
for i in `cat ../../Output/CHPD/pre/Stations_list.csv | awk -F',' '{print $1}'`
do
    c=$((c+1))
    j=`grep $i ../../Input/CHPD/HPD_v02r02_stationinv_c20221129.csv`

    staid=`echo $j | awk -F',' '{print $1}'`
    lat=`echo $j | awk -F',' '{print $2}'`
    lon=`echo $j | awk -F',' '{print $3}'`
    elev=`echo $j | awk -F',' '{print $4}'`

    state=`echo $j | awk -F',' '{print $5}'`
    name=`echo $j | awk -F',' '{print $6}' | sed 's/&/and/'`

    #por=`echo $j | awk -F',' '{print $10}'`

    #echo "$c & $staid & $lat & $lon & $elev & $state & $name & $por \\\\" >> $latextable
    echo "$c & $staid & $lat & $lon & $elev & $state & $name \\\\" >> $latextable
done

# Ending the table like a boss :)
echo "\hline" >> $latextable
#echo "\end{tabular}" >> $latextable
echo "\label{tablelistof74stations}" >> $latextable
#echo "\caption{List of 74 selected stations}" >> $latextable
#echo "\end{center}" >> $latextable
#echo "\end{table*}" >> $latextable
echo "\end{longtable}" >> $latextable
echo "\clearpage" >> $latextable
