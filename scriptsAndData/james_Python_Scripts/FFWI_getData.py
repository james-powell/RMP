# ~u1269218/anaconda3/bin/python3.7 

"""
Author  : James Powell
Date    : 6/11/2020
Purpose : Script to download RH, wind, & temp data to calculate the 
          six hour running avg and save that data
Editing : 
"""
#---------------------------------------------------------------------------#
# Import modules
import csv                            # Allows us to save data as csv 
import urllib.request                 # urllib is a module to download 
                                      # data via URL internet links
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt       # Plot data
import os.path
from os import path
import json
import pandas as pd
import calendar
import sys
import time
#---------------------------------------------------------------------------#
# global variables
filePath = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData'
#filePath = 'C:/Users/u1269218/Documents/Mesowest/RockyMtnPowerStudy'
token = 'c03c614370e24a89a2f73d2e2cd80fa8'

## Set the historical data time range to check (note that Synoptic Data archives start Jan 1997)
apitimestart = '199701010000'

# Set the time to be 12 hours before to make sure Synoptic has the data
today = datetime.today()
apitimeend = datetime.strftime(today, format='%Y%m%d%H%M')
print('apitimeend: ', apitimeend, '\n')


## Set Script Timezone to GMT for ease of use
os.environ['TZ'] = 'Etc/Greenwich'
time.tzset()

# Get the station that is passed in
mystnin = sys.argv[1]
#mystnin = 'PC016'

# Lets call the data
apiurl = 'http://api.synopticdata.com/v2/stations/timeseries?token=%s&units=english,speed|mph,temp|f&start=%s&end=%s&obtimezone=utc&stid=%s&vars=air_temp,relative_humidity,wind_speed'	%(token, apitimestart, apitimeend, str(mystnin))
print('now calling the api: ', apiurl)
getreq  = urllib.request.urlopen(apiurl)
getdata = getreq.read()
getreq.close()
thisjson = json.loads(getdata)

#---------------------------------------------------------------------------#
# Move on to anaylze the data and compute the FFWI for each data point

# get the time in a pandas datetime object
initialTime = np.array(thisjson['STATION'][0]['OBSERVATIONS']['date_time'])
# List for the dates as datetime objects
time_dt = pd.to_datetime(thisjson['STATION'][0]['OBSERVATIONS']['date_time'], format= '%Y-%m-%dT%H:%M:%SZ')

# Need the dates in epoch time to iterate through and search for values
myepoch = []
for x in initialTime:
    myepoch.append(int(calendar.timegm(time.strptime(x,'%Y-%m-%dT%H:%M:%SZ'))))
# Put it in a numpy array so we can use np.where
myepoch = np.array(myepoch)



# Get the other information in these lists
airTemp   = np.array(thisjson['STATION'][0]['OBSERVATIONS']['air_temp_set_1'], dtype=np.float64)
RH        = np.array(thisjson['STATION'][0]['OBSERVATIONS']['relative_humidity_set_1'], dtype=np.float64)
windSpeed = np.array(thisjson['STATION'][0]['OBSERVATIONS']['wind_speed_set_1'], dtype=np.float64)
print(RH)

#---------------------------------------------------------------------------#
# computeFFWI: This will compute the Fosberg Fire Weather Index
# For more info see
# https://a.atmos.washington.edu/wrfrt/descript/definitions/fosbergindex.html
#---------------------------------------------------------------------------#
def computeFFWI(rh, temp, u):

    # First compute m (moisture content variable)
    if rh <= 10:
        m = 0.03229 + 0.281073*rh - 0.000578*rh*temp
    elif 10 < rh and rh <= 50:
        m = 2.22749 + 0.160107*rh - 0.01478*temp
    else:
        m=21.0606 + 0.005565*rh**2 - 0.00035*rh*temp - 0.483199*rh

    # Find the value of n
    n = 1.0 - 2.0*(m/30.0) + 1.5*(m/30.0)**2.0 - 0.5*(m/30.0)**3.0
    # find FFWI
    ffwi = n*((1.0 + u**2.0)**.5)/0.3002
    return(ffwi)


## loop through the data to compute the FFWI
#declare variables
i = 0
FFWI = []
# Lets calculate some data
print('Computing the FFWI for each data point')
while i < len(time_dt):
    FFWI.append(computeFFWI(RH[i],airTemp[i], windSpeed[i]) )
    i += 1

#### NEXT PART OF CODE ####
## SIX HOUR RUNNING MEAN ##
# Create empty array to store the 6hr running mean in for later
running6FFWI = []
runTime      = []

# Since we are calculating the six hour running mean we have to start
# 6 Hrs from the time the data starts to get the last 6 hr running mean
after6Hrs = myepoch[0] + 21600
result = np.where(myepoch >= after6Hrs)[0]

#print('result: ', result[0])

# set i to start six hours after the begining of the data set
i = result[0]
count = 0

print('Now starting to compute the 6Hr mean...\n    This takes a while....')
while i != len(myepoch):
    # This will get the time six hours before the iteration
    before6Hrs = myepoch[i] - 21600
    startIndex = np.where(myepoch >= before6Hrs)[0]
    #print(time_dt[startIndex[0]], '        ', time_dt[i])        

    try:
        # np.where returns a tuple we want just the value for the index
        startIndex = startIndex[0]
        # Now we know the range of index to find the avg of
        # np.nanmean excludes nan which could present a problem if there is many in a row not just one
        running6FFWI.append(np.nanmean(FFWI[startIndex:i]))
        runTime.append(time_dt[i])
    except:
        count += 1
    i += 1


# this puts the time frames in a new array     
data = np.concatenate([[runTime],[running6FFWI]])


print('Now saving the file:   %s/dataFiles/FFWI_data/%s_6HR_Running_Mean1.csv' %(filePath, mystnin))
# This part will save the data array that is filled with the timeframes to a new csv file
np.savetxt('%s/dataFiles/FFWI_data/%s_6HR_Running_Mean.csv' %(filePath, mystnin), 
        data.T, fmt='%s', delimiter=',', 
        header=('Time UTC, 6Hr Running Mean'), comments='')

sys.exit()