# ~u1269218/anaconda3/bin/python3.7 

"""
Author  : James Powell
Date    : 6/12/2020
Purpose : This script will compute the daily climatolgical percentile at a 
          certain day and output a file of the percentiles for each day
Editing : 
"""
#---------------------------------------------------------------------------#
# Import modules
import csv                                  # Allows us to save data as csv 
import urllib.request                       # urllib is a module to download 
                                            # data via URL internet links
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt             # Plot data
import os.path
from os import path
import json
import pandas as pd
import calendar
import time
import sys
#---------------------------------------------------------------------------#

# Global variables
#filePath = 'C:/Users/u1269218/Documents/Mesowest/RockyMtnPowerStudy'
filePath = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData'

# Get the station that is passed in
mystnin = sys.argv[1]
#mystnin = 'UT3'

## Set Script Timezone to GMT for ease of use
os.environ['TZ'] = 'Etc/Greenwich'
time.tzset()

# Create an array that will serve as our days for the entire year. format MMDD
days = []
iterTime = datetime(year=2020, month=1, day=1)
# This will loop through each day and append the day in correct format to the array days
while str(iterTime.year) != '2021':
    if len(str(iterTime.month)) == 1:
        str_month = '0' + str(iterTime.month)
    else:
        str_month = str(iterTime.month)
    if len(str(iterTime.day)) == 1:
        str_day = '0' + str(iterTime.day)
    else:
        str_day = str(iterTime.day)
    day = str_month + str_day

    days.append(day)
    iterTime = iterTime + timedelta(days=1)


# This is te percentile list that we want to find
mypcts = np.arange(5.,100.,5.)
mypctsmore = np.array([0.,0.5,1.,99.,99.5,100.])
percentileList = np.concatenate((mypcts,mypctsmore))
# Sorts the list and puts it in order
percentileList.sort(kind='mergesort')


# The final data will go here 
stnPerc = {}

# Read in the data
# Get the right file path to the data and call that variable csvFile
csvFile = "%s/dataFiles/FFWI_data/%s_6HR_Running_Mean.csv" % (filePath, mystnin )
print("Checking to see if %s exists..."  % (csvFile))

# Check to see if the file exists
fileExist = os.path.exists(csvFile)
if fileExist == True:
    print("Path Exists, moving to analyzing data")
    
    ### Get the information from the csvFile and store it according to its columns that we want
    string_time = np.genfromtxt(csvFile, delimiter = ",", skip_header = 1, usecols = 0, dtype=str  )
    FFWI        = np.genfromtxt(csvFile, delimiter = ",", skip_header = 1, usecols = 1, dtype=float)

    # Get the string dates in the format MMDD
    long_time  = pd.to_datetime(string_time, format= '%Y-%m-%d %H:%M:%S')
    time1 = long_time.strftime('%m%d')

    print('Now calculating the percentiles for %s \n   This takes a while....' %(mystnin))
    # Iterate through the days (MMDD), then calc the percentiles
    iterYear1 = datetime(2020,1, 1)

    for day in days:
        epochDate = int(iterYear1.timestamp())
        ### Get the +- 5 days in epoch time so it will account for normal date problems ###
        epochList = np.arange((epochDate-5*86400), (epochDate+6*86400), 86400)

        #create empty list
        plusMinus5Days = []
        # go through the list and turn each item back into a string in the format MMDD
        for epochTime in epochList:
            plusMinus5Days.append(datetime.fromtimestamp(epochTime).strftime('%m%d'))
        #print('plusMinus5Days:  ', plusMinus5Days)

        ### Find the indices where the days are in for the FFWI ### 
        find = []
        # find is an array of all the index's that corelate with values of that day
        for period in plusMinus5Days:
            #np.flatnonzero is used here instead of np.where becasue we wanted a list not an array of index's
            find.extend(np.flatnonzero(time1 == period))

        # Do not really need this but it is nice to have all the indices in order
        find.sort()

        ### Calculate the percentiles for each given day with +- 5 days ###
        stnPerc[day] = {}
        for perc in percentileList:
            # calculate the percentiles
            mypctout = np.nanpercentile(FFWI[find],perc)
            stnPerc[day][perc] = mypctout
        
        # Go to the next day
        iterYear1 = iterYear1 + timedelta(hours = 24)


    # Now save the file
    # this code was taken from Alex's script for compute_percentiles that way both have the dame format

    print( 'Moving on to save the file: ', '%s/dataFiles/percentiles/%s_percentiles_FFWI_set_1.csv' % (filePath, mystnin))
    outhandle = open('%s/dataFiles/percentiles/%s_percentiles_FFWI.csv' % (filePath, mystnin),'w')
    outheader = 'MODY,'		
    outpcts = sorted(percentileList)		
    for outpct in outpcts:
        outheader = outheader+("%.2f" % outpct)+','
    outhandle.write(outheader+"\n")
    for mydy in sorted(days):
        outline = mydy+','
        for outpct in outpcts:
            outline = outline+("%.3f" % stnPerc[mydy][outpct])+','
        outhandle.write(outline+"\n")
    outhandle.close()

else:
    print('File Does not exist moving on to analyse the next file')
    
sys.exit()