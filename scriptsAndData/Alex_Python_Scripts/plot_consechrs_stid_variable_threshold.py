## Python Script for plotting percentile output from compute_consechrs_stid_variable_threshold.py

import numpy as np
import gzip, sys, datetime, re, time, os, calendar
import matplotlib as M
M.use('Agg')
from matplotlib import pyplot as mply

## Set Script Timezone to GMT for ease of use

os.environ['TZ'] = 'Etc/Greenwich'
time.tzset()

## Input arguments
## instn is the station ID of interest (e.g. KSLC)
## invar is the Synoptic Data API variable name of interest (e.g. wind_speed_set_1)
## myvarthresh is the threshold value to assess in english units (e.g. for humidity 10 for 10%, for wind gust 30 for 30 mph, etc.)
## myvarabvblw is either A (for >=) or B (<=) to assess if greater than or less than for threshold
## myconsecutivehrs is the number of consecutive hours the threshold needs to be met (e.g. 6 for 6 hours)

## Example of how to run: python plot_consechrs_stid_variable_threshold.py KCDC wind_gust_set_1 30 A 4

instn = sys.argv[1]
invar = sys.argv[2]
myvarthresh = sys.argv[3]
myvarabvblw = sys.argv[4]
myconsecutivehrs = sys.argv[5]
varplotlist = [invar]

## Some dictionaries used for fancier naming and plotting in code below

varnamedict = {
	'wind_speed_set_1': 'Sustained Wind Speed',
	'wind_gust_set_1': 'Maximum Wind Speed/Gust',
	'air_temp_set_1': 'Air Temperature',
	'relative_humidity_set_1': 'Relative Humidity',	
}
varnameunits = {
	'air_temp_set_1': 'F',
	'relative_humidity_set_1': '%',	
	'wind_speed_set_1': 'mph',
	'wind_gust_set_1': 'mph',
}
varnamethreshsign = {
	'A': '>=',
	'B': '<=',
}

## Define Directories for CSV and PNG files

csvdir = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/dataFiles/station_occurances/'
pngdir = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/pngFiles/stationClimatologicalPics/'

## Shorten the plot view period from May 1 to October 31

plotstart = '0501'
plotend = '1031'

for invar in varplotlist:

	## File Names

	threshcsvfile = csvdir+instn+'_consec_'+str(myconsecutivehrs)+'_occurence_dailycount_'+myvarabvblw+str(myvarthresh)+'_'+invar+'.csv'
	threshpngfile = pngdir+instn+'_consec_'+str(myconsecutivehrs)+'_occurence_dailycount_'+myvarabvblw+str(myvarthresh)+'_'+invar+'.png'

	print(threshcsvfile)
	print(threshpngfile)

	## Read in CSV file data

	inhandle = open(threshcsvfile,'r')
	indata = inhandle.read().splitlines()
	inhandle.close()

	## Logic to read CSV file and store in threshdict dictionary by the header names
	
	threshdict = {
		'MODY': [],
	}
	inheader = indata[0].split(',')
	for x in indata[1:]:
		dataarray = x.split(',')
		if(float(dataarray[0]) >= float(plotstart) and float(dataarray[0]) <= float(plotend)):
			fakedateepoch = int(calendar.timegm(time.strptime(('2020'+str(dataarray[0])),'%Y%m%d')))	
			threshdict['MODY'].append(fakedateepoch)		
			for i in range(1,len(dataarray)):
				if(inheader[i] not in threshdict):
					threshdict[inheader[i]] = []
				threshdict[inheader[i]].append(float(dataarray[i]))

	## Matplotlib Logic to format X-axis date by month/day

	datelocater = M.dates.AutoDateLocator()
	dateaxisfmt = M.dates.DateFormatter('%m/%d')
	mpldatesstn = M.dates.epoch2num(threshdict['MODY'])

	## 2-Plot Figure
	## Top plot shows the actual number of occurrences as blue dots

	fig = mply.figure(figsize=(8,8))
	mply.suptitle(instn+' - Historical Record of '+varnamedict[invar]+' '+varnamethreshsign[myvarabvblw]+' '+str(myvarthresh)+' '+varnameunits[invar]+' \nfor '+str(myconsecutivehrs)+' Consecutive Hours per Day')
	myp1 = fig.add_subplot(211)
	mply.scatter(mpldatesstn,np.array(threshdict['DAYCOUNT_ACHIEVED']),color='b',s=10)	
	myp1.set_ylabel('Occurrences per Day of Year')
	myp1.xaxis.set_major_locator(datelocater)
	myp1.xaxis.set_major_formatter(dateaxisfmt)
	
	## Bottom plot shows the percentage of occurrences as red dots

	myp2 = fig.add_subplot(212)
	mply.scatter(mpldatesstn,np.array(threshdict['COUNT_PCT']),color='r',s=10)	
	myp2.xaxis.set_major_locator(datelocater)
	myp2.xaxis.set_major_formatter(dateaxisfmt)
	myp2.set_ylabel('Percentage Occurrence over Years Sampled')
	myp2.set_xlabel('Month/Day')
	
	mply.savefig(threshpngfile)
	mply.close()

sys.exit()
