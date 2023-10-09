# ============================================================= #
#
# Step 01 : I am thinking about a map of "change factor"
#           at least for three durations (3h, 24h and 72h)
#           What about look at IDF curves 
#           for one "random" station first ?
# Wanna discuss: trqnguye@iu.edu
#
# ============================================================= #
#
import argparse
import matplotlib as mpl
mpl.use('Agg')
#
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
from math import cos, asin, sqrt
from mpl_toolkits.basemap import Basemap
#
# ============================================================= #
#
seasons=["DJF","MAM","JJA","SON"]
duration=[3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60,63,66,69,72]
frequency=[20,50,100]
freqname=['20-yr','50-yr','100-yr']
freqstyle=['dashdot','dashed','solid']
mcolors=['g','b','r']

# For plotting
buff=-0.75
mycmap = plt.cm.rainbow
bounds = np.arange(0,100,10) 
mynorm = mpl.colors.BoundaryNorm(bounds, mycmap.N)

# Bloomington location
in_lat = 39.17185
in_lon = -86.52214

# Some options for playing with data
ifreadallstation=False
ifreadonestation=True
#
# ============================================================= #
#
# Get arguments
def get_argument() :
    parser = argparse.ArgumentParser(description="Get arguments for analyzing IDF curves",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # Using these options indeed 
    parser.add_argument("-sl", "--stationlist", help="List of stations")
    parser.add_argument("-o", "--output", help="Location of output files")

    parser.add_argument("-a", "--inputcaseA", help="Location of input files of case A")
    parser.add_argument("-b", "--inputcaseB", help="Location of input files of case B")

    parser.add_argument("-na", "--nameinputA", help="Experiment name of case A")
    parser.add_argument("-nb", "--nameinputB", help="Experiment name of case B")

    args = parser.parse_args()
    config = vars(args)
    
    out1=config['stationlist']
    out2=config['output']

    out3=config['nameinputA']
    out4=config['nameinputB']

    out5=config['inputcaseA']
    out6=config['inputcaseB']

    return out1, out2, out3, out4, out5, out6

# Read information of selected stations
def read_stationinfo(filename) :
    df=pd.read_csv(filename,header=0)
    sta=df.iloc[:,0].values

    lat=df['Lat'].values
    lon=df['Lon'].values

    # Oh, now I put out all df to play later
    # return sta, lat, lon, df
    return sta, lat, lon

# Read IDF outputs
def read_output(filename) :
    dat = pd.read_csv(filename, header=0, index_col=0)
    outdat = np.array(dat.values).T
    return outdat

# Plot on map
def mapplot(myvals,la,lo,buff,mycmap,mynorm,mytitle,myfigure,ifone,la_one,lo_one) :
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
    #
    if ifone :
        cs=plt.scatter(lo_one, la_one, c=myvals, s=50, marker='o', cmap=mycmap, norm=mynorm)
    else :
        cs=plt.scatter(lo, la, c=myvals, s=50, marker='o', cmap=mycmap, norm=mynorm)
        cb=map.colorbar(cs,"right", size="5%", pad="2%")
    #
    plt.title(mytitle)
    plt.savefig(myfigure, dpi=300)
    plt.close()

# Just for finding a "random" station near the location that you want ???
# Borrowed from 
# https://stackoverflow.com/questions/41336756/find-the-closest-latitude-and-longitude
#
def distance(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295
    hav = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p)*cos(lat2*p) * (1-cos((lon2-lon1)*p)) / 2
    return 12742 * asin(sqrt(hav))

def closest(data, v):
    return min(data, key=lambda p: distance(v['lat'],v['lon'],p['lat'],p['lon']))

# Plot IDF curves (can it be generic one ?)
# Yep, do it !
def plot_idf_curves(duration,dat,ifmmh,labels,styles,colors,pngtitle,pngfile) :
    #
    fig=plt.figure()
    #
    for i in np.arange(np.shape(dat)[0]) :
        if ifmmh :
            plt.plot(duration,dat[i,:]/duration,colors[i],label=labels[i],linewidth=2.5,linestyle=styles[i])
        else :
            plt.plot(duration,dat[i,:],colors[i],label=labels[i],linewidth=2.5,linestyle=styles[i])

    # Because I saw it (good to be manually edit sometimes)
    #plt.ylim(0,50)
    plt.xlim(np.nanmin(duration)-1,np.nanmax(duration)+1)
    plt.xticks([3,6,12,24,48,72])

    # Show sub-daily boundary line
    plt.axvline(x = 24, color = 'grey', linestyle='--')

    # Show change factor line = 1
    plt.axhline(y = 1, color = 'grey', linestyle='--')

    plt.title(pngtitle,y=1.05)

    plt.xlabel('Duration (h)')
    if ifmmh :
        plt.ylabel('Intensity (mm/h)')
    else :
        plt.ylabel('Intensity (mm)')

    plt.legend(loc='best')
    plt.savefig(pngfile,dpi=300)
    plt.close()
#
# ============================================================= #
#

# Get argument
stafl, outdir, caseA, caseB, indir1, indir2 = get_argument()

# Read list of stations
#stalist, lat, lon, stainfo = read_stationinfo(str(stafl))
stalist, lat, lon = read_stationinfo(str(stafl))

# If you want to read data from all stations
if ifreadallstation :

    # Is it too big array ?
    df_A=np.zeros((len(stalist),len(seasons),len(frequency),len(duration)))
    df_B=np.zeros((len(stalist),len(seasons),len(frequency),len(duration)))
    
    for j in np.arange(len(seasons)) :
        for i in np.arange(len(stalist)) :
    
            # Read case A
            mfl=str(indir1)+str(stalist[i]).strip()+'_'+str(seasons[j])+'.csv'
            tmp=read_output(mfl)
            df_A[i,j,:,:]=tmp
    
            # Read case B
            mfl=str(indir2)+str(stalist[i]).strip()+'_'+str(seasons[j])+'.csv'
            tmp=read_output(mfl)
            df_B[i,j,:,:]=tmp
    
    # Change of mean (glance)
    #print (np.nanmean(df_A))
    #print (np.nanmean(df_B))
    
    #
    # "Simple" change factor
    #
    cf=np.zeros((len(stalist),len(seasons),len(frequency),len(duration)))
    #
    for j in np.arange(len(seasons)) :
        for i in np.arange(len(stalist)) :
            for k in np.arange(len(frequency)) :
    
                series_A=df_A[i,j,k,:] / duration
                series_B=df_B[i,j,k,:] / duration 
    
                tmp = series_B / series_A
    
                cf[i,j,k,:]=tmp
    
    #print (np.nanmean(cf))

#
# One station: how IDF curves look like?
#
""" Hum, too manually ?
tmp = np.where(np.logical_and(lon <-85.5, lon >-86.5, lat < 39.5), stalist, np.nan)
station = np.where(lat > 39, tmp, np.nan)  # np.logical_and no more than 3 conditions
print (station)
"""
# Find the closet one
# Hum, this guy did good ?
# https://stackoverflow.com/questions/41336756/find-the-closest-latitude-and-longitude
#
"""
tempDataList = [{'lat': lat[i], 'lon': lon[i]} for i in np.arange(len(lat))] 
v = {'lat': in_lat, 'lon': in_lon}
coordinates = closest(tempDataList, v)
station = np.where(np.logical_and(lat == coordinates['lat'], lon == coordinates['lon']), stalist, np.nan)
#print (station)
"""
# Woa, "suddenly" don't want to waste 5 mins here !
# Print it out and see that the station is USC00125407
#
staname="USC00125407"
# Grep it
# USC00125407,95.34883720930233,95.34883720930233,39.4039,-86.4531,93.02325581395348,93.02325581395348
lat_s = 39.4039
lon_s = -86.4531
#

# Read and analyze only one station
if ifreadonestation :

    df_1=np.zeros((len(seasons),len(frequency),len(duration)))
    df_2=np.zeros((len(seasons),len(frequency),len(duration)))
    
    for j in np.arange(len(seasons)) :
    
            # Read case A
            mfl=str(indir1)+str(staname).strip()+'_'+str(seasons[j])+'.csv'
            tmp=read_output(mfl)
            df_1[j,:,:]=tmp
    
            # Read case B
            mfl=str(indir2)+str(staname).strip()+'_'+str(seasons[j])+'.csv'
            tmp=read_output(mfl)
            df_2[j,:,:]=tmp
    
    # Change of mean (glance)
    #print (np.nanmean(df_1))
    #print (np.nanmean(df_2))
    print ("Mean diff : ",np.nanmean(df_2)-np.nanmean(df_1))
    print ("Shape : ",np.shape(df_2),np.shape(df_1))
    
    #
    # 291 : step by step
    #
    # Plot the location of stations on map (to make sure)
    mytitle="Location of random station to check"
    myfigure=str(outdir).strip()+"One_station_near_BL.png"
    #mapplot(99,lat,lon,buff,mycmap,mynorm,mytitle,myfigure,True,lat_s,lon_s)
    # The location looks good !!!
    #
    # Now, IDF curves
    #
    for i in np.arange(len(seasons)) :
        toplot=[] ; lbl=[] ; stl=[] ; cols=[]
        for j in np.arange(len(frequency)) :
            toplot.append(df_1[i,j,:])
            lbl.append(str(caseA) +" "+ str(freqname[j]))
            stl.append(str(freqstyle[j]))
            cols.append('k')

            toplot.append(df_2[i,j,:])
            lbl.append(str(caseB) +" "+ str(freqname[j]))
            stl.append(str(freqstyle[j]))
            cols.append('r')

        mytitle="Station : "+str(staname).strip()+" ("+str(seasons[i]).strip()+")"
        myfigure=str(outdir).strip()+"IDF_"+str(staname).strip()+"_"+str(caseA)+"vs"+str(caseB)+"_"+str(seasons[i]).strip()+".png"
        # In mm/h (NO, the issue on the IO of fixIDF jumps in here
        # See : https://github.com/ClimDesign/fixIDF
        # "A suitable unit for the input precipitation return levels would for example be mm.
        # A unit that would be inappropriate would be mm/hour."
        #plot_idf_curves(duration,np.array(toplot),True,lbl,stl,cols,mytitle,myfigure)
        # In mm <===
        plot_idf_curves(duration,np.array(toplot),False,lbl,stl,cols,mytitle,myfigure)

"""
# 
# Plot change factor
#
for j in np.arange(len(seasons)) :
    mfl=str(outdir)+'CF_'+str(caseB)+'_per_'+str(caseA)+'_'+str(seasons[j])+'.png'
    mtt=str(seasons[j])
    plot_cf_sigma(frequency,duration,cf[:,j,:,:],freqname,mcolors,mtt,mfl)
"""
#
# ============================================================= #
#
# C'est fin !
#
# ============================================================= #
