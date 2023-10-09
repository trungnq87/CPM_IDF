# ============================================================= #
#
# Plot heatmap of DTS test results (null not rejected cases)
#
# ============================================================= #
#
# Import as usual
import argparse
import numpy as np
import pandas as pd
import sys
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
#
# ============================================================= #
#
# Parameters or unchanged inputs
#
# Seasons
#seasons=['1','2','3','4','5','6','7','8','9','10','11','12']
#months=[[1],[2],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12]]
months=[1,2,3,4,5,6,7,8,9,10,11,12]
#
nduration=24
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

    args = parser.parse_args()
    config = vars(args)
    
    out1=config['stationlist']
    out2=config['input']
    out3=config['output']

    return out1, out2, out3

# Read station info
#
def read_stationinfo(filename) :
    df=pd.read_csv(filename,header=0)
    sta=df.iloc[:,0].values
    return sta
#
# Read DTS test output
#
def read_dts_output(filename) :
    df=pd.read_csv(filename, header=0)
    return df
#
# Plot heatmap
def plot_heatmap(a,b,pngfile,dpi) :

    yticks=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    xticks=['' for i in np.arange(24)]
    xticks[0]='3h'
    #i=7 ; j=i*3+3
    xticks[7]='24h'
    xticks[15]='48h'
    xticks[-1]='72h'

    myfontsize=18

    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, figsize=(8,15))

    fig.suptitle('ECDF two-sample test statistic: DTS approach', fontsize=myfontsize)

    #sns.heatmap(a.T, ax=ax1, annot=True, vmin=0, vmax=74, cmap='crest')
    #s1 = sns.heatmap(a.T, ax=ax1, vmin=0, vmax=74, cmap='crest', yticklabels=yticks)
    s1 = sns.heatmap(a.T, ax=ax1, vmin=0, vmax=74, cmap='crest')
    ax1.set_ylabel("Months", fontsize=myfontsize)
    ax1.axvline(x = 7.5, color = 'grey', linestyle='--')
    ax1.set_title('(a) For original WRF output', fontsize=myfontsize)
    ax1.set_yticklabels(yticks, rotation=0)

    s2 = sns.heatmap(b.T, ax=ax2, vmin=0, vmax=74, cmap='crest', yticklabels=yticks)
    ax2.set_ylabel("Months", fontsize=myfontsize)
    ax2.axvline(x = 7.5, color = 'grey', linestyle='--')
    ax2.set_title('(b) For bias-corrected WRF data', fontsize=myfontsize)
    ax2.set_yticklabels(yticks, rotation=0)

    s3 = sns.heatmap((b-a).T, ax=ax3, vmin=-20, vmax=20, cmap='bwr', yticklabels=yticks, xticklabels=xticks)
    ax3.set_ylabel("Months", fontsize=myfontsize)
    ax3.set_xlabel("Duration (h)", fontsize=myfontsize)
    ax3.axvline(x = 7.5, color = 'grey', linestyle='--')
    #ax3.set_title('(c) Difference between bias-corrected and original WRF data', fontsize=myfontsize)
    ax3.set_title('(c) Difference between (b) and (a)', fontsize=myfontsize)
    ax3.set_yticklabels(yticks, rotation=0)

    # We change the fontsize of minor ticks label
    ax1.tick_params(axis='both', which='major', labelsize=myfontsize)
    ax1.tick_params(axis='both', which='minor', labelsize=myfontsize)
    ax2.tick_params(axis='both', which='major', labelsize=myfontsize)
    ax2.tick_params(axis='both', which='minor', labelsize=myfontsize)
    ax3.tick_params(axis='both', which='major', labelsize=myfontsize)
    ax3.tick_params(axis='both', which='minor', labelsize=myfontsize)

    # Colorbar tick
    # use matplotlib.colorbar.Colorbar object
    cbar = s1.collections[0].colorbar
    # here set the labelsize by 20
    cbar.ax.tick_params(labelsize=myfontsize)

    cbar = s2.collections[0].colorbar
    cbar.ax.tick_params(labelsize=myfontsize)
    cbar = s3.collections[0].colorbar
    cbar.ax.tick_params(labelsize=myfontsize)

    plt.savefig(pngfile,dpi=dpi)
    plt.close()
#
# ============================================================= #
#
# Main game (07 from Napoleon Hill)
#

# Get arguments
stalist, indir, outdir = get_argument()

# Read station information
sta = read_stationinfo(stalist)

# Read data
org = np.zeros((nduration,len(months)))
bc = np.zeros((nduration,len(months)))

for i in np.arange(len(sta)) :
    for j in np.arange(len(months)) :

        fl=str(indir)+'dts_'+str(sta[i])+'_'+str(months[j])+'.csv'
        tmp = read_dts_output(fl)

        org[:,j] = org[:,j] + tmp['DTS_before'].values
        bc[:,j] = bc[:,j] + tmp['DTS_after'].values

# Plot data
outfile=str(outdir)+'DTS.png'
# Keep this order of variables 
# as the titles are not flexible in the plotting function
plot_heatmap(org,bc,outfile,600)
#
# ============================================================= #
#
# C'est fin !
#
# ============================================================= #
