# ============================================================= #
#
# Step 04 : "Change factor" : box-plot, select only stations 
#           with relative errors less than a threshold
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
myfontsz=28

# For plotting map
buff=-0.75

# Station near Bloomington, IN
staname="USC00125407"
lat_bl = 39.4039
lon_bl = -86.4531

# Some options for playing with data
ifreadallstation=True
ifboxplot=True
ifmapplot=False
ifadjust=True
if3dview=True

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
    parser.add_argument("-c", "--inputcaseC", help="Location of input files of case C")
    parser.add_argument("-d", "--inputcaseD", help="Location of input files of case D")

    parser.add_argument("-na", "--nameinputA", help="Experiment name of case A")
    parser.add_argument("-nb", "--nameinputB", help="Experiment name of case B")
    parser.add_argument("-nc", "--nameinputC", help="Experiment name of case C")
    parser.add_argument("-nd", "--nameinputD", help="Experiment name of case D")

    parser.add_argument("-th", "--threshold", help="Threshold of accepted relative errors")

    args = parser.parse_args()
    config = vars(args)
    
    out1=config['stationlist']
    out2=config['output']

    out3=config['nameinputA']
    out4=config['nameinputB']
    out5=config['nameinputC']
    out6=config['nameinputD']

    out7=config['inputcaseA']
    out8=config['inputcaseB']
    out9=config['inputcaseC']
    out10=config['inputcaseD']

    out11=config['threshold']

    return out1, out2, out3, out4, out5, out6, out7, out8, out9, out10, out11

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
    outdat = np.array(dat.values)
    return outdat

# Load data array from files
def load_data(df,seasons,stalist,indir) :
    for j in np.arange(len(seasons)) :
        for i in np.arange(len(stalist)) :
            mfl=str(indir)+str(stalist[i]).strip()+'_'+str(seasons[j])+'.csv'
            #print ("Reading data from : ",mfl)
            tmp=read_output(mfl)
            df[:,i,j,:]=tmp
    return df

# Deal with color 
def cmap_norm(bounds,cmapin) :
    mycmap = plt.get_cmap(cmapin)
    mynorm = mpl.colors.BoundaryNorm(bounds, mycmap.N)
    return mycmap,mynorm 

# Plot on map (can it be generic?)
def mapplot(myvals,la,lo,buff,mycmap,mynorm,mytitle,myfigure) :

    fig = plt.figure()
    ax = fig.add_subplot(111)

    map = Basemap(projection='cyl',llcrnrlon=np.nanmin(lo+buff),llcrnrlat=np.nanmin(la+buff),urcrnrlon=np.nanmax(lo-buff),urcrnrlat=np.nanmax(la-buff),resolution='h')

    parallels = np.arange(-90,90,5.)
    meridians = np.arange(-180,180,5.)
    map.drawparallels(parallels,labels=[1,0,0,0],fontsize=18,color="grey")
    map.drawmeridians(meridians,labels=[0,0,0,1],fontsize=18,color="grey")
    map.drawstates()
    map.drawcoastlines()
    map.drawrivers(color='blue')
    
    cs=plt.scatter(lo, la, c=myvals, s=50, marker='o', cmap=mycmap, norm=mynorm)
    cb=map.colorbar(cs,"right", size="5%", pad="2%")

    plt.title(mytitle)
    plt.savefig(myfigure, dpi=300)
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

# Calculate change factor (do I need a function?)
def change_factor(B,A) :
    cf = B/A
    return cf

# Mask 4D array (manually, omg)
def mymask(AA,rel,threshold) :

    out = np.full_like(AA, np.nan)
    th = float(threshold)

    for i in np.arange(np.shape(AA)[0]) :
        for j in np.arange(np.shape(AA)[1]) :
            for k in np.arange(np.shape(AA)[2]) :
                for l in np.arange(np.shape(AA)[3]) :
                    if ( rel[i,j,k,l] < abs(th) and rel[i,j,k,l] > -1*abs(th) ) :
                        out[i,j,k,l] = AA[i,j,k,l]
    return out

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

    dim1, dim2, dim3 = np.meshgrid(np.arange(dat.shape[0]), np.arange(dat.shape[1]), np.arange(dat.shape[2]), indexing='ij')

    #sns.set_style('whitegrid')

    # Use your defined colors
    #ax = sns.boxplot(x=dim1.ravel(), y=dat.ravel(), hue=dim3.ravel(), palette=incol)

    # Or sns palette
    #ax = sns.boxplot(x=dim1.ravel(), y=dat.ravel(), hue=dim3.ravel(), palette='Spectral', showfliers=ifoutliers)
    ax = sns.boxplot(x=dim1.ravel(), y=dat.ravel(), hue=dim3.ravel(), palette=incol, showfliers=ifoutliers)

    #ax.legend(handles=ax.legend_.legendHandles, labels=freq, fontsize=int(myfontsize*1.2))
    ax.legend(handles=ax.legend_.legendHandles, labels=freq, fontsize=myfontsize, loc='upper left')
    ax.set_xticklabels(dura)
    #sns.despine()

    # As 16 Oct 2023 :
    #plt.ylim(0.6,2.8)
    # As 26 Jan 2024 :
    plt.ylim(0.5,3.0)

    #plt.xlim(np.nanmin(duration)-1,np.nanmax(duration)+1)
    #plt.xticks([3,6,12,24,48,72])

    # Show sub-daily boundary line ( 3 hourly frequency)
    #plt.axvline(x = 6.5, color = 'grey', linestyle='--')
    plt.axvline(x = 2.5, color = 'grey', linestyle='--')

    plt.xlabel('Duration (h)', fontsize=myfontsize)
    plt.ylabel(ylab, fontsize=myfontsize)
    plt.title(pngtitle, fontsize=myfontsize)

    # We change the fontsize of minor ticks label
    ax.tick_params(axis='both', which='major', labelsize=myfontsize)
    ax.tick_params(axis='both', which='minor', labelsize=myfontsize)

    # Plot no change y=1 line
    plt.axhline(y = 1.0, color = 'red', linestyle='--', linewidth=2.5)

    plt.tight_layout()
    plt.savefig(pngfile,dpi=300)
    plt.close()

#
# ============================================================= #
#
# Main game
if __name__ == "__main__":
    
    # Get arguments
    stafl, outdir, caseA, caseB, caseC, caseD, indir1, indir2, indir3, indir4, threshold = get_argument()
    print ("Using station list : ",stafl)
    print ("Analyzing cases : ",caseA, caseB, caseC, caseD)
    print ("Output folder is : ",outdir)
    print ("Accepted threshold for relative errors is : ",threshold," (%) ")

    # Read list of stations
    stalist, lat, lon = read_stationinfo(str(stafl))
    
    # If you want to read data from all stations
    if ifreadallstation :

        # Is it too big array ?
        # or make it bigger df[case,:,:,:,:] ?
        df_A=np.zeros((len(duration),len(stalist),len(seasons),len(frequency)))
        df_B=np.zeros((len(duration),len(stalist),len(seasons),len(frequency)))
        df_C=np.zeros((len(duration),len(stalist),len(seasons),len(frequency)))
        df_D=np.zeros((len(duration),len(stalist),len(seasons),len(frequency)))
    
        # Load data array
        df_A=load_data(df_A,seasons,stalist,indir1)
        df_B=load_data(df_B,seasons,stalist,indir2)
        df_C=load_data(df_C,seasons,stalist,indir3)
        df_D=load_data(df_D,seasons,stalist,indir4)
        
        # Change of mean (glance)
        print ("Mean of df_A / df_B / df_C / df_D")
        print (np.nanmean(df_A), np.nanmean(df_B), np.nanmean(df_C), np.nanmean(df_D))

        # Relative errors are only for historical period
        # Still not "professional" way for coding ? then, how ?
        abs_diff,rel_diff = cal_diff(df_B,df_A)

        # Check mean
        print ("Mean of abs_diff / rel_diff")
        print (np.nanmean(abs_diff),np.nanmean(rel_diff))

        # Indexing used array by defined threshol (oh, my English, whatever, moving on)
        #th=float(threshold) # Oh my Py
        #df_A_s = df_A[np.where((rel_diff < abs(th)) & (rel_diff > -1*abs(th)))]
        #df_C_s = df_C[np.where((rel_diff < abs(th)) & (rel_diff > -1*abs(th)))]
        #df_D_s = df_D[np.where((rel_diff < abs(th)) & (rel_diff > -1*abs(th)))]
        # I just don't want to make mistake (here, in rush), so
        df_A_s = mymask(df_A,rel_diff,threshold)
        df_C_s = mymask(df_C,rel_diff,threshold)
        df_D_s = mymask(df_D,rel_diff,threshold)
        
        # Change of mean (glance)
        print ("Mean of df_A_s / df_C_s / df_D_s")
        print (np.nanmean(df_A_s), np.nanmean(df_C_s), np.nanmean(df_D_s))

        # Now change factor :
        cf_C = df_C_s / df_A_s
        cf_D = df_D_s / df_A_s

        print ("Check shape cf_C / df_C_s / df_A_s")
        print (np.shape(cf_C),np.shape(df_C_s),np.shape(df_A_s))

        print ("Mean of cf_C / cf_D")
        print (np.nanmean(cf_C), np.nanmean(cf_D))

        # Plot box-plot for each seasons
        for i in np.arange(len(seasons)) :

            # NO outliers : should be used in the article

            # Change factor case C (should be RCP 4.5)
            pngtitle=make_a_name(" ",["Change factor :",caseC," vs ",caseA," in ",seasons[i]])
            pngfile=make_a_name("_",[outdir,"CF",caseC,"vs",caseA,seasons[i],".png"])
            plot_boxplot(duration,freqname,cf_C[:,:,i,:],"Paired","Change factor (-)",myfontsz,pngtitle,pngfile,False)

            # Change factor case D (should be RCP 8.5)
            pngtitle=make_a_name(" ",["Change factor :",caseD," vs ",caseA," in ",seasons[i]])
            pngfile=make_a_name("_",[outdir,"CF",caseD,"vs",caseA,seasons[i],".png"])
            plot_boxplot(duration,freqname,cf_D[:,:,i,:],"Set2","Change factor (-)",myfontsz,pngtitle,pngfile,False)

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
# C'est fin !
#
# ============================================================= #
# Non, c'est pas... it's never easy... it has been not easy
# Still don't know if it's my own view or it's a fact...
# Not easy to do research with an empty stomach...
# and a mind full of family and financial issues...
# But, it ain't about how hard you get hit...
# It's about hard you get hit and keep moving forward !
# It's not easy to forgive myself... when groundhog day keeps coming
# But, sometimes, you just forgive yourself and keep moving
# Hope is dangerous but marvellous thing !
# ============================================================= #
