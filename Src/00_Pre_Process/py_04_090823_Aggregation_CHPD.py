# ============================================================= #
#
# Step 04: Aggregation of C-HPD series to ALL Durations 
#         (e.g. 3h, 6h, 9h, ...)
#
# Question: IDF curves for the Midwest U.S. how future diff ?
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
# Seasons (Look a noob declares variables!)
seasons=['1','2','3','4','5','6','7','8','9','10','11','12']
months=[[1],[2],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12]]
#
# To write output corresponding to current output frequency of WRF
wrffreq=int(3)
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

    parser.add_argument("-fh", "--firsthour", help="First hour to aggregate", required=True, type=int)
    parser.add_argument("-iv", "--interval", help="Intervals between durations", required=True, type=int)
    parser.add_argument("-nd", "--numberduration", help="Number of durations for aggregating", type=int)

    parser.add_argument("-sk", "--skiprow", help="Number of row to skip (in station list file)", type=int)
    parser.add_argument("-nr", "--numberofrow", help="Number of row to process (in station list file)", type=int)

    args = parser.parse_args()
    config = vars(args)
    
    out1=config['stationlist']
    out2=config['input']
    out3=config['output']
    out4=config['startyear']
    out5=config['endyear']

    out6=config['firsthour']
    out7=config['interval']
    out8=config['numberduration']

    out9=config['skiprow']
    out10=config['numberofrow']

    return out1, out2, out3, out4, out5, out6, out7, out8, out9, out10

#
def read_stationinfo(filename,sk,nr) :
    df=pd.read_csv(filename,header=0,skiprows=sk,nrows=nr)
    sta=df.iloc[:,0].values
    return sta
#
def read_stationdata(filename,startyear,endyear,staname,mon) :

    # Get full timestamp
    starttime=str(startyear).strip()+'-01-01'
    endtime=str(endyear).strip()+'-12-31 23:00:00'
    # Is it better ? endtime=str(endyear+1).strip()+'-01-01'
    d = pd.date_range(starttime,endtime,freq='H')
    d = d[d.month == mon]
   
    # Don't use index_col=0
    df=pd.read_csv(filename, header=0)
    df['DATE']=pd.to_datetime(df['DATE'])
    df=df.set_index('DATE')

    # Select only qualified data
    df=df[df['Quality flag'] == ' '] 

    # Set full time index
    df=df.reindex(d)
    return df
#
def aggregation(df,staname,fh,inter,nduration) :

    df_all=[]
    for i in np.arange(nduration) :
        j=fh+inter*i
        # Running sum
        df_r=df.rolling(int(j)).sum() # Think about min_periods OR fillna here !
        # Get annual maximum
 #       df_max=df_r.groupby(df_r.index.year).max()
        df_r=df_r.rename(columns={str(staname):str(j)+'h'})
        # Append it to concat later
        df_all.append(df_r)
        # For sure
        del df_r
 #       del df_max
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
stalist, indir, outdir, startyear, endyear, firsthour, interval, ndura, skro, nrow = get_argument()

# Read station information
sta=read_stationinfo(stalist,skro,nrow)

# Do it for each season
for s in np.arange(len(seasons)) :

    # Read data from each station
    for i in np.arange(len(sta)) :
        # A season can be three-months or five-month-rainy-season
        df_a = []
        for m in np.arange(len(months[s])) :
            fl=str(indir)+str(sta[i])+'_month_'+str(months[s][m])+'.csv'
            tmp=read_stationdata(fl,startyear,endyear,sta[i],months[s][m])
            df_a.append(tmp)

        # This is dataframe for all months in a season
        df_o = pd.concat(df_a,axis=0)

        # Aggregate data
        df_c=aggregation(df_o,sta[i],firsthour,interval,ndura)
 
        # Save data frame to CSV file
        outfile=str(outdir)+str(sta[i])+'_'+str(seasons[s])+'.csv'

        # Oh, yes ! The current WRF output is 3-hourly
        df_c[::wrffreq].to_csv(str(outfile))
        del df_c
#
# ============================================================= #
#
# C'est fin !
#
# ============================================================= #
