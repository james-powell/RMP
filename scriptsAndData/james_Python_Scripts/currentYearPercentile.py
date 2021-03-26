# ~u1269218/anaconda3/bin/python3.7 

"""
Author  : James Powell
Date    : 6/3/2020
Purpose : Script to download RH and wind data for current year and compute
          daily averages to compare to the climatological percentiles

          This is set up to be run by a cron task every day to update
          crontask is done on Meso3 server
"""
#----------------------------------------------------------------------#
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
#----------------------------------------------------------------------#

#---------------------------------------------------------------------------#
# computeFFWI: This will compute the Fosberg Fire Weather Index
# For more info see
# https://a.atmos.washington.edu/wrfrt/descript/definitions/fosbergindex.html
#---------------------------------------------------------------------------#
def computeFFWI(rh, temp, u):
    # Need the RH to be in decimal form
    rh = rh/100
    # First compute m (moisture content variable)
    if rh <= .10:
        m = 0.03229 + 0.281073*rh - 0.000578*rh*temp
    elif .10 < rh and rh <= .50:
        m = 2.22749 + 0.160107*rh - 0.01478*temp
    else:
        m=21.0606 + 0.005565*rh**2 - 0.00035*rh*temp - 0.483199*rh

    # Find the value of n
    n = 1.0 - 2.0*(m/30.0) + 1.5*(m/30.0)**2.0 - 0.5*(m/30.0)**3.0
    # find FFWI
    ffwi = n*((1.0 + u**2.0)**.5)/0.3002
    return(ffwi)



# LETS BEGIN #

# set global variables
filePath = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData'
# This is James Powells API token
token = 'c03c614370e24a89a2f73d2e2cd80fa8'
# we are excluding 'BHCU1' since it stopped reporting last winter
stations = ["KSLC", "UT5", "UT3", "KIJ", "UTJUN", "UTHEB", "KHCR", "PGRU1", "KCDC", "UTBLK", "LPRU1", "UTLGP", "BBN", "KHIF"]
            # These are exculded because they do not have long enough data records to get a climatological percentile for last summer
            # need to run Alex's compute_percentiles first before running these
            #, "PC010", "PC016", "PC018", "PC021", "PC022", "PC023", "PC024", "PC025", "PC032", "PC033", "PC034"]



for station in stations:
    print('______________________STARTING WITH STATION: %s______________________________________\n' % (station))
    # initialize variables
    dailyAvgRH        = []
    dailyAvgWindSpeed = []
    dailyMaxWind      = []
    dailyAvgFFWI      = []
    day               = []
    date  = datetime(year = 2020, month = 5, day = 1)
    today = datetime.today()
    count = 0

    while date.date() != today.date():
        print("Starting on date:", date)
        # Need the right format for the dates for the api call
        # If the the month is 5 then the format needs to be 05 but if the month is 12 then it does not need a zero, the same goes for days
        if len(str(date.month)) == 1:
            if len(str(date.day)) == 1:
                url = "https://api.synopticdata.com/v2/stations/timeseries?&token=%s&start=%s0%s0%s0000&end=%s0%s0%s2359&obtimezone=utc&vars=relative_humidity,wind_speed,wind_gust,peak_wind_speed,air_temp&output=json&stid=%s" % (token, str(date.year), str(date.month), str(date.day), str(date.year), str(date.month), str(date.day), station )
            else:
                url = "https://api.synopticdata.com/v2/stations/timeseries?&token=%s&start=%s0%s%s0000&end=%s0%s%s2359&obtimezone=utc&vars=relative_humidity,wind_speed,wind_gust,peak_wind_speed,air_temp&output=json&stid=%s" % (token, str(date.year), str(date.month), str(date.day), str(date.year), str(date.month), str(date.day), station )
    
        else:
            if len(str(date.day)) == 1:
                url = "https://api.synopticdata.com/v2/stations/timeseries?&token=%s&start=%s%s0%s0000&end=%s%s0%s2359&obtimezone=utc&vars=relative_humidity,wind_speed,wind_gust,peak_wind_speed,air_temp&output=json&stid=%s" % (token, str(date.year), str(date.month), str(date.day), str(date.year), str(date.month), str(date.day), station )
            else:
                url = "https://api.synopticdata.com/v2/stations/timeseries?&token=%s&start=%s%s%s0000&end=%s%s%s2359&obtimezone=utc&vars=relative_humidity,wind_speed,wind_gust,peak_wind_speed,air_temp&output=json&stid=%s" % (token, str(date.year), str(date.month), str(date.day), str(date.year), str(date.month), str(date.day), station )
        print("Now opening this api: ", url)

        # This gets the data from the api
        response = urllib.request.urlopen(url)
        # This stores the information of the called api in a json format
        stationData = json.loads(response.read())

        #---------------------------- Calculate the Numbers we Need ----------------------------------------#
        #Get the month and day in the format MDD
        if len(str(date.day)) == 1:
            day.append('%s0%s' %(date.month, date.day))
        else:
            day.append('%s%s' %(date.month, date.day))
        
        ## this section of try and except statements make sure that in case there is no data we see the ERROR
        # Find the avg RH for that day
        try:
            RH     = np.array(stationData['STATION'][0]['OBSERVATIONS']['relative_humidity_set_1'], dtype=np.float64)
            RHmean = np.nanmean(RH)
        except:
            print('\nERROR: no data for RelativeHumdidty\n' )
            RHmean = 0
        # append the mean data
        dailyAvgRH.append(RHmean)

        #Find the avg Wind Speed
        try:
            windSpeed     = np.array(stationData['STATION'][0]['OBSERVATIONS']['wind_speed_set_1'], dtype=np.float64)
            windSpeedMean = np.nanmean(windSpeed)
        except:
            print('\nERROR: no data for windSpeed\n' )
            windSpeedMean = 0
        # append the mean data
        dailyAvgWindSpeed.append(windSpeedMean)

        # Find the max value of either the wind gust or peak wind speed
        # Need to get rid of NONE types so we can use the np.nanmax
        try:
            windGust    = np.array(stationData['STATION'][0]['OBSERVATIONS']['wind_gust_set_1'], dtype=np.float64)
            windGustMax = np.nanmax(windGust)
        except:
            print('\nERROR: no data for windGust\n' )
            windGustMax = 0
        try:
            peakWindSpeed    = np.array(stationData['STATION'][0]['OBSERVATIONS']['peak_wind_speed_set_1'], dtype=np.float64)
            peakWindSpeedMax = np.nanmax(peakWindSpeed)
        except:
            print('\nERROR: no data for peakWindSpeed\n' )
            peakWindSpeedMax = 0
        
        # Get the air Temp for use in the FFWI
        try:
            airTemp = np.array(stationData['STATION'][0]['OBSERVATIONS']['air_temp_set_1'], dtype=np.float64)
        except:
            print('\nERROR: no data for airTemp\n')

        # Find the which is bigger, the peak wind speed or the wind gust for that day
        if windGustMax >= peakWindSpeedMax:
            dailyMaxWind.append(windGustMax)
        else:
            dailyMaxWind.append(peakWindSpeedMax)


        # Lets get the FFWI
        FFWI    = []
        x = 0
        # Compute the FFWI for every data point
        while x < len(airTemp):
            FFWI.append(computeFFWI(RH[x], airTemp[x], windSpeed[x]))
            x += 1
        # Find the average of them all
        FFWImean = np.nanmean(FFWI)
        # append the mean data
        dailyAvgFFWI.append(FFWImean)

        count += 1
        date = date + timedelta(hours=24)

    #print('dailyAvgRH:',dailyAvgRH)
    print('len(dailyAvgRH):', len(dailyAvgRH))
    #print('dailyAvgWindSpeed:', dailyAvgWindSpeed)
    print('len(dailyAvgWindSpeed):', len(dailyAvgWindSpeed))
    #print('dailyMaxWind:', dailyMaxWind)
    print('len(dailyMaxWind):', len(dailyMaxWind))
    print('len(dailyAvgFFWI):', len(dailyAvgFFWI))
    #--------------------------------------------------------------------------------------------------------------------------#
    ### NEXT PART OF THE CODE ###
    ### This section will read in the station climatolgical records and then find based on a day and a value what the percentile was for that day

    #-------------------------------------------------------------------------------------------------------#
    # splineInterpolation: This function will perform spline Interpolation. I had to create my own function 
    # instead of using scipy because there were many repeat x values with multiple y values. So this function
    # will find the find the first occurance of the value that is directly less than the x wanted and the 
    # first value that is directly greater than the xw. It will then do the spline interpolation to find the
    # correct percentile.
    #-------------------------------------------------------------------------------------------------------#
    def splineInterpolation(xw, day, stnID, variable):
        # This reads in the data
        if variable == 'FFWI':
            percentileData = pd.read_csv('%s/dataFiles/percentiles/%s_percentiles_%s.csv' % (filePath, stnID, variable), index_col = 'MODY',usecols=range(0,26))
        else:
            percentileData = pd.read_csv('%s/dataFiles/percentiles/%s_percentiles_%s_set_1.csv' % (filePath, stnID, variable), index_col = 'MODY',usecols=range(0,26))

        # I did not include the 0 and 100 percentile since this can very easily be made up of bad data
        col_Names = ['0.50','1.00','5.00','10.00','15.00','20.00','25.00','30.00','35.00','40.00','45.00','50.00','55.00','60.00','65.00','70.00','75.00','80.00','85.00','90.00','95.00','99.00','99.50']

        j =0

        # This condition checks in case the value is lower than the 0.5 percentile,
        if xw < float(percentileData[col_Names[j]][day]):
            j =23
            # Assign the percentile as 0 since it is so small
            yw = 0

        # this is a condition in case the x wanted is 0 than that means there was no data 
        if xw == 0:
            j = 23
            yw = np.nan 


        # This loop takes care of selected the right values to do the spline interpolation
        while j < 23:
            # This will find the first value that is bigger than the x wanted.
            # the = of the >= takes care of the exception if the x wanted is the exact value as one of the col_Names
            if float(percentileData[col_Names[j]][day]) >= xw:
                y1 = float(col_Names[j])
                x1 = float(percentileData[col_Names[j]][day])

                #This deals with if the x values were repeated before finding the value above xw
                #this while loops logic is
                # While the value x-2 == x-1 keep looping
                while float(percentileData[col_Names[j-2]][day]) == float(percentileData[col_Names[j-1]][day]):
                    # move backwards till it is not the case that the x values are repeating
                    j -= 1
                # Once it is no longer repeating assign these values
                if  float(percentileData[col_Names[j-2]][day]) != float(percentileData[col_Names[j-1]][day]):
                    y0 = float(col_Names[j-1])
                    x0 = float(percentileData[col_Names[j-1]][day])
                break

            # In case the value is higher than any percentile
            if j == 22:
                #Since it is so high it is now the 100 percentile
                yw = 100
            j +=1

        # Condition to not run this if we aleady said that yw is 100
        if j != 23:
            # Spline interpolation equation
            # This solves for y wanted(our percentile) for the x wanted
            yw = y0 + ((y1 - y0)/ (x1-x0))*(xw - x0)
    
        return(yw)


    #Initialize final variables that will have the date and the percentile for that station
    RHDailyPercentile        = []
    windSpeedDailyPercentile = []
    windGustDailyPercentile  = []
    FFWIDailyPercentile      = []
    k = 0
    
    print('count: ', count)

    # This loop will go through each day and find the daly percentile that cooresponds to the certain value
    while k < count:
        #print('Starting on Date:', day[k])
        RHDailyPercentile.append(       splineInterpolation( float(dailyAvgRH[k])       , float(day[k]), station, 'relative_humidity' ))
        windSpeedDailyPercentile.append(splineInterpolation( float(dailyAvgWindSpeed[k]), float(day[k]), station, 'wind_speed' ))
        windGustDailyPercentile.append( splineInterpolation( float(dailyMaxWind[k])     , float(day[k]), station, 'wind_gust' ))
        FFWIDailyPercentile.append(     splineInterpolation( float(dailyAvgFFWI[k])     , float(day[k]), station, 'FFWI'))
        #print('________________________________________________________________________________')

        k += 1

    #--------------------------------------------------------------------------------------------------------------------------------#
    ### NEXT PART OF THE CODE ###
    ### This section will plot the data for each variable and save the graph

    # Have to make the lists a numpy array
    day = np.array(day)
    RHDailyPercentile        = np.array(RHDailyPercentile)
    windSpeedDailyPercentile = np.array(windSpeedDailyPercentile)
    windGustDailyPercentile  = np.array(windGustDailyPercentile)
    FFWIDailyPercentile      = np.array(FFWIDailyPercentile)

    # Initialize  variable lists to plot the data and the date
    varList      = [RHDailyPercentile, windSpeedDailyPercentile, windGustDailyPercentile, FFWIDailyPercentile]
    varListNames = ['Relative Humidity', 'Wind Speed', 'Max Wind Speed', 'FFWI']
    varFileNames = ['relative_humidity', 'wind_speed', 'wind_gust', 'FFWI']


    # This will go through the variables and make a plot for each
    for y, varName, fileName in zip(varList, varListNames, varFileNames):
        print('Starting to plot the graph: ', station + varName + ' Percentile 2020' )
        
        # create figure
        fig, ax = plt.subplots()
        #get the right data set fo y axis
        ax.scatter(day, y, s = 15)
        ax.set_title(station + " " + varName + ' Percentile 2020')
        fig.figsize=(8,8)


        # Helps the x axis appear less crowded
        start, end = ax.get_xlim()
        ax.xaxis.set_ticks(np.arange(start, end, 4))

        plt.gcf().autofmt_xdate()
        plt.grid(True, axis='y')
        plt.xlabel('Month/Day')
        if varName == 'Max Wind Speed':
            plt.ylabel('Daily '+ varName +' Percentile')
        else:
            plt.ylabel('Daily Mean '+ varName +' Percentile')

        plt.figure(figsize=(8,8))

        fig.savefig('%s/pngFiles/yearlyPercentilePics/%s_%s_Percentile_%s.png' % (filePath, station, date.year, fileName))
        print('Saving the figure: ', '%s/pngFiles/yearlyPercentilePics/%s_%s_Percentile_%s.png' % (filePath, station, date.year, fileName))
        #plt.show()
        

    print('______________________DONE WITH STATION: %s______________________________________\n' % (station))