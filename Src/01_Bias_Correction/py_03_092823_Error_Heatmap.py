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
nstation=74
#
ifbefore=True
ifafter=True
ifdiff=True
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
def plot_heatmap_percent(a,b,c,total,pngfile,dpi,clor,low,high) :

    yticks=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    xticks=['' for i in np.arange(24)]
    xticks[0]='3h'
    #i=7 ; j=i*3+3
    xticks[7]='24h'
    xticks[15]='48h'
    xticks[-1]='72h'

    myfontsize=18

    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, figsize=(8,15))

    fig.suptitle('ECDF two-sample test statistics', fontsize=myfontsize)

    aa = 100*a/total
    s1 = sns.heatmap(aa.T, ax=ax1, vmin=low, vmax=high, cmap=clor)
    ax1.set_ylabel("Months", fontsize=myfontsize)
    ax1.axvline(x = 7.5, color = 'grey', linestyle='--')
    ax1.set_title('(a) Kolmogorov Smirnov test', fontsize=myfontsize)
    ax1.set_yticklabels(yticks, rotation=0)

    bb = 100*b/total
    s2 = sns.heatmap(bb.T, ax=ax2, vmin=low, vmax=high, cmap=clor)
    ax2.set_ylabel("Months", fontsize=myfontsize)
    ax2.axvline(x = 7.5, color = 'grey', linestyle='--')
    ax2.set_title('(b) Cramér–von Mises test', fontsize=myfontsize)
    ax2.set_yticklabels(yticks, rotation=0)

    cc = 100*c/total
    s3 = sns.heatmap(cc.T, ax=ax3, vmin=low, vmax=high, cmap=clor, xticklabels=xticks)
    ax3.set_ylabel("Months", fontsize=myfontsize)
    ax3.set_xlabel("Duration (h)", fontsize=myfontsize)
    ax3.axvline(x = 7.5, color = 'grey', linestyle='--')
    ax3.set_title('(c) DTS test', fontsize=myfontsize)
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

# Before bias-correction
if ifbefore :
    ks_org = np.zeros((nduration,len(months)))
    cvm_org = np.zeros((nduration,len(months)))
    dts_org = np.zeros((nduration,len(months)))

    for i in np.arange(len(sta)) :
        for j in np.arange(len(months)) :
    
            fl=str(indir)+'a5_'+str(sta[i])+'_'+str(months[j])+'.csv'
            tmp = read_dts_output(fl)
            dts_org[:,j] = dts_org[:,j] + tmp['DTS_before'].values
            del tmp
    
            fl=str(indir)+'a6_'+str(sta[i])+'_'+str(months[j])+'.csv'
            tmp = read_dts_output(fl)
            ks_org[:,j] = ks_org[:,j] + tmp['KS_before'].values
            del tmp
    
            fl=str(indir)+'a7_'+str(sta[i])+'_'+str(months[j])+'.csv'
            tmp = read_dts_output(fl)
            cvm_org[:,j] = cvm_org[:,j] + tmp['CVM_before'].values
            del tmp

    # Plot data
    outfile=str(outdir)+'ECDF_Stat_Org.png'
    # Keep this order of variables 
    # as the titles are not flexible in the plotting function
    plot_heatmap_percent(ks_org,cvm_org,dts_org,nstation,outfile,600,'crest',0,100)

# After bias-correction
if ifafter :
    ks_bc = np.zeros((nduration,len(months)))
    cvm_bc = np.zeros((nduration,len(months)))
    dts_bc = np.zeros((nduration,len(months)))

    for i in np.arange(len(sta)) :
        for j in np.arange(len(months)) :
    
            fl=str(indir)+'a5_'+str(sta[i])+'_'+str(months[j])+'.csv'
            tmp = read_dts_output(fl)
            dts_bc[:,j] = dts_bc[:,j] + tmp['DTS_after'].values
            del tmp
    
            fl=str(indir)+'a6_'+str(sta[i])+'_'+str(months[j])+'.csv'
            tmp = read_dts_output(fl)
            ks_bc[:,j] = ks_bc[:,j] + tmp['KS_after'].values
            del tmp
    
            fl=str(indir)+'a7_'+str(sta[i])+'_'+str(months[j])+'.csv'
            tmp = read_dts_output(fl)
            cvm_bc[:,j] = cvm_bc[:,j] + tmp['CVM_after'].values
            del tmp

    # Plot data
    outfile=str(outdir)+'ECDF_Stat_Bc.png'
    # Keep this order of variables 
    # as the titles are not flexible in the plotting function
    plot_heatmap_percent(ks_bc,cvm_bc,dts_bc,nstation,outfile,600,'crest',0,100)

# Difference
if ifdiff :
    if ifbefore and ifafter :
        ks_diff = ks_bc - ks_org
        cvm_diff = cvm_bc - cvm_org
        dts_diff = dts_bc - dts_org

        # Plot data
        outfile=str(outdir)+'ECDF_Stat_Diff.png'
        # Keep this order of variables 
        # as the titles are not flexible in the plotting function
        plot_heatmap_percent(ks_diff,cvm_diff,dts_diff,nstation,outfile,600,'bwr',-100,100)
    else :
        print ("Need True for ifbefore and ifafter !")

#
# ============================================================= #
#
# C'est fin !
#
# ============================================================= #
