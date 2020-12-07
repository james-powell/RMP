## Python Script for computing percentiles for a particular weather station and variable set

import numpy as np
import urllib.request
from datetime import datetime, timedelta
import gzip, sys, re, time, os, urllib, json, calendar

## Set Script Timezone to GMT for ease of use

os.environ['TZ'] = 'Etc/Greenwich'
time.tzset()

## Define Output Directory
outdir = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/dataFiles/percentiles/'
token = 'c03c614370e24a89a2f73d2e2cd80fa8'

## Input arguments
## mystnin is the station ID of interest (e.g. KSLC)
## myvarchoice can be temprh (to get temperature and relative humidity percentiles) or wind (to get wind speed/gust percentiles)
## Example of how to run: python compute_percentiles_stid_variable.py KCDC wind

mystnin = sys.argv[1]
myvarchoice = sys.argv[2]

## Create API variable lists (note that NWS stations also report peak_wind_speed_set_1 so we want that included in the gust percentile information)

if(myvarchoice == 'temprh'):
	varlist = 'air_temp,relative_humidity'
	myvars = ['air_temp_set_1','relative_humidity_set_1']
	myvarpct = ['air_temp_set_1','relative_humidity_set_1']
else:
	varlist = 'wind_speed,wind_gust,peak_wind_speed'
	myvars = ['wind_speed_set_1','wind_gust_set_1','peak_wind_speed_set_1']
	myvarpct = ['wind_speed_set_1','wind_gust_set_1']

## Generate list of percentiles we want to keep (0,0.5,1,5,10 ... 85,90,95,99,99.5,100)

mypcts = np.arange(5.,100.,5.)
mypctsmore = np.array([0.,0.5,1.,99.,99.5,100.])
mypcts = np.concatenate((mypcts,mypctsmore))

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

	stndata = {}
	stnobcount = {}
	stnpcts = {}
	
	for var in myvars:
		if var not in ['peak_wind_speed_set_1']:
			stndata[var] = {}
			stnpcts[var] = {}
			stnobcount[var] = {}

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
		
			## Convert ob timestamp to epoch seconds
			myepoch = int(calendar.timegm(time.strptime(stn['OBSERVATIONS']['date_time'][i],'%Y-%m-%dT%H:%M:%SZ')))
			
			## For a particular observation, we want to use the value for +-5 days around the current day (helps percentiles have a better representation of data for time of year and increases sampling size)
			## To do so, create a list of month-day elements
			
			mydylist = []
			for x in range((myepoch-5*86400),(myepoch+6*86400),86400):
				mysday = time.strftime('%m%d',time.localtime(x))
				mydylist.append(mysday)
				
			## Now loop through those month-day elements and each variable in the JSON output
				
			for myday in mydylist:
				for var in myvars:
					try:
						floatcheck = float(stn['OBSERVATIONS'][var][i])
						
						## If the variable is peak_wind_speed_set_1 we want to include the data values in wind_gust_set_1 percentiles instead
						## Store the observational values in stndata by variable and month-day keys, and also keep count of the number of observations added using stnobcount
						
						if var == 'peak_wind_speed_set_1':
							mytmpvar = 'wind_gust_set_1'
							if myday not in stndata[mytmpvar]:
								stndata[mytmpvar][myday] = []
								stnobcount[mytmpvar][myday] = 0
							stndata[mytmpvar][myday].append(floatcheck)
							stnobcount[mytmpvar][myday] = stnobcount[mytmpvar][myday]+1
						else:
							if myday not in stndata[var]:
								stndata[var][myday] = []
								stnobcount[var][myday] = 0
							stndata[var][myday].append(floatcheck)
							stnobcount[var][myday] = stnobcount[var][myday]+1
					except:
						skip = 1

	## Now loop through each variable and month-day combination

	for var in myvarpct:
		for mydy in stndata[var]:
		
			## Create an empty percentile dictionary using nested keys variable, month-day, and percentile
			## Use np.percentile to figure out the percentile of the observation data for that variable and month-day combo
		
			stnpcts[var][mydy] = {}
			for pcts in mypcts:
				mypctout = np.percentile(np.array(stndata[var][mydy]),pcts)
				stnpcts[var][mydy][pcts] = mypctout
				
		## Now write percentile output for each month-day to a CSV file based on station and variable
				
		outpctfile = outdir+mystn+'_percentiles_'+var+'.csv'
		print(outpctfile)
		outhandle = open(outpctfile,'w')
		outheader = 'MODY,'		
		outpcts = sorted(mypcts)		
		for outpct in outpcts:
			outheader = outheader+("%.2f" % outpct)+','
		outhandle.write(outheader+"\n")
		for mydy in sorted(stndata[var]):
			outline = mydy+','
			for outpct in outpcts:
				outline = outline+("%.3f" % stnpcts[var][mydy][outpct])+','
			outhandle.write(outline+"\n")
		outhandle.close()

sys.exit()