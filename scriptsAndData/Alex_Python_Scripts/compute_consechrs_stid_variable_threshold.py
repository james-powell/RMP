## Python Script for computing occurrences where a weather station ecclipses set variable and time thresholds

import numpy as np
import urllib.request
from datetime import datetime, timedelta
import gzip, sys, re, time, os, urllib, json, calendar

## Set Script Timezone to GMT for ease of use
os.environ['TZ'] = 'Etc/Greenwich'
time.tzset()

## Define Output Directory
outdir = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/dataFiles/station_occurances/'

token = 'c03c614370e24a89a2f73d2e2cd80fa8'


## Input arguments
## mystnin is the station ID of interest (e.g. KSLC)
## myvarin is the Synoptic Data API variable name of interest (e.g. wind_speed_set_1)
## myvarthresh is the threshold value to assess in english units (e.g. for humidity 10 for 10%, for wind gust 30 for 30 mph, etc.)
## myvarabvblw is either A (for >=) or B (<=) to assess if greater than or less than for threshold
## myconsecutivehrs is the number of consecutive hours the threshold needs to be met (e.g. 6 for 6 hours)
## Example of how to run: python compute_consechrs_stid_variable_threshold.py KCDC wind_gust_set_1 30 A 4
## That would find the occurrences where KCDC had wind gusts exceeding 30 mph for 4 consecutive hours

mystnin = sys.argv[1]
myvarin = sys.argv[2]
myvarthresh = sys.argv[3]
myvarabvblw = sys.argv[4]
myconsecutivehrs = sys.argv[5]

print('Station',mystnin,'VAR',myvarin,'THRESH',myvarthresh,myvarabvblw,'CONSECUTIVE HRS',myconsecutivehrs)

## Create API variable lists (note that NWS stations also report peak_wind_speed_set_1 so we want that included when wind_gust_set_1 is chosen)

if(myvarin == 'wind_gust_set_1'):
	varlist = 'wind_gust,peak_wind_speed'
	myvars = ['wind_gust_set_1','peak_wind_speed_set_1']
else:
	varlist = myvarin.replace("_set_1","")
	myvars = [myvarin]

## Set the historical data time range to check (note that Synoptic Data archives start Jan 1997)

apitimestart = '199701010000'

# Set the time to be 12 hours before to make sure Synoptic has the data
today = datetime.today()
apitimeend = datetime.strftime(today, format='%Y%m%d%H%M')
print('apitimeend: ', apitimeend, '\n')

## Put mystnin into a list and begin process of accessing historical data

sfcstnlist = [mystnin]
for mystn in sfcstnlist:

	## Create empty dictionaries and lists to store information

	stnhrs = {}
	stndaycountlist = {}
	stnyrlist = {}

	## Query Synoptic Data API and load into Python JSON Dictionary Format
	
	apiurl = 'http://api.synopticdata.com/v2/stations/timeseries?token='+token+'&units=english,speed|mph&start='+apitimestart+'&end='+apitimeend+'&stid='+str(mystn)+'&vars='+str(varlist)	
	print(apiurl)
	getreq = urllib.request.urlopen(apiurl)
	getdata = getreq.read()
	getreq.close()
	thisjson = json.loads(getdata)
	
	## Loop through JSON Structure
	
	for stn in thisjson['STATION']:
		for i in range(0,len(stn['OBSERVATIONS']['date_time'])):
			
			## Convert ob timestamp to epoch seconds and then figure out the hour the timestamp belongs to
			myepoch = int(calendar.timegm(time.strptime(stn['OBSERVATIONS']['date_time'][i],'%Y-%m-%dT%H:%M:%SZ')))
			myhrtime = time.strftime('%Y%m%d%H',time.localtime(myepoch))
			
			## Set an initial occurrence counter for the hour given to 0
			if myhrtime not in stnhrs:
				stnhrs[myhrtime] = 0
				
			## Loop through the variables acquire and see if any observations in that hour ecclipse the threshold specfied
			## If yes, then increment the stnhrs value for that particular hour
			for var in myvars:
				try:
					floatcheck = float(stn['OBSERVATIONS'][var][i])
					if(myvarabvblw == 'A'):
						if(floatcheck >= float(myvarthresh)):
							# print(stn['OBSERVATIONS']['date_time'][i],floatcheck,myhrtime)
							stnhrs[myhrtime] = stnhrs[myhrtime]+1
					else:
						if(floatcheck <= float(myvarthresh)):
							# print(stn['OBSERVATIONS']['date_time'][i],floatcheck,myhrtime)
							stnhrs[myhrtime] = stnhrs[myhrtime]+1
				except:
					skip = 1

	## Generate a CSV file that will contain every hour the station has reported where threshold was reached

	outhrfile = outdir+mystn+'_hourly_occurences_'+myvarabvblw+str(myvarthresh)+'_'+myvarin+'.csv'
	outhandle1 = open(outhrfile,'w')
	outheader1 = 'OBHOUR,OBS_ABOVE_THRESH,CONSEC_HRS'
	outhandle1.write(outheader1+"\n")

	## Complicated part - we need to keep track of (and reset) consecutive hours where a threshold was reached, which is done here
	hrcounter = 0
	epochlast = 0
	
	## Work through the hours consecutively
	for x in sorted(stnhrs):
	
		## Define empty lists based on month-day and 4-digit year to keep track of occurences by day of year and total years analyzed
		mody = x[4:8]
		thisyr = x[0:4]
		if(mody not in stnyrlist):
			stndaycountlist[mody] = []			
			stnyrlist[mody] = []
		if(thisyr not in stnyrlist[mody]):
			stnyrlist[mody].append(thisyr)
			
		## Figure out epoch second difference between current hour X and previous hour analyzed	
		xepoch = int(calendar.timegm(time.strptime(x,'%Y%m%d%H')))
		epochdiff = int(xepoch)-int(epochlast)
		
		## If that epoch second difference is larger than an hour (3600 seconds) - reset the counter (we can't assume threshold was met if we have no data for that hour)
		if(epochdiff <= 3600):
			skip = 1
		else:
			hrcounter = 0
			
		## If the number of occurrences for a particular hour is greater than 0, increment the counter, otherwise reset it
		if(float(stnhrs[x]) > 0):
			hrcounter = hrcounter + 1
		else:
			hrcounter = 0
			
		## If the hour counter is larger than 0, write it out to that previous CSV file (might be useful to see time periods where threshold was reached)
		if(hrcounter > 0):
			outline1 = x+','+("%.0f" % (stnhrs[x]))+','+("%.0f" % (hrcounter))
			outhandle1.write(outline1+"\n")
			
		## If the hour counter is greater than the consecutive hours desired, add the year to stndaycountlist dictionary by month-day if it wasn't in there already
		if(hrcounter >= int(myconsecutivehrs)):
			if(thisyr not in stndaycountlist[mody]):
				stndaycountlist[mody].append(thisyr)
		epochlast = xepoch
		
	outhandle1.close()
				
	## Now write out a CSV file which contains the month-day
	## The number of occurrences where the conditions were met for that station on that month-day
	## The total number of years assessed for that month-day
	## A percentage occurence based on those two values
	
	outdayfile = outdir+mystn+'_consec_'+str(myconsecutivehrs)+'_occurence_dailycount_'+myvarabvblw+str(myvarthresh)+'_'+myvarin+'.csv'
	outhandle = open(outdayfile,'w')
	outheader = 'MODY,DAYCOUNT_ACHIEVED,DAYCOUNT_TOTAL,COUNT_PCT'
	outhandle.write(outheader+"\n")
	for mydy in sorted(stnyrlist):
		outline = mydy+','+("%.0f" % (len(stndaycountlist[mydy])))+','+("%.0f" % (len(stnyrlist[mydy])))+','+("%.2f" % ((len(stndaycountlist[mydy])/len(stnyrlist[mydy]))*100.))
		outhandle.write(outline+"\n")
	outhandle.close()

sys.exit()