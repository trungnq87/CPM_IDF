# ============================================================= #
#
# Step 03 : Basemap of relative errors of WRF-Hist
#           Notice : for boxplot please use py_02_*
#
# Wanna discuss: trqnguye@iu.edu
#
# ============================================================= #
#
# Libraries
import argparse
import matplotlib as mpl
mpl.use('Agg')
#
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import seaborn as sns
#from math import cos, asin, sqrt
from matplotlib.offsetbox import (AnchoredOffsetbox, AuxTransformBox,
                                  DrawingArea, TextArea, VPacker)
# Zoomed ? no, but nice
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
# Inset axes
from mpl_toolkits.axes_grid.inset_locator import inset_axes
#
# ============================================================= #
#
# Parameters
seasons=["DJF","MAM","JJA","SON"]
#duration=np.arange(3,75,3)
duration=np.array([3,6,12,24,48,72])
frequency=[20,50,100]

# For labelling
freqname=['20-yr','50-yr','100-yr']
freqstyle=['dashdot','dashed','solid']
mcolors=['g','b','r']
myfontsz=18
fcols=[(0.9873125720876587, 0.6473663975394078, 0.3642445213379469), (0.9971549404075356, 0.9118031526336025, 0.6010765090349866), (0.6334486735870821, 0.8521337946943485, 0.6436755094194541)]

# For plotting map
buff=-0.75
bounds=np.arange(-30,35,5)
selectdura=[3,24,72]

# Station near Bloomington, IN
staname="USC00125407"
lat_bl = 39.4039
lon_bl = -86.4531

# Some options for playing with data
ifreadallstation=True
ifboxplot=False # Should be always False here (use py_02_* for correct plotting function)
ifmapplot=True
ifadjust=True
if3dview=True
ifdebug=False

#
# ============================================================= #
#
# Functions

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
    return sta, lat, lon

# Read IDF outputs (hum, will I keep this format ?)
def read_output(filename) :
    dat = pd.read_csv(filename, header=0, index_col=0)
    outdat = np.array(dat.values).T
    return outdat

# Load data array from files
def load_data(df,seasons,stalist,indir) :
    for j in np.arange(len(seasons)) :
        for i in np.arange(len(stalist)) :
            mfl=str(indir)+str(stalist[i]).strip()+'_'+str(seasons[j])+'.csv'
            #print ("Reading data from : ",mfl)
            tmp=read_output(mfl)
            df[i,j,:,:]=tmp
    return df

# Deal with color 
def cmap_norm(bounds,cmapin) :
    mycmap = plt.get_cmap(cmapin)
    mynorm = mpl.colors.BoundaryNorm(bounds, mycmap.N)
    return mycmap,mynorm 

# Plot on map (can it be generic?)
def mapplot(la,lo,myvals,buff,mycmap,mynorm,myfontsize,mytitle,myfigure,subcol) :

    fig = plt.figure()
    ax = fig.add_subplot(111)

    map = Basemap(projection='cyl',llcrnrlon=np.nanmin(lo+buff),llcrnrlat=np.nanmin(la+buff),urcrnrlon=np.nanmax(lo-buff),urcrnrlat=np.nanmax(la-buff),resolution='h')

    parallels = np.arange(-90,90,5.)
    meridians = np.arange(-180,180,5.)
    map.drawparallels(parallels,labels=[1,0,0,0],fontsize=18,color="grey")
    map.drawmeridians(meridians,labels=[0,0,0,1],fontsize=18,color="grey")
    map.drawcoastlines()
    map.drawrivers(color='grey')
    map.drawstates()
    
    cs=plt.scatter(lo, la, c=myvals, s=50, marker='o', cmap=mycmap, norm=mynorm)
    cb=map.colorbar(cs,"right", size="5%", pad="2%")
    cb.ax.set_title('(%)')

    plt.title(mytitle)

    # If you only want few stats info
    #outstr = get_stat(myvals)
    #draw_text(ax, outstr)

    # If you want to seriously live your life
    #draw_sub_boxplot(ax,map,myvals,la)
    draw_sub_boxplot(ax,myvals,subcol)

    plt.savefig(myfigure, dpi=300)
    #plt.savefig(myfigure, dpi=300, facecolor=fig.get_facecolor())

    plt.close()

# Plot IDF curves (for one station case)
def plot_idf_curves(duration,dat,ifmmh,labels,styles,colors,pngtitle,pngfile) :
    fig=plt.figure()
    for i in np.arange(np.shape(dat)[0]) :
        if ifmmh :
            plt.plot(duration,dat[i,:]/duration,colors[i],label=labels[i],linewidth=2.5,linestyle=styles[i])
        else :
            plt.plot(duration,dat[i,:],colors[i],label=labels[i],linewidth=2.5,linestyle=styles[i])

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

# Calculate absolute and relative differences
def cal_diff(B,A) :
    abs_dif = B - A
    rel_dif = 100 * (B - A) / A
    return abs_dif, rel_dif

# Well, I always want a file name or title
def make_a_name(deli,instr) :
    outstring=""
    for i in np.arange(len(instr)-1) :
        outstring=outstring+str(instr[i]).strip()+str(deli)
    # Arg, will have _.png but let fix it later !
    outstring=outstring+str(instr[-1]).strip()
    return outstring

# Plot box-plot
def plot_boxplot(dura,freq,dat,incol,ylab,myfontsize,pngtitle,pngfile,ifoutliers) :

    fig, ax = plt.subplots(figsize=(15,8))

    dim1, dim2, dim3 = np.meshgrid(np.arange(dat.shape[2]), np.arange(dat.shape[0]), np.arange(dat.shape[1]), indexing='ij')

    #sns.set_style('whitegrid')

    # Use your defined colors
    #ax = sns.boxplot(x=dim1.ravel(), y=dat.ravel(), hue=dim3.ravel(), palette=incol)

    # Or sns palette
    ax = sns.boxplot(x=dim1.ravel(), y=dat.ravel(), hue=dim3.ravel(), palette='Spectral', showfliers=ifoutliers)

    ax.legend(handles=ax.legend_.legendHandles, labels=freq, fontsize=myfontsize)
    ax.set_xticklabels(dura)
    #sns.despine()

    #plt.ylim(0,50)
    #plt.xlim(np.nanmin(duration)-1,np.nanmax(duration)+1)
    #plt.xticks([3,6,12,24,48,72])

    # Show sub-daily boundary line ( 3 hourly frequency)
    plt.axvline(x = 6.5, color = 'grey', linestyle='--')

    plt.xlabel('Duration (h)', fontsize=myfontsize)
    plt.ylabel(ylab, fontsize=myfontsize)
    plt.title(pngtitle, fontsize=myfontsize)

    # We change the fontsize of minor ticks label
    ax.tick_params(axis='both', which='major', labelsize=myfontsize)
    ax.tick_params(axis='both', which='minor', labelsize=myfontsize)

    plt.tight_layout()
    plt.savefig(pngfile,dpi=300)
    plt.close()

# Get statistics of array
def get_stat(dat) :

    meanval="{:.2f}".format(np.nanmean(dat))
    medval="{:.2f}".format(np.nanmedian(dat))
    maxval="{:.2f}".format(np.nanmax(dat))
    minval="{:.2f}".format(np.nanmin(dat))

    nsample=str(np.count_nonzero(~np.isnan(dat)))
    nall=str(len(dat))

    mystr=" Stations : "+nsample+" / "+nall+" \n "+"Mean/Median : "+meanval+" / "+medval+" \n "+"Min/Max : "+minval+" / "+maxval

    return mystr

# Adapted from https://matplotlib.org/stable/gallery/misc/anchored_artists.html
def draw_text(ax, instr) :
    """Draw a text-box anchored to the lower-right corner of the figure."""
    box = AnchoredOffsetbox(child=TextArea(instr),
                            loc="lower right", frameon=True)
    box.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
    ax.add_artist(box)

# Learnt from :
# https://basemaptutorial.readthedocs.io/en/latest/locator.html
# oh, here : https://matplotlib.org/2.0.2/examples/pylab_examples/axes_demo.html
#
# https://www.geeksforgeeks.org/matplotlib-pyplot-axes-in-python/
# # to generate window of custom  
# dimensions [left, bottom, width, 
# height] along with the facecolor  
#def draw_sub_boxplot(ax, m, vals, la) :
def draw_sub_boxplot(ax, vals, sc) :
    """Draw a box-plot anchored to the lower-right corner of the figure."""

    # convert to map projection coords.
    # Note that lon,lat can be scalars, lists or numpy arrays.
    #xpt,ypt = m(lon,lat)
    #xpt,ypt = m(-85,np.nanmin(la))
    #print ("Good song never die ! ",xpt,ypt)
    #a = plt.axes([xpt, ypt, .2, .1], facecolor='white')

    #a = plt.axes([0.6, 0.25, .2, .1], facecolor='white', frameon=False)
    #a = plt.axes([0.6, 0.25, .2, .08], facecolor='y', frameon=False)
    #a = plt.axes([0.6, 0.25, .2, .08], facecolor='white')
    a = plt.axes([0.61, 0.245, .2, .09], facecolor='white')

    #c='#4273b3'

    #box1 = plt.boxplot(vals, vert=False, showfliers=False, patch_artist=True, boxprops=dict(facecolor=c, color=c))
    box1 = plt.boxplot(vals, vert=False, showfliers=False, patch_artist=True, boxprops=dict(facecolor=sc),  medianprops=dict(color='k'), widths=0.5)

    #instr='No. of stations : '+str(len(vals))
    instr=' N = '+str(len(vals))
    plt.title(instr)
    #plt.text(0.1, 1.5, instr)

    #for item in ['boxes', 'whiskers', 'fliers', 'medians', 'caps']:
    #    plt.setp(box1[item], color='orange')
    #plt.setp(box1['boxes'], color='orange')

    #plt.xlim(0, 0.2)
    #plt.xticks([])

    plt.yticks([])

"""
Color
import seaborn as sns
from PIL import Image, ImageDraw

iter = 15
palette = list(reversed(sns.color_palette("Spectral", iter).as_hex()))
print(palette)
['#4471b2', '#3d95b8', '#5eb9a9', '#86cfa5', '#b1dfa3', '#d6ee9b', '#eff9a6', '#ffffbe', '#feec9f', '#fed481', '#fdb567', '#f98e52', '#f06744', '#dd4a4c', '#c1274a']
or '_r'
['#be254a', '#dc484c', '#ef6645', '#f88c51', '#fdb365', '#fed27f', '#feeb9d', '#fffebe', '#f0f9a7', '#d8ef9b', '#b3e0a2', '#89d0a4', '#60bba8', '#3f97b7', '#4273b3']

no, this one :
sns.color_palette("Spectral")
[(0.8853517877739331, 0.3190311418685121, 0.29042675893886966), (0.9873125720876587, 0.6473663975394078, 0.3642445213379469), (0.9971549404075356, 0.9118031526336025, 0.6010765090349866), (0.9288735101883892, 0.9715494040753557, 0.6380622837370243), (0.6334486735870821, 0.8521337946943485, 0.6436755094194541), (0.2800461361014994, 0.6269896193771626, 0.7024221453287197)]

"""

#
# ============================================================= #
#
# Main game
if __name__ == "__main__":
    
    # Get arguments
    stafl, outdir, caseA, caseB, indir1, indir2 = get_argument()
    print ("Using station list : ",stafl)
    print ("Analyzing cases : ",caseA, caseB)
    print ("Output folder is : ",outdir)

    # Read list of stations
    stalist, lat, lon = read_stationinfo(str(stafl))
    
    # If you want to read data from all stations
    if ifreadallstation :

        # Is it too big array ?
        # or make it bigger df[case,:,:,:,:] ?
        df_A=np.zeros((len(stalist),len(seasons),len(frequency),len(duration)))
        df_B=np.zeros((len(stalist),len(seasons),len(frequency),len(duration)))
    
        # Load data array
        df_A=load_data(df_A,seasons,stalist,indir1)
        df_B=load_data(df_B,seasons,stalist,indir2)
        
        # Change of mean (glance)
        print ("Mean of df_A / df_B")
        print (np.nanmean(df_A), np.nanmean(df_B))

        # Relative errors are only for historical period
        # Still not "professional" way for coding ? then, how ?
        abs_diff,rel_diff = cal_diff(df_B,df_A)

        # Check mean
        print ("Mean of abs_diff / rel_diff")
        print (np.nanmean(abs_diff),np.nanmean(rel_diff))

        if ifboxplot :
            # Plot box-plot for each seasons
            for i in np.arange(len(seasons)) :

                # NO outliers : should be used in the article
    
                # Absolute errors 
                pngtitle=make_a_name(" ",["Errors :",caseB,"minus",caseA,"in",seasons[i]])
                pngfile=make_a_name("_",[outdir,"Abs_diff",caseB,"minus",caseA,seasons[i],".png"])
                plot_boxplot(duration,freqname,abs_diff[:,i,:,:],mcolors,"Errors (mm)",myfontsz,pngtitle,pngfile,False)
    
                # Relative errors
                pngtitle=make_a_name(" ",["Relative errors :",caseB," vs ",caseA,"in",seasons[i]])
                pngfile=make_a_name("_",[outdir,"Rel_diff",caseB,"vs",caseA,seasons[i],".png"])
                plot_boxplot(duration,freqname,abs_diff[:,i,:,:],mcolors,"Relative errors (%)",myfontsz,pngtitle,pngfile,False)
    
                # With outliers : should be kept in Supplementary section
    
                # Absolute errors 
                pngtitle=make_a_name(" ",["Errors :",caseB,"minus",caseA,"in",seasons[i]])
                pngfile=make_a_name("_",[outdir,"Outliers_Abs_diff",caseB,"minus",caseA,seasons[i],".png"])
                plot_boxplot(duration,freqname,abs_diff[:,i,:,:],mcolors,"Errors (mm)",myfontsz,pngtitle,pngfile,True)
    
                # Relative errors
                pngtitle=make_a_name(" ",["Relative errors :",caseB," vs ",caseA,"in",seasons[i]])
                pngfile=make_a_name("_",[outdir,"Outliers_Rel_diff",caseB,"vs",caseA,seasons[i],".png"])
                plot_boxplot(duration,freqname,abs_diff[:,i,:,:],mcolors,"Relative errors (%)",myfontsz,pngtitle,pngfile,True)

        if ifmapplot :
            # Map plot for each seasons and each frequency (oh, and each duration !)
            for i in np.arange(len(seasons)) :
                for j in np.arange(len(frequency)) :
                    for k in np.arange(len(duration)) :

                        for l in np.arange(len(selectdura)) :
                            if selectdura[l] == duration[k] :

                                # Relative errors
                                print (" ","Relative errors :",seasons[i],freqname[j],duration[k],"(h)")
                                pngtitle=make_a_name(" ",["Relative errors :",seasons[i],freqname[j],duration[k],"(h)"])
                                pngfile=make_a_name("_",[outdir,"Map_rel_err",seasons[i],freqname[j],duration[k],".png"])
                                mcmap, mnorm = cmap_norm(bounds,'bwr')
                                mapplot(lat,lon,rel_diff[:,i,j,k],buff,mcmap,mnorm,myfontsz,pngtitle,pngfile,fcols[j])

                                # If debug (or develop)
                                if ifdebug :
                                    sys.exit()

    # Read and analyze only one station
    # One station: how IDF curves look like?
    else :

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
        print ("Mean diff : ",np.nanmean(df_2)-np.nanmean(df_1))
        print ("Shape : ",np.shape(df_2),np.shape(df_1))
    
        # Now, IDF curves
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
            # Plot
            mytitle="Station : "+str(staname).strip()+" ("+str(seasons[i]).strip()+")"
            myfigure=str(outdir).strip()+"IDF_"+str(staname).strip()+"_"+str(caseA)+"vs"+str(caseB)+"_"+str(seasons[i]).strip()+".png"
            plot_idf_curves(duration,np.array(toplot),False,lbl,stl,cols,mytitle,myfigure)

#
# ============================================================= #
#
# C'est fin ! How do you see the "donut"?
#
# ============================================================= #
