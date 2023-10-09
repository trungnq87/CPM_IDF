# ============================================================= #
#
# Pre-processing C-HPD data
# For question: IDF curves for the central U.S. How future diff ?
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
# List of months (well, in case you don't want to pre-process all month)
months=[1,2,3,4,5,6,7,8,9,10,11,12]
# Missing value
missval=-9999
# Convert inches (in C-HPD) to mm
scale=25.4/float(100)
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
    parser.add_argument("-sk", "--skiprow", help="Number of rows to skip", type=int)
    parser.add_argument("-nr", "--numrow", help="Get only n next rows", type=int)
    
    args = parser.parse_args()
    config = vars(args)
    
    out1=config['stationlist']
    out2=config['input']
    out3=config['output']
    out4=config['startyear']
    out5=config['endyear']
    out6=config['skiprow']
    out7=config['numrow']

    return out1, out2, out3, out4, out5, out6, out7
#
# Read Station Info
#
def read_stationinfo(filename,sk,nr) :
    df=pd.read_csv(filename,header=0,skiprows=sk,nrows=nr)
    sta=df.iloc[:,1].values
    utc=df.iloc[:,9].values
    return sta,utc
#
# Read C-HPD data and re-format them
#
def read_stationdata(filename,utc_offset,startyear,endyear,staname,missvalue,selectmonth,scale) :
    # Using pandas
    df=pd.read_csv(filename, header=0)
    # Is this rushy or efficient ?
    gotcha=['DATE']
    for i in np.arange(24) :
        gotcha.append('HR'+str(i).zfill(2)+'Val')
    # Copy data from C-HPD file, with column names of HR01Val, HR02Val,...
    hr=df[np.array(gotcha)].copy()
    # Hourly column data to row data
    hr=pd.melt(hr, id_vars=['DATE'])
    hr=hr.rename(columns={'variable': 'hour'}) # Don't really need this line
    hr['hour']=hr['hour'].apply(lambda x: int(x.lstrip('HR').rstrip('Val')))
    #
    # readme.csv.txt told me that :
    # HR00Val    is the value on the first hour of the day (i.e., the precipitation
    #           total during the time of day 00:00-01:00; missing = -9999).
    #           The units are hundredths of inch.
    # => correct : UTC offset AND "ending time" to reasonable compare with WRF output (+1)
    #
    combined=hr.apply(lambda x: pd.to_datetime(x['DATE'], dayfirst=True) - timedelta(hours=int(x['hour'])+int(utc_offset)+1), axis=1)
    # 01 Jan 2023 : correct timedelta ( - not + )
    # as: 
    # UTC_Offset         is the number of hours the station's local time is offset
    #                    from GMT. Negative values are earlier than GMT.
    hr['DATE']=combined
    del hr['hour']
    hr=hr.sort_values(by='DATE')
    hr=hr.set_index('DATE')
    # Kind of duplicate later but well...
    hr=hr.replace(missvalue,np.nan)
    # Convert inches to mm
    hr *= scale
    # Do the same procedure to get "quality flag" (01 Nov 2022: slow but efficient enough)
    gotcha=['DATE']
    for i in np.arange(24) :
        gotcha.append('HR'+str(i).zfill(2)+'QF')
    qf=df[np.array(gotcha)].copy()
    qf=pd.melt(qf, id_vars=['DATE'])
    qf=qf.rename(columns={'variable': 'hour'})
    qf['hour']=qf['hour'].apply(lambda x: int(x.lstrip('HR').rstrip('QF')))
    combined_qf=qf.apply(lambda x: pd.to_datetime(x['DATE'], dayfirst=True) - timedelta(hours=int(x['hour'])+int(utc_offset)+1), axis=1)
    qf['DATE']=combined_qf
    del qf['hour']
    qf=qf.sort_values(by='DATE')
    qf=qf.set_index('DATE')
    qf.rename(columns={'value':'Quality flag'}, inplace=True)
    # Merge "quality flag" with data
    chpd = pd.concat([hr,qf], axis=1)
    del df
    # Select data only in your study period
    hr_c=chpd[ (chpd.index.year >= startyear) & (chpd.index.year <= endyear) ]
    hr_c.rename(columns={'value':str(staname)}, inplace=True)
    # 02 mins for python running with 01 station on Carbonates HPC (?)
    hr_c=hr_c.replace(missvalue,np.nan) # Doesn't meaning anymore, but, well...
    # Fill all missing date to get hourly frequency
    hr_h=hr_c.asfreq('H')
    # Select only the month that you want 
    hr_m=hr_h[ hr_h.index.month == selectmonth ]
    return hr_m
#
# ============================================================= #
#
# Main game (life is how you see it, right?)
#
# Read arguments to process
stalist, indir, outdir, startyear, endyear, skro, nrow = get_argument()

# Read station information
sta,utc=read_stationinfo(stalist,skro,nrow)

#
# Read data from each station and save to new "pre-processed" files
for i in np.arange(len(sta)) :
    fl=str(indir)+str(sta[i])+'.csv'
    # For each month
    for j in np.arange(len(months)) :
        df_c=read_stationdata(fl,utc[i],startyear,endyear,sta[i],missval,months[j],scale)
        # Save data frame to CSV file
        outfile=str(outdir)+str(sta[i])+'_month_'+str(months[j])+'.csv'
        df_c.to_csv(str(outfile))
        del df_c
#
# ============================================================= #
#
# C'est fin !
#
# ============================================================= #
