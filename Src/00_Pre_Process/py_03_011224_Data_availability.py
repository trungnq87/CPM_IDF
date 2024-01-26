# ============================================================= #
#
# Step 03: Check data availability: simple is the best ?
#           I don't want to miss a thing ...
#
# ============================================================= #
#
# Import as usual
import argparse
import matplotlib as mpl
mpl.use('Agg')
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
#
# ============================================================= #
#
# Parameters or unchanged inputs
#
# Seasons
seasons=['DJF','MAM','JJA','SON']
months=[[12,1,2],[3,4,5],[6,7,8],[9,10,11]]
# For plotting
buff=-0.75
mycmap = plt.cm.rainbow
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

    parser.add_argument("-bf", "--boundsfull", nargs='+', help="Full color scale to plot", required=True)
    parser.add_argument("-ba", "--boundsallow", nargs='+', help="Prefer color scale to plot", required=True)
    
    parser.add_argument("-du", "--duration", help="Duration for checking (e.g., 72h)", type=int)
    parser.add_argument("-th", "--threshold", help="Threshold of data availability", type=int)

    args = parser.parse_args()
    config = vars(args)
    
    out1=config['stationlist']
    out2=config['input']
    out3=config['output']
    out4=config['startyear']
    out5=config['endyear']

    out6=config['boundsfull']
    out7=config['boundsallow']

    out8=config['duration']
    out9=config['threshold']

    return out1, out2, out3, out4, out5, out6, out7, out8, out9

#
def read_stationinfo(filename) :
    df=pd.read_csv(filename,header=0)
    sta=df.iloc[:,1].values
    lat=df.iloc[:,2].values
    lon=df.iloc[:,3].values
    return sta,lat,lon
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
def anothermap(myvals,la,lo,la_all,lo_all,buff,mycmap,mynorm,mytitle,myfigure,iflayout) :
    #
    fig = plt.figure()
    ax = fig.add_subplot(111)
    #
    map = Basemap(projection='cyl',llcrnrlon=np.nanmin(lo+buff),llcrnrlat=np.nanmin(la+buff),urcrnrlon=np.nanmax(lo-buff),urcrnrlat=np.nanmax(la-buff),resolution='h')
    #
    parallels = np.arange(-90,90,5.)
    meridians = np.arange(-180,180,5.)
    map.drawparallels(parallels,labels=[1,0,0,0],fontsize=18,color="grey")
    map.drawmeridians(meridians,labels=[0,0,0,1],fontsize=18,color="grey")
    map.drawstates()
    map.drawcoastlines()
    map.drawrivers(color='blue')
    # If you want to show non-selected stations as grey triangle symbols
    if iflayout :
        cs_a=plt.scatter(lo_all, la_all, c='grey', marker='^', alpha=0.2)
        cs=plt.scatter(lo, la, c=myvals, s=55, marker='o', cmap=mycmap, norm=mynorm)
    else :
        cs=plt.scatter(lo, la, c=myvals, s=50, marker='o', cmap=mycmap, norm=mynorm)
    cb=map.colorbar(cs,"right", size="5%", pad="2%")
    #
    plt.title(mytitle)
    plt.savefig(myfigure, dpi=300)
    plt.close()
#
# ============================================================= #
#
# Main game (life is how you see it, right?)
#

# Get arguments
stalist, indir, outdir, startyear, endyear, boundsfull, boundsallow, checkduration, allow = get_argument()

temp = [float(i) for i in boundsfull]
normfull = mpl.colors.BoundaryNorm(temp, mycmap.N)

temp = [float(i) for i in boundsallow]
normallow = mpl.colors.BoundaryNorm(temp, mycmap.N)

# Read station information
sta,lat,lon=read_stationinfo(stalist)

# I wanna check availability for all seasons
df_sea=[]

# Do it for each season
for s in np.arange(len(seasons)) :
    # To store what to plot
    ratio = []
    # Read data from each station and get data availability info
    for i in np.arange(len(sta)) :
        # A season can be three-months or five-month-rainy-season
        df_a = []
        for m in np.arange(len(months[s])) :
            fl=str(indir)+str(sta[i])+'_month_'+str(months[s][m])+'.csv'
            tmp=read_stationdata(fl,startyear,endyear,sta[i],months[s][m])
            df_a.append(tmp)
        df_o = pd.concat(df_a,axis=0)
 
        # This counting is not useful, right?
        #per = 100*df_o[str(sta[i])].count()/len(df_o[str(sta[i])])

        # So far : by default "rolling" looks for n-1 prior rows of data 
        # to aggregate, where n is the window size.
        # If that condition is not met, it will return NaN for the window.
        # If you would like to avoid returning NaN, you could pass min_periods=1 
        # to the method which reduces the minimum required 
        # number of valid observations in the window to 1 

        # Running sum
        df_r=df_o.rolling(int(checkduration)).sum() # Think about min_periods OR fillna here !
        # Get annual maximum
        df_max=df_r.groupby(df_r.index.year).max()

        # Now percentage
        per = 100*df_max[str(sta[i])].count()/len(df_max[str(sta[i])])

        # Save it for plotting
        ratio.append(per)

    # Well, put it to dataframe
    df_ratio = pd.DataFrame(ratio, columns=[str(seasons[s])], index=sta) 
    df_sea.append(df_ratio)

    # How many stations ?
    tit = sum(i > allow for i in ratio)

    # Now, plot it :)
    myt='Percentage of non-NaN data in '+str(seasons[s])+' ('+str(tit)+'/'+str(len(ratio))+')'
    myf=str(outdir)+'DA_'+str(seasons[s])+".png"
    anothermap(ratio,lat,lon,lat,lon,buff,mycmap,normfull,myt,myf,False)

# Get it all (> allow %)
df_all = pd.concat(df_sea,axis=1)
df_use = df_all[df_all > allow].dropna()

# Get lat/lon
data = { 'Lat' : lat, 'Lon' : lon}
df_sta = pd.DataFrame(data, index=sta) 

# Combine
df_plot=df_sta.combine_first(df_use).dropna()
la=df_plot['Lat'].values
lo=df_plot['Lon'].values
rat=df_use.min(axis=1)

# Now plot
myt='Stations with >'+str(allow)+'% data for all seasons ('+str(len(rat))+'/'+str(len(ratio))+')'
myf=str(outdir)+'DA_'+str(allow)+'.png'
anothermap(rat,la,lo,lat,lon,buff,mycmap,normallow,myt,myf,True)

# Save to CSV file
df_plot.to_csv(str(indir)+'Stations_list.csv')
#
# ============================================================= #
#
# C'est fin !
#
# ============================================================= #
