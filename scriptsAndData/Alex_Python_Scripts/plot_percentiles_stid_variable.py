## Python Script for plotting percentile output from compute_percentiles_stid_variable.py

import numpy as np
import gzip, sys, datetime, re, time, os,  calendar
import matplotlib as M
M.use('Agg')
from matplotlib import pyplot as mply

## Set Script Timezone to GMT for ease of use

os.environ['TZ'] = 'Etc/Greenwich'
time.tzset()

## Input arguments
## instn is the station ID of interest (e.g. KSLC)
## myvarin is the Synoptic Data API variable name of interest (e.g. wind_speed_set_1)

## Example of how to run: python plot_percentiles_stid_variable.py KCDC wind_gust_set_1

instn = sys.argv[1]
myvarin = sys.argv[2]
varplotlist = [myvarin]

## Some dictionaries used for fancier naming and plotting in code below

varnamedict = {
	'wind_speed_set_1': 'Sustained Wind Speed',
	'wind_gust_set_1': 'Maximum Wind Speed/Gust',
	'air_temp_set_1': 'Air Temperature',
	'relative_humidity_set_1': 'Relative Humidity',
	'FFWI': 'Fosberg Fire Weather Index',
	'KBDI': 'Keetch Byram Drought Index',
}
varnameunits = {
	'wind_speed_set_1': 'mph',
	'wind_gust_set_1': 'mph',
	'air_temp_set_1': 'F',
	'relative_humidity_set_1': '%',	
	'FFWI': '',
	'KBDI': '',
}

## Define Directories for CSV and PNG files

csvdir = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/dataFiles/percentiles/'
pngdir = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/pngFiles/stationClimatologicalPics/'

## Shorten the plot view period from May 1 to October 31
if myvarin == 'KBDI':
	plotstart = '0101'
	plotend = '1231'
else:
	plotstart = '0501'
	plotend = '1031'

for invar in varplotlist:

	## File Names
	
	pctcsvfile = csvdir+instn+'_percentiles_'+invar+'.csv'
	pctpngfile = pngdir+instn+'_plot_percentiles_'+invar+'.png'

	## Read in CSV file data

	inhandle = open(pctcsvfile,'r')
	indata = inhandle.read().splitlines()
	inhandle.close()

	## Lists of percentiles and line colors to use for plot (can change this as needed to only show specific percentiles)
	if myvarin == 'relative_humidity_set_1':
		keeppcts = ['50.00','10.00','5.00','1.00']
	else:
		keeppcts = ['50.00','90.00','95.00','99.00']
	pltcolors = ['b'   ,'g'    ,'orange'   ,'r'    ]
	
	## Logic to read CSV file and store in pctdict dictionary by percentiles
	
	pctdict = {
		'MODY': [],
	}
	for x in keeppcts:
		pctdict[x] = []
	inheader = indata[0].split(',')
	for x in indata[1:]:
		dataarray = x.split(',')	
		if(float(dataarray[0]) >= float(plotstart) and float(dataarray[0]) <= float(plotend)):	
			fakedateepoch = int(calendar.timegm(time.strptime(('2020'+str(dataarray[0])),'%Y%m%d')))	
			pctdict['MODY'].append(fakedateepoch)
			for i in range(0,len(dataarray)):
				if(inheader[i] in keeppcts):
					myval = float(dataarray[i])
					pctdict[inheader[i]].append(myval)

	## Matplotlib Logic to format X-axis date by month/day

	datelocater = M.dates.AutoDateLocator()
	dateaxisfmt = M.dates.DateFormatter('%m/%d')

	## Generate and Save Percentile Figure

	fig = mply.figure(figsize=(8,8))
	myp1 = fig.add_subplot(111)
	mply.title(instn+' - '+varnamedict[invar]+' - Daily Percentiles')
	mpldatesstn = M.dates.epoch2num(pctdict['MODY'])
	for i in range(0,len(keeppcts)):
		mply.plot(mpldatesstn,np.array(pctdict[keeppcts[i]]),color=pltcolors[i],label=keeppcts[i])	
	myp1.xaxis.set_major_locator(datelocater)
	myp1.xaxis.set_major_formatter(dateaxisfmt)
	myp1.set_xlabel('Month/Day')

	if myvarin == 'FFWI' or myvarin == 'KBDI':
		myp1.set_ylabel(varnamedict[invar])
	else:
		myp1.set_ylabel(varnamedict[invar]+' ('+varnameunits[invar]+')')
	mylegend = fig.legend(loc=8,ncol=5,borderaxespad=-0.3)
	frame = mylegend.get_frame()
	frame.set_edgecolor('none')
	mply.savefig(pctpngfile)
	mply.close()

sys.exit()
