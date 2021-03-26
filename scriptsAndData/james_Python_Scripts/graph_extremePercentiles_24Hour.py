# ~u1269218/anaconda3/bin/python3.7 

"""
Author  : James Powell
Date    : 6/19/2020
Purpose : Script to download RH & wind. To make graphs for the last 24
           Hours for RH, wind speed and gust, and FFWI for many stations
           Also set up to send emails when a station is no longer repor-
           ting data and when a station is back up and running
Editing : 9/18/20 This script is ready to run on a chron task to update 
                  every hour by itself. The saved product is the png files
"""
#----------------------------------------------------------------------#
# Import modules
import csv                            # Allows us to save data as csv 
import urllib.request                 # urllib is a module to download 
                                      # data via URL internet links
from datetime import datetime, timedelta, timezone
import numpy as np
import matplotlib.pyplot as plt       # Plot data
import os.path
from os import path
import json
import pandas as pd
import calendar
import time
from graph_extremePercentiles_KBDI import sendEmail

import cgitb                          # For sending error emails
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# get_stn_last24Hr: Pass in a station and it gets the last 30hours. 
#                   It does 30 hrs instead of 24 to just make sure we have 
#                   enough data for the FFWI 6 hour average
#-----------------------------------------------------------------------------#
def get_stn_last24Hr(stn):
    url = 'https://api.synopticdata.com/v2/stations/timeseries?&token=%s&units=english,speed|mph,temp|f&obtimezone=utc&vars=relative_humidity,wind_speed,wind_gust,peak_wind_speed,air_temp&output=json&stid=%s&recent=1800' % (token, stn )
    response = urllib.request.urlopen(url)
    jsn_data = json.loads(response.read())
    return(jsn_data)

#-----------------------------------------------------------------------------#
# pull_vars_fromJSON: This passes in a json file from the api call and gets 
#                     all the variables in an array either np or pd 
#-----------------------------------------------------------------------------#
def pull_vars_fromJSON(json_data):
     ### Get Data that we need
    # This gets the time and converts it to a pandas dateTime object
    initialTime = np.array(json_data['STATION'][0]['OBSERVATIONS']['date_time'])
    dt     = pd.to_datetime(initialTime, format= '%Y-%m-%dT%H:%M:%SZ')

    # Need the dates in epoch time to iterate through and search for values
    epoch = []
    for x in initialTime:
        epoch.append(int(calendar.timegm(time.strptime(x,'%Y-%m-%dT%H:%M:%SZ'))))
    # Put it in a numpy array so we can use np.where
    epoch = np.array(epoch)

    ### Get the other infornation in these lists
    # Get rh
    try:
        rh =  np.array(json_data['STATION'][0]['OBSERVATIONS']['relative_humidity_set_1'], dtype=np.float64)
    except Exception:
        print('ERROR: no data for rh')
    # Get Wind Speed
    try:
        wind_speed = np.array(json_data['STATION'][0]['OBSERVATIONS']['wind_speed_set_1'], dtype=np.float64)
    except Exception:
        print('ERROR: no data for Wind Speed')
    # Get Air Temp
    try:
        air_temp = np.array(json_data['STATION'][0]['OBSERVATIONS']['air_temp_set_1'], dtype=np.float64) 
    except Exception:
        print('ERROR: no data for Air Temp')
    # This section gets the max_wind. It needs many exceptions to account for different reporting errors
    # since some stations report peakwind_speed and other do not
    max_wind  = []
    try:
            wind_gust = np.array(json_data['STATION'][0]['OBSERVATIONS']['wind_gust_set_1'], dtype=np.float64)
    except Exception:
        print('ERROR: no data for Wind Gust' )
        wind_gust = 0
    try:
        peakwind_speed = np.array(json_data['STATION'][0]['OBSERVATIONS']['peak_wind_speed_set_1'], dtype=np.float64)
        
        # This finds which value is greater to get the real max wind for the time. If no peak wind speed is reported wind gust will be the max wind
        i = 0
        while i < len(wind_gust):
            #print(i)
            if wind_gust[i] >= peakwind_speed[i]:
                max_wind.append(wind_gust[i])
            else:
                max_wind.append(peakwind_speed[i])
            i+=1
    except Exception:
        print('no data for peakwind_speed' )
        peakwind_speed = 0
        max_wind = wind_gust
    
    return(dt, epoch, rh, wind_speed, air_temp, max_wind)

#-----------------------------------------------------------------------------#
# computeFFWI: This will compute the Fosberg Fire Weather Index
# For more info see
# https://a.atmos.washington.edu/wrfrt/descript/definitions/fosbergindex.html
#-----------------------------------------------------------------------------#
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

#-----------------------------------------------------------------------------#
# compute_FFWI6: This computes the 6hr rolling average of the FFWI 
#-----------------------------------------------------------------------------#
def compute_FFWI6(epoch, ffwi):
    # Create empty array to store the 6hr running mean in for later
    runningFFWI6 = []
    run_time      = []

    # Since we are calculating the six hour running mean we have to start
    # 6 Hrs from the time the data starts to get the last 6 hr running mean
    after6Hrs = myepoch[0] + 21600
    result = np.where(myepoch >= after6Hrs)[0]

    # set i to start six hours after the begining of the data set
    i = result[0]
    count = 0

    #print('Now starting to compute the 6Hr mean for FFWI')
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
            runningFFWI6.append(np.nanmean(ffwi[startIndex:i]))
            run_time.append(time_dt[i])
        except Exception:
            count += 1
        i += 1

    return(runningFFWI6, run_time)

#-----------------------------------------------------------------------------#
# get_perc_info: This will pass in a station and get the appropriate percentile
#                data for the station
#-----------------------------------------------------------------------------#
def get_perc_info(stn_dic, stn):
    # This if statement is so that if the station is a Pacificorp then it grabs the percentile data not from the PC station but the
    # one close to in in the compareDir
    #if station[0:3] == 'PC0' or station[0:2] == 'P0':
    if stn in compareDir:
        ## tHIS SECTION GETS THE DATA FOR THE 95TH PERCENTILE
        # Read in the data for the 95th percentile and the 5th so we can plot it
        RH5perc         = pd.read_csv('%s/dataFiles/percentiles/%s_percentiles_relative_humidity_set_1.csv' % (filePath, compareDir[station]),usecols=(0,4) , skiprows=[60], dtype = str)
        windSpeed95perc = pd.read_csv('%s/dataFiles/percentiles/%s_percentiles_wind_speed_set_1.csv' % (filePath, compareDir[station]),       usecols=(0,22), skiprows=[60], dtype = str)
        windGust95perc  = pd.read_csv('%s/dataFiles/percentiles/%s_percentiles_wind_gust_set_1.csv' % (filePath, compareDir[station]),        usecols=(0,22), skiprows=[60], dtype = str)
        FFWI95perc      = pd.read_csv('%s/dataFiles/percentiles/%s_percentiles_FFWI.csv' % (filePath, compareDir[station]),                   usecols=(0,22), skiprows=[60], dtype = str)

        print('Using __%s__ station climo for %s  '%(compareDir[station], station))

    # Just grab the stations percentile list
    else:
        ## tHIS SECTION GETS THE DATA FOR THE 95TH PERCENTILE
        # Read in the data for the 95th percentile and the 5th so we can plot it
        RH5perc         = pd.read_csv('%s/dataFiles/percentiles/%s_percentiles_relative_humidity_set_1.csv' % (filePath, station),usecols=(0,4) , skiprows=[60], dtype = str)
        windSpeed95perc = pd.read_csv('%s/dataFiles/percentiles/%s_percentiles_wind_speed_set_1.csv' % (filePath, station),       usecols=(0,22), skiprows=[60], dtype = str)
        windGust95perc  = pd.read_csv('%s/dataFiles/percentiles/%s_percentiles_wind_gust_set_1.csv' % (filePath, station),        usecols=(0,22), skiprows=[60], dtype = str)
        FFWI95perc      = pd.read_csv('%s/dataFiles/percentiles/%s_percentiles_FFWI.csv' % (filePath, station),                   usecols=(0,22), skiprows=[60], dtype = str)

    #print(FFWI95perc)
    percentile_list = [RH5perc, windSpeed95perc, windGust95perc, FFWI95perc]
    
    return(percentile_list)

#-----------------------------------------------------------------------------#
# organize_Perc: This takes the percentile dates in format MMDD and puts 
#                them in a format compatabile with datetime objects It also
#                reorganizes the percentile values accordingly
#-----------------------------------------------------------------------------#
def organize_Perc(final_date, perc_df, perc_name):
    # Get the final_date in a format to compare to the MMDD format
    final_date_str = '{:02d}'.format(final_date.month) + '{:02d}'.format(final_date.day)
    
    perc_values1 = []
    perc_values2 = []
    perc_dates1  = []
    perc_dates2  = []

    i = 0
    ctr = 0
    # This loop will go thorugh each day
    while i < len(perc_df['MODY']):
        #if perc_df['MODY'][i] == '0229':
        #    i += 1

        # check if its before the end date then its still this year
        if ctr == 0:
            # If we have passed today then set ctr to 1
            if str(perc_df['MODY'][i]) == final_date_str:
                ctr = 1

            # add the year and hour to each date
            perc_dates1.append(str(final_date.year) + perc_df["MODY"][i] + ' 120000')
            # get the percnetile value in the correct list
            perc_values1.append(perc_df[perc_name][i])

        # need to run this normally one more time
        elif ctr == 1:
            perc_dates1.append(str(final_date.year) + perc_df["MODY"][i] + ' 120000')
            # get the percnetile value in the correct list
            perc_values1.append(perc_df[perc_name][i])
            ctr +=1
        # if we have passed today then the rest of the dates should be last year
        else:
            # add the year and hour to each date
            perc_dates2.append(str(final_date.year - 1) + perc_df["MODY"][i] + ' 120000')
            # get the percnetile value in the correct list
            perc_values2.append(perc_df[perc_name][i])

        i += 1

    # Combine the percentile values in the right order last year and then this years
    perc_dates  = perc_dates2 + perc_dates1
    perc_values = perc_values2 + perc_values1
    #print('len(perc_dates): ',  len(perc_dates ))
    #print('len(perc_values): ', len(perc_values))
    return(perc_dates, perc_values)


# set global variables
filePath = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData'
# This is James Powells API token
token = 'c03c614370e24a89a2f73d2e2cd80fa8'
# we are excluding 'BHCU1' since it stopped reporting last winter    
stations = ["KSLC", "UT5", "UT3", "KIJ", "UTJUN","BHCU1", "UTHEB", "KHCR", "PGRU1", "KCDC", "UTBLK", "LPRU1", "UTLGP", "BBN", "KHIF",
            "PC010", "PC016", "PC018", "PC021", "PC022", "PC023", "PC024", "PC025", "PC032", "PC033", "PC034", 'PC053', 'PC054', 'PC058', 'PC059',
            # Thses stations will be added at some point but need a station to compare it too:  ['P056C', 'P057C','PC055','PC056','PC057','PC060',]
            # These following stations are only used to compare and or are on the other mesowest stations page
            'UTASG', 'PCPD', 'UTMFS', 'UTSTR', 'UTPLC', 'UTPCY', 'UTSVC', 'MTMET', 'HERUT', 'UT9' ]


# Since the PC* stations do not have a long enough record to compare the variables we will 
# use these other stations that are near them to compare too.
compareDir = {
    "PC010": 'UTASG',    "PC016": 'KCDC', 
    "PC018": 'PCPD' ,    "PC021": 'UT5', 
    "PC022": 'UT3'  ,    "PC023": 'UTMFS', 
    "PC024": 'KHCR' ,    "PC025": 'UTSTR', 
    "PC032": 'UT3'  ,    "PC033": 'UTPLC', 
    "PC034": 'UTPCY',    
    #"P056C": 'UTSVC',    "P057C": 'MTMET',   #Moved sometime and now dont have any stations close that are similar climatologically
    "PC053": 'UTBLK',    "PC054": 'BHCU1',    #Added 10/13/2020 
    "PC058": 'MTMET',    "PC059": 'UTSVC',    #Added 11/06/2020
}

for station in stations:
    print('______________________STARTING WITH STATION: %s______________________________________' % (station))
    
    ### This is an error list text document
    # It holds a list of stations that are not reporting for use in sending automatic emails regarding 
    # the status of stations
    f = open("%s/james_Python_Scripts/errorFiles/graph_24Hr_errorStns.txt" %(filePath), "r")
    errorFileString = f.read()

    # if one station throws an error proceed to the next station
    try:

        endDate   = datetime.today()
        # This calls the api and gets the data needed
        stationData = get_stn_last24Hr(station)
        # This pulls the data and puts it in easier to manipulate formats
        time_dt, myepoch, RH, windSpeed, airTemp, maxWind = pull_vars_fromJSON(stationData)

        # Lets get the FFWI
        FFWI    = []
        x = 0
        # Compute the FFWI for every data point
        while x < len(time_dt):
            FFWI.append(computeFFWI(RH[x], airTemp[x], windSpeed[x]))
            x += 1

        #-----------------------------------------------------------------------------#
        # NEED TO COMPUTE THE 6 HOUR RUNNING MEAN FOR FFWI
        #-----------------------------------------------------------------------------#

        running6FFWI, runTime = compute_FFWI6(myepoch, FFWI)

        ## Have to make this list a numpy array 
        running6FFWI = np.array(running6FFWI)
        # Make this a series so that we can use index's to call sections from it
        runTime = pd.Series(runTime)

        # Initialize  variable lists to plot the data and the date
        varList      = [ RH, windSpeed, maxWind, running6FFWI]
        varListNames = [ 'Relative Humidity', 'Wind Speed', 'Max Wind Speed', 'FFWI']
        varFileNames = [ 'relative_humidity', 'wind_speed', 'wind_gust', 'FFWI'] 
        threshold    = [  20,                  20,           30,          30   ]

        # Get the startTime for the graph 24 hours before the current hour
        startTimeGraph = endDate - timedelta(hours = 24)

        #-----------------------------------------------------------------------------#
        ## THIS SECTION GETS THE PERCENTILE DATA 
        
        percentileList = get_perc_info( compareDir, station )

        # Loops through the percentile data to put them in a datetime and float objects
        for var, varFileName in zip(percentileList,varFileNames):
            
            if str(varFileName) == 'relative_humidity':
                # This will get the date and percentile info in the right format
                var['MODY'], var['5.00'] = organize_Perc(endDate, var, '5.00')
                var['5.00'] = pd.to_numeric(var['5.00'])
            else:
                # This will get the date and percentile info in the right format
                var['MODY'], var['95.00'] = organize_Perc(endDate, var, '95.00')
                var['95.00'] = pd.to_numeric(var['95.00'])

            var['MODY'] = pd.to_datetime(var['MODY'], format='%Y%m%d %H%M%S')
        
        #-----------------------------------------------------------------------------#
        ### NEXT PART OF THE CODE ###
        ### This section will plot the data for each variable and save the graph
        # This converts the time to MST we do not account for times when it will be 
        # daylight savings since this is only meant to be used in the summer
        runTime = runTime - timedelta(hours=6)
        time_dt = time_dt - timedelta(hours=6)


        ## Plot the Data
        # This will go through the variables and make a plot for each
        for y, varName, fileName, thres, perc in zip(varList, varListNames, varFileNames, threshold, percentileList):          
            try:
                # Wind Speed
                fig, ax = plt.subplots()
                #get the right data set for y axis
                dataUpper = y >  thres
                dataLower = y <= thres
                
                # Plot info for RH
                if varName == 'Relative Humidity':
                    # This plots the y with a different color if the values exceed the threshold
                    ax.scatter( time_dt[dataLower], y[dataLower], color = 'indianred', s = 10, label = 'Data under Threshold')
                    ax.scatter(time_dt[dataUpper], y[dataUpper],  s =10, label = 'Data')
                    ax.axhline(thres, color='red', lw=2, alpha=0.7, label = 'Threshold (' + str(thres) + ')')
                    
                    # Dont want to plot these values for certain stations
                    if station == 'PC010' or station == 'PC018':
                        print(' Not plotting RH 5th percentile for this station becasue the percentile is not representitive')
                    else:
                        # this is for the extreme percentile values            
                        ax.plot(perc['MODY'], perc['5.00'], color='orange', linestyle = '--', label='5th Percentile')

                    ax.set_ylabel( '%s' %(varName))

                # Plot info for FFWI
                elif varName == 'FFWI':
                    # This plots the y with a different color if the values exceed the threshold
                    ax.scatter(runTime[dataLower], y[dataLower], s = 8, label = '%s Data' % (varName))
                    ax.scatter(runTime[dataUpper], y[dataUpper], color = 'indianred', s =8, label = 'Data over Threshold')
                    ax.axhline(thres, color='red', lw=2, alpha=0.7, label = 'Threshold (' + str(thres) + ')')

                    # Dont want to plot these values for certain stations
                    if station == 'PC010' or station == 'PC018':
                        print(' Not plotting FFWI 95th percentile for this station becasue the percentile is not representitive')
                    else:
                        # this is for the extreme percentile values
                        ax.plot(perc['MODY'], perc['95.00'], color='orange', linestyle = '--', label='95th Percentile')

                    ax.set_ylabel( '%s' %(varName))

                # Plot info for wind speed and wind gust
                else:    
                    # This plots the y with a different color if the values exceed the threshold
                    ax.scatter( time_dt[dataLower], y[dataLower], s = 10, label = '%s Data' % (varName))
                    ax.scatter(time_dt[dataUpper], y[dataUpper], color = 'indianred', s =10, label = 'Data over Threshold')
                    ax.axhline(thres, color='red', lw=2, alpha=0.5, label = 'Threshold (' + str(thres) + ')')
                            
                    # Dont want to plot these values for certain stations
                    if station == 'PC010' or station == 'PC018':
                        print(' Not plotting wind speed or Gust 95th percentile for this station becasue the percentile is not representitive')
                    elif varName == 'Wind Speed':
                        ax.plot(perc['MODY'], perc['95.00'], color='orange', linestyle = '--', label='95th Percentile')

                    else:
                        # this is for the extreme percentile values
                        ax.plot(perc['MODY'], perc['95.00'], color='orange', linestyle = '--', label='95th Percentile')

                    ax.set_ylabel( '%s (mph)' %(varName))

                # Setup for all variables of the graph
                ax.set_xlabel( 'Month-Day Hour (Local Time)')
                ax.set_title('%s %s Extreme Events For The Last 24 Hours' %(station, varName) )            
                ax.set_xlim( xmin=startTimeGraph, xmax=endDate)

                lgd = ax.legend(loc='upper center', bbox_to_anchor=(.5,1.28), ncol=4, shadow = True)#, fancybox=True, shadow=True)

                fig.figsize=(8,8)
                plt.gcf().autofmt_xdate()
                plt.grid(True, axis='y')

                fig.savefig('%s/pngFiles/extremePercentilePics/%s_Extreme_%s_24Hrs.png' % (filePath, station, fileName),  bbox_extra_artists=(lgd,), bbox_inches='tight')
                #print('Saving the figure: /%s_Extreme_%s_24Hrs.png' % ( station, fileName))
                plt.close('all')

            except Exception:                       
                    print('---------------------------------------------------------------------------------------')
                    print('\tFOR WHATEVER REASON COULDN\'T GRAPH %s FOR %s ' %(varName, station))
                    print('---------------------------------------------------------------------------------------')

        ### if this is the first time one of the stations has ran after not having any data
        ### clear it from the error list
        if errorFileString.find(station) != -1:
            print('Station was in error list, Removing it now from the list')
            # send email saying the station is reporting again
            email_subject = "%s, RMP station running again" %(station)
            email_body = """%s is now reporting data,
            graph_extremePercentiles_24Hour.py will continue running it.
            
            Please contact James Powell if you have any questions at u1269218@utah.edu.

            -Pointer Bot""" %(station)

            #sendEmail(email_body, email_subject)

            # now remove this station from the error station list
            errorFileString = errorFileString.replace(station + '\n', '')
            # now write the new string to the txt file
            with open("%s/james_Python_Scripts/errorFiles/graph_24Hr_errorStns.txt" %(filePath),'w') as f:
                f.write(errorFileString)

        print('_______________________________________________________________________________________\n\n\n')

    # If a station is not reporting than it will send an email telling a station is down
    except Exception:
        print('--ERROR with station %s, moving on to the next station' %(station))
        
        # This is to check if the station is already on the station error file list
        if errorFileString.find(station) != -1:
            print('The station is already in the Error File list so it will not send an email')

        # If this is the first time it has not reported then write that station to the error list
        # and send out an email saying so
        else:
            print('This station is not in the error file list, it will be added now')
            # This appends this station to the end of the list
            with open("%s/james_Python_Scripts/errorFiles/graph_24Hr_errorStns.txt" %(filePath),'a') as f:
                f.write(station + '\n')
            
            # Subject and message body delcarations
            email_subject = "%s, RMP code error" %(station)
            email_body = """%s is no longer reporting data,
            graph_extremePercentiles_24Hour.py is skipping it.

            For more information see https://mesowest.utah.edu/cgi-bin/droman/meso_base_dyn.cgi?stn=%s
            
            Please contact James Powell if you have any questions at u1269218@utah.edu.

            -Pointer Bot""" %(station,station)
            # Turning this off for the winter, it will still update the error file
            #sendEmail(email_body, email_subject)
    

    f.close()
