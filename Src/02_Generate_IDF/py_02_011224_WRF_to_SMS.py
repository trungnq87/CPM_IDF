# ============================================================= #
#
# Step 2 : Aggregation of WRF outputs to Seasonal Maximum Series 
#          at different durations (e.g. 3h, 6h, 9h, ...)
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
seasons=['DJF','MAM','JJA','SON']
months=[[12,1,2],[3,4,5],[6,7,8],[9,10,11]]
#
# ============================================================= #
#
# User-defined functions (well, me-defined functions)
#

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

    parser.add_argument("-j", "--stationjob", help="Submit job for each station", type=int)

    args = parser.parse_args()
    config = vars(args)
    
    out1=config['input']
    out2=config['output']
    out3=config['stationjob']

    out4=config['startyear']
    out5=config['endyear']
    out6=config['stationlist']

    return out1, out2, out3, out4, out5, out6 

#
# Read station info
#
def read_stationinfo(filename) :
    df=pd.read_csv(filename,header=0)
    sta=df.iloc[:,0].values
    return sta
#
# Read WRF output
#
def read_stationdata(filename) :

    # Read data
    df=pd.read_csv(filename, header=0)

    # Set time index 
    df=df.set_index(pd.to_datetime(df['Time']))

    # No need 'Time' column
    del df['Time']

    return df
#
# Aggregation of WRF output
#
def annualmaximum(df,firstyear,lastyear) :

    # Get only your study period
    df_s=df[(df.index.year >= firstyear) & (df.index.year <= lastyear)]

    # Get annual maximum
    df_out=df_s.groupby(df_s.index.year).max()

    # Change the name of index column to 'Year'
    df_out.index.name='Year'

    return df_out
#
# ============================================================= #
#
# Main game (life is how you see it, right?)
#

# Get arguments
indir, outdir, stajob, startyear, endyear, stalist = get_argument()

#
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
        fl=str(indir)+str(sta[stajob])+'_'+str(months[s][m])+'.csv'

        tmp=read_stationdata(fl)
        df_a.append(tmp)

    # This is dataframe for all months in a season
    df_o = pd.concat(df_a,axis=0)

    # Aggregate data
    df_c=annualmaximum(df_o,startyear,endyear)
 
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
