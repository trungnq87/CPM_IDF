# ============================================================= #
#
# Plot all the IDF curves (oh, yeah, remember to submit jobs)
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
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
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

# Some options for playing with data
ifreadallstation=True

# For coloring the IDF curves
gacolors=['limegreen','dodgerblue','orangered','crimson']

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

# Plot IDF curves (for one station case)
def plot_idf_curves(duration,a,b,labels,colors,pngtitle,pngfile) :

    #fig=plt.figure()
    fig, ax = plt.subplots(figsize=(15,10))

    for i in np.arange(np.shape(a)[0]) :

        plt.plot(duration,a[i,:],colors[i],linewidth=3.5,linestyle='--')

        plt.plot(duration,b[i,:],colors[i],label=labels[i],linewidth=4.0,linestyle='-')

    #plt.ylim(0,50)
    plt.xlim(np.nanmin(duration)-1,np.nanmax(duration)+1)
    plt.xticks([3,6,12,24,48,72])

    # Show sub-daily boundary line
    plt.axvline(x = 24, color = 'grey', linestyle='--')

    #plt.title(pngtitle,y=1.05)
    plt.title(pngtitle, fontsize=28)
    plt.suptitle("Return periods: 100-year (solid lines) & 20-year (dashed lines)", fontsize=28)

    plt.xlabel('Duration (h)', fontsize=28)
    plt.ylabel('Intensity (mm)', fontsize=28)

    # We change the fontsize of minor ticks label
    ax.tick_params(axis='both', which='major', labelsize=28)
    ax.tick_params(axis='both', which='minor', labelsize=28)

    plt.legend(loc='best', fontsize=28)
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

        for i in np.arange(len(seasons)) :
            for j in np.arange(len(stalist)) :
                
                pngtitle="Station : "+stalist[j]+"                           Season : "+seasons[i]
                pngfile=make_a_name("_",[outdir,seasons[i],"GA",stalist[j],seasons[i],".png"])
                labels=[caseA,caseB,caseC,caseD]

                # Only 20-yr and 100-yr now !
                dat1=[]
                dat1.append(df_A[:,j,i,0])
                dat1.append(df_B[:,j,i,0])
                dat1.append(df_C[:,j,i,0])
                dat1.append(df_D[:,j,i,0])

                dat2=[]
                dat2.append(df_A[:,j,i,2])
                dat2.append(df_B[:,j,i,2])
                dat2.append(df_C[:,j,i,2])
                dat2.append(df_D[:,j,i,2])

                plot_idf_curves(duration,np.array(dat1),np.array(dat2),labels,gacolors,pngtitle,pngfile)

    # Read and analyze only one station
    # One station: how IDF curves look like?
    else :

        print ("Deleted option")

#
# ============================================================= #
#
# C'est fin !
#
# ============================================================= #
