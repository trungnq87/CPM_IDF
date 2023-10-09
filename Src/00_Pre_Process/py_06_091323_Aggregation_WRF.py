# ============================================================= #
#
# Step 6:  Aggregation of WRF outputs to
#          different durations (e.g. 3h, 6h, 9h, ...)
#
# Question: IDF curves for the central U.S. how future diff ?
# Wanna discuss: trqnguye@iu.edu
#
# ============================================================= #
#
# Import as usual
import argparse
import numpy as np
import pandas as pd
import sys
from datetime import datetime, timedelta
#
# ============================================================= #
#
# Parameters or unchanged inputs
#
# Seasons
seasons=['1','2','3','4','5','6','7','8','9','10','11','12']
months=[[1],[2],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12]]
#
# ============================================================= #
#
# User-defined functions (well, me-defined functions)
#

# Get arguments
#
def get_argument() :
    parser = argparse.ArgumentParser(description="Get arguments for selecting stations from C-HPD",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # Using these options indeed 
    parser.add_argument("-sl", "--stationlist", help="List of stations")
    parser.add_argument("-i", "--input", help="Location of input files")
    parser.add_argument("-o", "--output", help="Location of output files")
    parser.add_argument("-sy", "--startyear", help="Start year of study period", type=int)
    parser.add_argument("-ey", "--endyear", help="Start year of study period", type=int)

    parser.add_argument("-st", "--stationnumber", help="Submitting job for each station", required=True, type=int)
    parser.add_argument("-fh", "--firsthour", help="First hour to aggregate", required=True, type=int)
    parser.add_argument("-iv", "--interval", help="Intervals between durations", required=True, type=int)
    parser.add_argument("-nd", "--numberduration", help="Number of durations for aggregating", type=int)

    args = parser.parse_args()
    config = vars(args)
    
    out1=config['stationlist']
    out2=config['input']
    out3=config['output']
    out4=config['startyear']
    out5=config['endyear']

    out6=config['stationnumber']
    out7=config['firsthour']
    out8=config['interval']
    out9=config['numberduration']

    return out1, out2, out3, out4, out5, out6, out7, out8, out9

# Read station info
#
def read_stationinfo(filename) :
    df=pd.read_csv(filename,header=0)
    sta=df.iloc[:,0].values
    return sta
#
# Read WRF output
#
def read_stationdata(filename,timefile) :

    # Get timestamp from "original interpolated" WRF output
    timedf=pd.read_csv(timefile, header=0, index_col=0)

    # For CDFt
    df=pd.read_csv(filename, header=0)

    # Set time index 
    df=df.set_index(pd.to_datetime(timedf.index))

    return df
#
# Aggregation of WRF output
#
def aggregation(df,staname,fh,inter,nduration) :

    df_all=[]
    for i in np.arange(nduration) :
        j=fh+inter*i
        # Running sum
        df_r=df.rolling(int(j)).sum() # Think about min_periods OR fillna here !
        # Get annual maximum
        #df_max=df_r.groupby(df_r.index.year).max()
        #df_r=df_r.rename(columns={'x':str(j*3)+'h'})
        df_r=df_r.rename(columns={str(staname):str(j*3)+'h'})
        # Append it to concat later
        df_all.append(df_r)
        # For sure
        del df_r
        #del df_max
    df_out = pd.concat(df_all,axis=1)

    # Change the name of index column to 'Year'
    df_out.index.name='Time'

    return df_out
#
# ============================================================= #
#
# Main game (life is how you see it, right?)
#

# Get arguments
stalist, indir, outdir, startyear, endyear, stajob, firsthour, interval, ndura = get_argument()

# Read station information
sta=read_stationinfo(stalist)
#
# Do it for each season
#
for s in np.arange(len(seasons)) :

    # For only one station (!!! for submitted job !!!)
    # A season can be three-months or five-month-rainy-season
    df_a = []
    for m in np.arange(len(months[s])) :
        fl=str(indir)+str(sta[stajob])+'_month_'+str(months[s][m])+'.csv'
        #timefl=str(indir_time)+str(sta[stajob])+'_month_'+str(months[s][m])+'.csv'

        #tmp=read_stationdata(fl,timefl)
        tmp=read_stationdata(fl,fl) # <= oops, I just overnight, so ...
        df_a.append(tmp)

    # This is dataframe for all months in a season
    df_o = pd.concat(df_a,axis=0)

    # Aggregate data
    df_c=aggregation(df_o,sta[stajob],firsthour,interval,ndura)
 
    # Save data frame to CSV file
    outfile=str(outdir)+str(sta[stajob])+'_'+str(seasons[s])+'.csv'
    df_c.to_csv(str(outfile))
    del df_c
#
# ============================================================= #
#
# C'est fin !
#
# ============================================================= #
