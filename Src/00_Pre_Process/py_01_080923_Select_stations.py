#
# Read station info from C-HPD and select only stations
# from U.S. states that you want
# In this case: IL IN OH KY
# But it should work for any other states (plz, help me to test this)
#

# 
# Libraries
#
import pandas as pd
import numpy as np
import argparse

#
# Get arguments
#
def get_argument() :
    parser = argparse.ArgumentParser(description="Get arguments for selecting stations from C-HPD",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    # Keep these options for fun
    parser.add_argument("--ignore-existing", action="store_true", help="skip files that exist")
    parser.add_argument("--exclude", help="files to exclude")
    
    # Using these options indeed 
    parser.add_argument("-i", "--input", help="Input C-HPD file")
    parser.add_argument("-o", "--output", help="Output file for station list")
    parser.add_argument('-s','--states', nargs='+', help="List of U.S. States", required=True)
    
    args = parser.parse_args()
    config = vars(args)
    
    out1=config['input']
    out2=config['output']
    out3=config['states']

    return out1, out2, out3

if __name__ == "__main__" :

    # Read arguments 
    CHPD_file, CSVOUT, states = get_argument()
    print ("Working with :")
    print (CHPD_file)
    print ("Selecting : ",states)

    # Get list of stations belongs to the U.S. States that you want
    df=pd.read_csv(str(CHPD_file))
    df_s=df.loc[ df['State/Province'].isin(states) ] 
    df_s.to_csv(str(CSVOUT))
    print ("Output file: ",CSVOUT)
