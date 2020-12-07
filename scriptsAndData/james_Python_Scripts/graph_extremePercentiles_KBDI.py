# ~u1269218/anaconda3/bin/python3.7 

"""
Author  : James Powell
Date    : 7/9/2020
Purpose : Script to call the KBDI csv file for that station and then
          calculate any new values that need to be down to catch up the
          record to the day before it runs
Editing : 7/9/20 This script is ready to run on a chron task to update 
                  everday by itself. The saved product is the png files
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
import cgitb                          # For sending error emails
#----------------------------------------------------------------------#

########################################################################
# sendEmail: This function is to send an email in case of an error to 
#             alert whoever needs to know about the error
########################################################################
def sendEmail( emailBody, emailSubject ):
    # Email message to notify web admins in the case of a forecast.utah.edu downtime
    cgitb.enable()

    # Declare addresses
    frommail = 'u1269218@utah.edu'
    tomail = "u1269218@utah.edu"

    # Subject and message body delcarations
    emailsubjectlist = emailSubject
    emailmessage = emailBody

    # Craft email message
    emailp = os.popen('/usr/sbin/sendmail -t','w')
    emailp.write("From: "+frommail+"\n")
    emailp.write("To: "+tomail+"\n")
    emailp.write("Subject: "+emailsubjectlist+"\n")
    emailp.write(emailmessage+"\n")
    emailstatus = emailp.close()

if __name__ =='__main__':
    # set global variables
    filePath = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData'
    # filePath = 'C:/Users/u1269218/Documents/Mesowest/RockyMtnPowerStudy'
    # This is James Powells API token
    token = 'c03c614370e24a89a2f73d2e2cd80fa8'
    # I included BCHU1 again since it started reporting again
    stations = ["KSLC", "KCDC", "PGRU1", "LPRU1"] # "KHIF"  This station had problems with the precip reprted data 2020, 9, 8 so stopping calculation of the KBDI for now till we can restart it
    #stations = ['KCDC']

    for station in stations:
        try:
            print('______________________ STARTING TO CACLULATE THE KBDI INDEX AND GRAPH LAST YEAR FOR STATION: %s______________________________________\n' % (station))
            
            #############################################################################
            ######## GET THE LAST KBDI INDEX VALUE AND THE ANNUAL MEAN RAINFALL #########
            #############################################################################
            csvFile = '%s/dataFiles/KBDI_data/%s_KBDI_daily_values.csv' %(filePath, station)
            # the first row these will read in will look like this annual Mean RainFall, number
            KBDI_date = np.genfromtxt(csvFile, delimiter = ",", skip_header = 1, usecols = 0, dtype=str )
            KBDI      = np.genfromtxt(csvFile, delimiter = ",", skip_header = 1, usecols = 1, dtype=float )

            # need to get the R value to compute the KBDI index
            R = KBDI[0]
            # once we have the R value we can get rid of that data for when we save it we do not duplicate it
            KBDI      = np.delete(KBDI, [0]) 
            KBDI_date = np.delete(KBDI_date, [0])


            # Now we need to get the last date that the KBDI index was caclulated for and 
            # calculate the new KBDI index for all the days up until yesterday
            try:
                startDate = datetime.strptime(KBDI_date[-1], '%m/%d/%Y') + timedelta(days=1)
            except:
                startDate = datetime.strptime(KBDI_date[-1], '%Y-%m-%d') + timedelta(days=1)
            # We need a full day to calculate the KBDI so our endDate will be for yesterday
            # so we have a full days of data to call 
            endDate   = datetime.today() - timedelta(days=1)
            # Get int string form
            apiStartTime = datetime.strftime(startDate, format='%Y%m%d')
            apiEndTime   = datetime.strftime(endDate,   format='%Y%m%d')

            #print("Starting on date:", startDate.date())

            #############################################################################
            ################### THIS PART GETS THE RAIN DATA NEEDED #####################
            #############################################################################
            url = 'https://api.synopticdata.com/v2/stations/precipitation?&token=%s&start=%s0000&end=%s2359&pmode=intervals&interval=day&obtimezone=utc&units=precip|in&stid=%s' % (token, apiStartTime, apiEndTime, station)
            #print("Now opening this api: ", url)

            # This gets the data from the api
            response = urllib.request.urlopen(url)
            # This stores the information of the called api in a json format
            precipJson = json.loads(response.read())

            ### The format is weird so we need to iterate through to get all the data,
            ### so here are some empty lists to append data to
            precip     = []
            stringDays = []

            k = 0
            # If it calls more than one day it has an interval section that can work as the len of the list
            try:
                # If this statement is true go through and get all of the data
                if k < precipJson['STATION'][0]['OBSERVATIONS']['precipitation'][-1]['interval']:
                    while k < precipJson['STATION'][0]['OBSERVATIONS']['precipitation'][-1]['interval']:
                        precip.append(precipJson['STATION'][0]['OBSERVATIONS']['precipitation'][k]['total'])
                        stringDays.append(precipJson['STATION'][0]['OBSERVATIONS']['precipitation'][k]['first_report'])
                        k += 1
            
            # If it calls jsut one day the interval section is not there so just add the one value and move on
            except:
                precip.append(precipJson['STATION'][0]['OBSERVATIONS']['precipitation'][k]['total'])
                stringDays.append(precipJson['STATION'][0]['OBSERVATIONS']['precipitation'][k]['last_report'])
                #print('Running the except Statement')
            # This loops through and adds the precip totals and days to the respective lists


            # put precip in numpy array ad the rainDays in a pandas datetime object
            precip = np.array(precip)
            rainDays = pd.to_datetime(stringDays, format= '%Y-%m-%dT%H:%M:%SZ')

            #############################################################################
            ################ MOVE ON TO GET THE MAX DAILY TEMPERATURES ##################
            #############################################################################

            # Call the air Temp data and get 24 hour maximums
            apiurlTemp = 'http://api.synopticdata.com/v2/stations/timeseries?token=%s&units=temp|f&start=%s0000&end=%s2359&obtimezone=utc&stid=%s&vars=air_temp' %(token, apiStartTime, apiEndTime, station)	
            #print('now calling the api: ', apiurlTemp)
            getreq1  = urllib.request.urlopen(apiurlTemp)
            getdata1 = getreq1.read()
            getreq1.close()
            tempjson = json.loads(getdata1)

            # get the time in a pandas datetime object
            initialTime = np.array(tempjson['STATION'][0]['OBSERVATIONS']['date_time'])
            # List for the dates as datetime objects
            time_dt = pd.to_datetime(tempjson['STATION'][0]['OBSERVATIONS']['date_time'], format= '%Y-%m-%dT%H:%M:%SZ')

            # Get the other information in these lists
            airTemp   = np.array(tempjson['STATION'][0]['OBSERVATIONS']['air_temp_set_1'], dtype=np.float64)

            # find daily Temperature Maximums
            i = 0
            dailyMaxTemp = []
            tempDays = []
            iterDate = startDate

            # Loop  get the daily Max temp
            while iterDate.date != datetime.today().date():
                # create an empty array to store all the daily values in
                dailyValues = []

                # Iterate through one day.
                while time_dt[i].date() != (iterDate +timedelta(days=1)).date():
                    # add the values from that day to list
                    dailyValues.append(airTemp[i])
                    
                    # check to make sure that i is not passing the len of the list
                    if i >= len(time_dt)-1:
                        i += 1
                        break
                    i += 1
                
                

                # the KBDI index needs to have a threshold Temp values of 50-110 F
                # Some of synoptics data is messy so we need to do some clean up first
                # drop any values over 110
                dailyValues2 = [T for T in dailyValues if T <= 110]

                # put the max value in the right list
                try:
                    dailyMaxTemp.append(np.nanmax(dailyValues2))
                    tempDays.append(time_dt[i-1])
                except:
                    print('ERROR: No data for this day ', iterDate.date())
                
                # move it forward to the next day
                iterDate += timedelta(days=1)
                if i >= len(time_dt)-1:
                    break
                
            #print('len(dailyMaxTemp): ', len(dailyMaxTemp))
            #print('len(tempDays): ', len(tempDays))
            #print('len(precip): ', len(precip))
            #print('len(rainDays): ', len(rainDays))

            #############################################################################
            ########################## COMPUTE THE KBDI VALUES ##########################
            #############################################################################

            # Iterable variables
            counterR = 0
            counterT = 0

            # loop through the list to calc the KBDI until today
            while startDate.date() != (endDate + timedelta(days=1)).date():
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
                #print('precip[counterR]: ', precip[counterR])
                if precip[counterR] > 0:
                    # condition to check if it has rained the days leading up to the iterated day    
                    precipBefore = []        
                    daysBefore = -1
                    while precip[counterR + daysBefore] > 0:
                        #print('precip[counterR + daysBefore]: ', precip[counterR + daysBefore])
                        precipBefore.append(precip[counterR + daysBefore])
                        daysBefore -= 1
                    #print('daysBefore: ', daysBefore)
                    # if it had not rain before and the precip amount is over 0.2
                    if daysBefore == -1 and precip[counterR] > 0.2:
                        # then the net rain is the 24Hr precip minus 0.2
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
                ## calculate the drought factor and add that to the adjusted KBDI value to get
                ## todays KBDI value
                # calculate the Drought Factor
                droughtFactor = ((800-KBDI[-1])* (0.968*np.exp(0.0486*dailyMaxTemp[counterT]) - 8.30) *1 *0.001 )/ (1+10.88*np.exp(-0.0441*R))

                # condition to make sure the drought factor is never 0
                if droughtFactor < 0:
                    droughtFactor = 0

                newKBDI = adjKBDI + droughtFactor
                
                # the KBDI index should never go below 0 even if it rains    
                if newKBDI < 0:
                    newKBDI = 0
                # Put the new KBDI value in the list
                KBDI = np.append(KBDI, newKBDI)
                KBDI_date = np.append(KBDI_date, datetime.strftime(tempDays[counterT].date(), '%m/%d/%Y'))


                #print('rainDays[ctrR]: ', rainDays[counterR].date(), '\tprecip[ctrR]: ', precip[counterR],' ', '\tnetRainFall: ', netRainFall, '\tadjKBDI: ', adjKBDI, '\tdroughtFactor: ', droughtFactor, '\tdailyMaxTemp[ctrT]: ', dailyMaxTemp[counterT], '\tnewKBDI: ', KBDI[-1])
                #print('-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
                counterT += 1
                counterR += 1
                startDate += timedelta(days=1)


            #############################################################################
            ################# SAVE THE NEW INFORMATION TO THE CSV FILE ##################
            #############################################################################

            # this puts the time frames in a new array     
            data = np.concatenate([[KBDI_date],[KBDI]])

            print('Now writing over this file:   %s/dataFiles/KBDI_data/%s_KBDI_daily_values.csv' %(filePath, station))

            # This part will save the data array that is filled with the timeframes to a new csv file
            np.savetxt('%s/dataFiles/KBDI_data/%s_KBDI_daily_values.csv' %(filePath, station), 
                    data.T, fmt='%s', delimiter=',', 
                    header=('Time UTC, KBDI values\n anual mean RainFall, %f'%( round(R, 2)) ), comments='')

            
            #--------------------------------------------------------------------------------------------------------------------------------#
            ### NEXT PART OF THE CODE ###
            ### This section will plot the data for each variable and save the graph
            
            # Initialize  variable lists to plot the data and the date
            varList      = [ KBDI ]
            varListNames = [ 'Keetch Byram Drought Index' ]
            varFileNames = [ 'KBDI' ] 
            #threshold    = [ 622.2 ]

            KBDI_date = pd.to_datetime(KBDI_date, format= '%m/%d/%Y')

            # This is for the period of the x axis
            begin = datetime.today().date().replace(day=1).replace(month=1)
            endDate = endDate.replace(month=12, day=31)

            #--------------------------------------------------------------------------------------------------------------------------------#

            ## THIS SECTION GETS THE DATA FOR THE 95TH PERCENTILE
            # Read in the data for the 95th percentile and the 5th so we can plot it
            KBDIperc  = pd.read_csv('%s/dataFiles/percentiles/%s_percentiles_KBDI.csv' % (filePath, station),usecols=(0,22) , dtype = str)
            # Get the percentile information in the right format
            KBDIperc['MODY'] = str(endDate.year) + KBDIperc["MODY"]
            KBDIperc['MODY'] = pd.to_datetime(KBDIperc['MODY'], format='%Y%m%d')
            
            KBDIperc['95.00'] = pd.to_numeric(KBDIperc['95.00'])
            #--------------------------------------------------------------------------------------------------------------------------------#

            ## Plot the Data
            # This will go through the variables and make a plot for each
            for y, varName, fileName in zip(varList, varListNames, varFileNames):
                # Wind Speed
                fig, ax = plt.subplots()
                
                # This plots the y with a different color if the values exceed the threshold
                ax.plot(KBDI_date, KBDI, label=fileName)
                ax.plot(KBDIperc['MODY'], KBDIperc['95.00'], color='orange', linestyle = '--', label='95th Percentile')
            
                ax.set_ylabel(varName)

                ax.set_xlabel( 'Year-Month-Day (UTC Time)')
                # let the user know when the last date on the graph is
                yesterday = datetime.today() - timedelta(days=1)
                ax.set_title('%s %s For The Current Year\n Last updated %s' %(station, varName, yesterday.date()))            
                
                # set the time period
                ax.set_xlim( xmin=begin, xmax=endDate)

                lgd = ax.legend(loc='upper center', bbox_to_anchor=(.5,1.28),
                                ncol=2, shadow = True)

                plt.gcf().autofmt_xdate()
                plt.grid(True, axis='y')

                # not working because it formats it for the whole data set not just the xlim that I set
                #plt.autoscale(enable=True, axis='both')
                plt.figure(figsize=(8,30))

                fig.savefig('%s/pngFiles/currentYear/%s_%s_Extreme_%s_Year.png' % (filePath, station, endDate.year, fileName),  bbox_extra_artists=(lgd,), bbox_inches='tight')
                print('Saving the figure: ', '%s/pngFiles/currentYear/%s_%s_Extreme_%s_Year.png' % (filePath, station, endDate.year, fileName))
                plt.close(fig)


            #print('______________________DONE WITH STATION: %s______________________________________\n' % (station))

        except:
            email_Subject = "%s, RMP code error with KBDI" %(station)
            email_Body = """graph_extremePercentiles_KBDI.py is skipping station %s.
            Please contact James Powell if you have any questions at u1269218@utah.edu.
            For more information see https://mesowest.utah.edu/cgi-bin/droman/meso_base_dyn.cgi?stn=%s

            -Pointer Bot""" %(station, station)

            sendEmail( email_Body, email_Subject)
        