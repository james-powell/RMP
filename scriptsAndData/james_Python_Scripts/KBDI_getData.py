# ~u1269218/anaconda3/bin/python3.7 

"""
Author  : James Powell
Date    : 6/24/2020
Purpose : This is a script to download a stations information to find the
          KBDI values for each day and save that data
Editing : 7/7/20 Ready to be put in runMulitpleStations and run 
          automatically
"""
#----------------------------------------------------------------------#
# Import modules
import csv                            # Allows us to save data as csv 
import urllib.request                 # urllib is a module to download 
                                      # data via URL internet links
from   datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt       # Plot data
import os.path
from   os import path
import json
import pandas as pd
import calendar
import time
import sys
#----------------------------------------------------------------------#
# Need to run these stations:
# KSLC, KCDC, PGRU1, LPRU1, KHIF
#----------------------------------------------------------------------#

# set global variables
filePath = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData'
#filePath = 'C:/Users/u1269218/Documents/Mesowest/RockyMtnPowerStudy'

# This is James Powells API token
token = 'c03c614370e24a89a2f73d2e2cd80fa8'
# we are excluding all UDOT stations and BBN due to insufficient records
station = sys.argv[1]
#station = "KHIF"

## Set Script Timezone to GMT for ease of use
os.environ['TZ'] = 'Etc/Greenwich'
time.tzset()

# You have to start the record after a time of heavy rainfall so each 
# station needs a different start time
compareDir = {
    "KSLC":  '201004070000',    "KCDC":  '201003150000',
    "PGRU1": '201004100000',    "LPRU1": '201003160000',
    "KHIF":  '201004070000', 
}
    

# because of synoptic issues we have to call the api in two parts. 
# 2010-2014 and 2015-today
apiStartTimes = [compareDir[station], '201501010000']
apiEndTimes   = ['20141231', datetime.strftime(datetime.today() - timedelta(days=7), '%Y%m%d')]


#############################################################################
############### THIS PART GETS/COMPUTES THE RAIN DATA NEEDED ################
#############################################################################
print('Starting to get/compute the rain data for the Last 10 years for', station)
precip     = []
stringDays = []

# Get the rain data from the two api calls
for begin,end in zip(apiStartTimes, apiEndTimes):
    # call teh API and get the data
    apiurl = 'https://api.synopticdata.com/v2/stations/precipitation?&token=%s&start=%s&end=%s2359&pmode=intervals&interval=day&obtimezone=utc&units=precip|in&stid=%s' % (token, begin, end, station)

    print('now calling the api: ', apiurl)
    getreq  = urllib.request.urlopen(apiurl)
    getdata = getreq.read()
    getreq.close()
    thisjson = json.loads(getdata)

    k = 0
    # This loops through and adds the precip totals and days to the respective lists
    while k < thisjson['STATION'][0]['OBSERVATIONS']['precipitation'][-1]['interval']:
        precip.append(thisjson['STATION'][0]['OBSERVATIONS']['precipitation'][k]['total'])
        stringDays.append(thisjson['STATION'][0]['OBSERVATIONS']['precipitation'][k]['first_report'])
        k += 1


# put precip in numpy array ad the rainDays in a pandas datetime object
precip = np.array(precip)
rainDays = pd.to_datetime(stringDays, format= '%Y-%m-%dT%H:%M:%SZ')

#print('len(precip): ', len(precip))
#print('len(rainDays): ',len(rainDays))

####### Calculate mean annual rain fall for this station for the given ten years ########
annualRainTotals = []
#start at the begining
loopDate = datetime.strptime(apiStartTimes[0], '%Y%m%d%H%M')

# We need this years date since it is not complete we do not want to include it in 
# the total annual rainfall since it is not completely done yet
endYear = datetime.today().year
ctr = 0

while loopDate.year != endYear: 
    #print('\n-------starting new YEAR: %s ------------------------' %(str(rainDays[ctr].year)))

    # empty variable to add each years totals up
    daily_precip_accum = 0

    # add values for that year to this list
    while loopDate.year == rainDays[ctr].year:
        # make sure it is not a null value
        if str(precip[ctr]) != 'None':
            daily_precip_accum += precip[ctr]
        else:
            print('NULL PRECIP VALUE day before ', rainDays[ctr+1].date())
        ctr += 1

        while str(rainDays[ctr]) == 'NaT':
            ctr += 1
            print('NULL DATE VALUE day before ', rainDays[ctr].date())
    
    annualRainTotals.append(daily_precip_accum)
    loopDate += timedelta(days=366)

#print(annualRainTotals)
#print(len(annualRainTotals))

# This is the average of all of the annual total rain falls
R = np.mean(annualRainTotals)
print('R: ',  R)


#############################################################################
################ MOVE ON TO GET THE MAX DAILY TEMPERATURES ##################
#############################################################################

# Call the air Temp data and get 24 hour maximums
apiurl1 = 'http://api.synopticdata.com/v2/stations/timeseries?token='+token+'&units=temp|f&start='+apiStartTimes[0]+'&end='+apiEndTimes[-1] +'2359&obtimezone=utc&stid='+station+'&vars=air_temp'	
print('now calling the api: ', apiurl1)
getreq1  = urllib.request.urlopen(apiurl1)
getdata1 = getreq1.read()
getreq1.close()
tempjson = json.loads(getdata1)


# get the time in a pandas datetime object
initialTime = np.array(tempjson['STATION'][0]['OBSERVATIONS']['date_time'])
# List for the dates as datetime objects
time_dt = pd.to_datetime(tempjson['STATION'][0]['OBSERVATIONS']['date_time'], format= '%Y-%m-%dT%H:%M:%SZ')

# Get the other information in these lists
airTemp   = np.array(tempjson['STATION'][0]['OBSERVATIONS']['air_temp_set_1'], dtype=np.float64)

#print(time_dt, '\n')
#print(airTemp, '\n')
#print('len(time_dt): ', len(time_dt))
#print('len(airTemp): ', len(airTemp))

# find daily Temperature Maximums
i = 0
dailyMaxTemp = []
tempDays = []
iterDate = datetime.strptime(apiStartTimes[0], '%Y%m%d%H%M')

# Loop  get the daily Max temp
while i < len(time_dt):
    # create an empty array to store all the daily values in
    dailyValues = []

    # Iterate through one day.
    while time_dt[i].date() == iterDate.date():
        # add the values from that day to list
        dailyValues.append(airTemp[i])
        
        # check to make sure that i is not passing the len of the list
        if i >= len(time_dt)-1:
            i += 1
            break
        i += 1
    
    if i >= len(time_dt)-1:
        break

    # the KBDI index needs to have a threshold Temp values of 50-110 F
    # Some of synoptics data is messy so we need to do some clean up first
    # drop any values over 110
    dailyValues2 = [T for T in dailyValues if T <= 110]

    # put the max value in the right list
    try:
        dailyMaxTemp.append(np.nanmax(dailyValues2))
        tempDays.append(time_dt[i])
    except:
        print('ERROR: No data for this day ', iterDate.date())
    
    # move it forward to the next day
    iterDate += timedelta(days=1)
    
#print('len(dailyMaxTemp): ', len(dailyMaxTemp))
#print('len(tempDays): ', len(tempDays))


#############################################################################
################# MOVE ON TO COMPUTE THE KBDI INDEX VALUES ##################
#############################################################################
# For more info about computing the KBDI see
# https://www.srs.fs.usda.gov/pubs/rp/rp_se038.pdf

### lists to put the KBDI values in and the dates 
# First date for KBDI index is started at 0
KBDI  = [0]
KBDIdates = [datetime.strptime(apiStartTimes[0], '%Y%m%d%H%M').date()]

# two counter variables for the Temperature and rainfall list
counterT = 1
counterR = 1

# loop to calculate the KBDI index values
while counterR < len(rainDays) and counterT < len(tempDays):
    #print('-tempDays[counterT]: ', tempDays[counterT].date())
    #print('-rainDays[counterR]: ', rainDays[counterR].date())

    # Conditions to make sure that we are on the same date for the temp and rain list
    if tempDays[counterT].date() != rainDays[counterR].date():
        
        ###conditions to take care of NaT values
        while str(tempDays[counterT]) == 'NaT' or str(dailyMaxTemp[counterT]) == 'None':
            counterT += 1

        while str(rainDays[counterR]) == 'NaT' or str(precip[counterR]) == 'None':
            counterR +=1
        
        # if tempDays is sooner or less than the date on raindays than move forward tempDays till it is the same
        while tempDays[counterT].date() < rainDays[counterR].date():
            counterT += 1

        # if tempDays is later or greater than the date on raindays than move forward rainDays till it is the same
        while tempDays[counterT].date() > rainDays[counterR].date():
            counterR += 1
        

        #print('---tempDays[counterT]: ', tempDays[counterT].date())
        #print('---rainDays[counterR]: ', rainDays[counterR].date())

    # add here a condition regarding if a certain number of days have eclipsed raise a flag/ send an email saying KBDI index has faltered

    #### Move on to calculate the KBDI index
    daysBefore = 0

    ### STEP 1 ###
    ## Get the Net Rainfall
    # If the days accumulated rain was not 0 check it
    if precip[counterR] > 0:
        # condition to check if it has rained the days leading up to the iterated day    
        precipBefore = []        
        daysBefore = -1
        while precip[counterR + daysBefore] > 0:
            precipBefore.append(precip[counterR + daysBefore])
            daysBefore -= 1
        #print(daysBefore)

        # if it had not rain before and the precip amount is over 0.2
        if daysBefore == -1 and precip[counterR] > 0.2:
            # then the net rain is the 24 precip minus 0.2
            netRainFall = precip[counterR] - 0.2

        # now we need to take care of the excpetion of if it had been raining for multiple days in a row
        if daysBefore != -1:
            # check if it has already passed the threshold 0.2 
            if np.sum(precipBefore) > 0.2:
                netRainFall = precip[counterR]
            
            # If it has not then try to see if adding the current days precip makes it pass
            else:
                precipBefore.append(precip[counterR])
                
                if np.sum(precipBefore) > 0.2:
                    netRainFall = np.sum(precipBefore) - 0.2
                else:
                    netRainFall = 0

    # if the days accumulated rain was 0 then the netrainfall is 0 
    else:
        netRainFall = 0


    ### STEP 2 ###
    ## subtract yesterdays KBDI value by the net rain fall * 100 to get adjKBDI
    # condition in case the index value yesterday was 0
    adjKBDI = KBDI[-1] - (netRainFall*100)


    ### STEP 3 ###
    ## calculate the drought factor and add that to the adjusted KBDI value to get to
    ## todays KBDI value

    # calculate the Drought Factor
    droughtFactor = ((800-KBDI[-1])* (0.968*np.exp(0.0486*dailyMaxTemp[counterT]) - 8.30) *1 *0.001 )/ (1+10.88*np.exp(-0.0441*R))

    if droughtFactor < 0:
        droughtFactor = 0

    newKBDI = adjKBDI + droughtFactor
    
    # the KBDI index should never go below 0 even if it rains    
    if newKBDI < 0:
        newKBDI = 0

    KBDI.append(newKBDI)
    KBDIdates.append(rainDays[counterR].date())


    print('rainDays[ctrR]: ', rainDays[counterR].date(), '\tprecip[ctrR]: ', precip[counterR],' ', '\tnetRainFall: ', netRainFall, '\tadjKBDI: ', adjKBDI, '\tdroughtFactor: ', droughtFactor, '\tdailyMaxTemp[ctrT]: ', dailyMaxTemp[counterT], '\tnewKBDI: ', KBDI[-1])
    print('-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    counterT += 1
    counterR += 1

"""
fig=plt.figure()
fig.show()
ax=fig.add_subplot(111)

ax.plot(KBDIdates,KBDI_allow_negative_dQ,label='Formula1: allow negative dQ')
ax.plot(KBDIdates,KBDI_dQ_absolute_value,label='Formula2: take the absolute value of dQ')
ax.plot(KBDIdates,KBDI_dQ_set_0, label='Formula3: set negative dQ\'s to 0')
#ax.set_xlim( xmin=datetime(2019,9,20), xmax=datetime(2019,10,15))

lgd = ax.legend(loc='upper center', bbox_to_anchor=(.5,1.2),  #(1.23,1.03)
            ncol=4, shadow = True)#, fancybox=True, shadow=True)

#plt.legend(loc=2)
plt.draw()
fig.savefig('%s/pngFiles/other/%s_KBDI_show_3ways_long.png' %(filePath, station),  bbox_extra_artists=(lgd,), bbox_inches='tight')


# lets fine the average and maximum range of the different values
range_allow_negative_dQ_max = []
range_allow_negative_dQ_min = []
range_dQ_absolute_value_max = []
range_dQ_absolute_value_min = []
range_dQ_set_0_max          = []
range_dQ_set_0_min          = []

rangeList1 = [range_allow_negative_dQ_max, range_dQ_absolute_value_max, range_dQ_set_0_max ]
rangeList2 = [range_allow_negative_dQ_min, range_dQ_absolute_value_min, range_dQ_set_0_min]

# find daily Temperature Maximums
i = 0
iterDate = datetime.strptime(apiStartTimes[0], '%Y%m%d%H%M')

# Loop  get the yearly max and min values
while i < len(KBDIdates):
    # create an empty array to store all the daily values in
    dailyValues_allow_negative_dQ = []
    dailyValues_dQ_absolute_value = []
    dailyValues_dQ_set_0 = []

    # Iterate through one day.
    while KBDIdates[i].year == iterDate.year:
        # add the values from that day to list
        dailyValues_allow_negative_dQ.append(KBDI_allow_negative_dQ[i])
        dailyValues_dQ_absolute_value.append(KBDI_dQ_absolute_value[i])
        dailyValues_dQ_set_0.append(KBDI_dQ_set_0[i])
        
        # check to make sure that i is not passing the len of the list
        if i >= len(KBDIdates)-1:
            i += 1
            break
        i += 1
    
    if i >= len(KBDIdates)-1:
        break

    # put the max value in the right list
    range_allow_negative_dQ_max.append(np.nanmax(dailyValues_allow_negative_dQ))
    range_allow_negative_dQ_min.append(np.nanmin(dailyValues_allow_negative_dQ))
    range_dQ_absolute_value_max.append(np.nanmax(dailyValues_dQ_absolute_value))
    range_dQ_absolute_value_min.append(np.nanmin(dailyValues_dQ_absolute_value))
    range_dQ_set_0_max.append(np.nanmax(dailyValues_dQ_set_0))
    range_dQ_set_0_min.append(np.nanmin(dailyValues_dQ_set_0))
    
    # move it forward to the next day
    iterDate += timedelta(days=366) 


# find the average yearly range
avgRange_allow_negative_dQ_max = np.mean(range_allow_negative_dQ_max)
avgRange_allow_negative_dQ_min = np.mean(range_allow_negative_dQ_min)
avgRange_dQ_absolute_value_max = np.mean(range_dQ_absolute_value_max)
avgRange_dQ_absolute_value_min = np.mean(range_dQ_absolute_value_min)
avgRange_dQ_set_0_max          = np.mean(range_dQ_set_0_max)
avgRange_dQ_set_0_min          = np.mean(range_dQ_set_0_min)


print('allow negative dQ average yearly range    Min:', avgRange_allow_negative_dQ_min,'\tMax:', avgRange_allow_negative_dQ_max)
print('absolute value dQ average yearly range    Min:', avgRange_dQ_absolute_value_min,'\tMax:', avgRange_dQ_absolute_value_max)
print('set negative dQ = 0 average yearly range  Min:', avgRange_dQ_set_0_min,'\tMax:', avgRange_dQ_set_0_max)

# find the maximumn yearly range
Range_allow_negative_dQ_max = np.max(range_allow_negative_dQ_max)
Range_allow_negative_dQ_min = np.min(range_allow_negative_dQ_min)
Range_dQ_absolute_value_max = np.max(range_dQ_absolute_value_max)
Range_dQ_absolute_value_min = np.min(range_dQ_absolute_value_min)
Range_dQ_set_0_max          = np.max(range_dQ_set_0_max)
Range_dQ_set_0_min          = np.min(range_dQ_set_0_min)


print('allow negative dQ maximum yearly range    Min:', Range_allow_negative_dQ_min,'\tMax:', Range_allow_negative_dQ_max)
print('absolute value dQ maximum yearly range    Min:', Range_dQ_absolute_value_min,'\tMax:', Range_dQ_absolute_value_max)
print('set negative dQ = 0 maximum yearly range  Min:', Range_dQ_set_0_min,'\tMax:', Range_dQ_set_0_max)
"""
#############################################################################
################ Lets output the KBDI values to a csv file ##################
#############################################################################

#KBDIdates = pd.to_datetime(KBDIdates)
KBDIdates_string = []
for date in KBDIdates:
    KBDIdates_string.append(datetime.strftime(date, format='%m/%d/%Y'))

# this puts the time frames in a new array     
data = np.concatenate([[KBDIdates_string],[KBDI]])

print('Now saving the file:   %s/dataFiles/KBDI_data/%s_KBDI_daily_values.csv' %(filePath, station))

# This part will save the data array that is filled with the timeframes to a new csv file
np.savetxt('%s/dataFiles/KBDI_data/%s_KBDI_daily_values.csv' %(filePath, station), 
        data.T, fmt='%s', delimiter=',', 
        header=('Time UTC, KBDI values\n anual mean RainFall, %f'%( round(R, 2)) ), comments='')


sys.exit()
