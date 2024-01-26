# ============================================================= #
#
# Interpolation the WRF to station location
#
import argparse
import netCDF4 as nc
import pandas as pd
import numpy as np
import sys
#
# ============================================================= #
#
# This is fixed for current WRF output
starttime="-01-01 00:00:00"
wrffreq='3H' # 03 hourly WRF data
var="PRECIP"
ext=".nc"
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

    parser.add_argument("-m", "--month", nargs='+', help="Month to process, for submitting job", required=True)
    parser.add_argument("-st", "--stationnumber", help="Submitting job for each station", required=True, type=int)

    args = parser.parse_args()
    config = vars(args)
    
    out1=config['stationlist']
    out2=config['input']
    out3=config['output']
    out4=config['startyear']
    out5=config['endyear']

    out6=config['month']
    out7=config['stationnumber']

    return out1, out2, out3, out4, out5, out6, out7

#
# Read station info
#
def read_stationinfo(filename) :
    df=pd.read_csv(filename,header=0)
    sta=df.iloc[:,0].values
    lat=df.iloc[:,3].values
    lon=df.iloc[:,4].values
    return sta,lat,lon
#
# Read WRF output
#
def read_wrf(filename,year) :
    ds=nc.Dataset(filename)
    prcp=ds[var][:]
    wlat=ds['XLAT'][0,:,0]  # Just take the 1st time step
    wlon=ds['XLONG'][0,0,:] # And take 1D array
    wtime=ds['XTIME'][:]
    # 21 Feb 2023: should add argument of "starttime" and re-run 
    pdtime=pd.date_range(start=str(year)+str(starttime), periods=len(wtime), freq=str(wrffreq))
    del ds
    return prcp,wlat,wlon,pdtime
#
# Interpolation
#
def nearest(lat_1d, lon_1d, lat_in, lon_in):
    lat_index = np.nanargmin((lat_1d - lat_in)**2)
    lon_index = np.nanargmin((lon_1d - lon_in)**2)
    return lat_index,lon_index
#
# ============================================================= #
#
# Main
#

# Get arguments
stfl, indir, outdir, startyear, endyear, months, stajob = get_argument()

# Study periods
nyear=endyear-startyear+1

# Station info
sta,lat,lon=read_stationinfo(stfl)
#
# For each month
for m in np.arange(len(months)) :
    # For only one station (!!! for submitted job !!!)
    k=int(stajob)

    # Store all
    df_a=[]
    for y in np.arange(nyear) :
        year = startyear + y
        # WRF output
        fn=str(indir)+str(var)+'_'+str(year)+str(ext)
        prcp,wlat,wlon,pdtime=read_wrf(fn,year)
        # Interpolation
        i,j=nearest(wlat,wlon,lat[k],lon[k])
        # To data frame
        df=pd.DataFrame(prcp[:,j,i], columns=[str(sta[k])], index=pdtime) # Order of i,j or j,i pythonic mindset
        # Select only the month that you want 
        df_m=df[ df.index.month == int(months[m]) ]
        #
        df_a.append(df_m)
    #
    df_out = pd.concat(df_a)
    fl=str(outdir)+str(sta[k])+'_month_'+str(months[m])+'.csv'
    df_out.to_csv(fl)
    del df_out
#
# ============================================================= #
#
# Oi, con song que, con song que ...
#
# ============================================================= #
