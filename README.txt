Project  : Rocky Mtn Power 2020 (John Horel has said the webpages may be the start to do other work into station climatology besides just this)
Author   :  James Powell
Purpose  : Help develop tools to better predict wildfire conditions. It will be avaible via my public_html for communication purposes.
Last Edit: 7/9/2020

Programs needed: all scripts were created and initally ran using python3.7
                 webpages are created using html, css, and javascript

modules needed:  (FOR PYTHON3.7)
                    import csv                            
                    import urllib.request                                      
                    from datetime import datetime, timedelta
                    import numpy as np
                    import matplotlib.pyplot as plt      
                    import os.path
                    from os import path
                    import json
                    import pandas as pd
                    import calendar 
                    import sys
                    import time

File Structure:

                                                                       
                       
                       |-README.txt ( you found it )
                       | 
                       | 
                       |                                                          |-compute_consechrs_stid_variable_threshold.py (calculates and outputs a csv file to get consecutive climatology data)
                       |                                                          |
                       |                                                          |-compute_percentiles_stid_variable.py         (calculates and outputs a csv file to get daily percentile data)
                       |                              |-Alex_Python_Scripts-------|
                       |                              | (all these Alex J. made)  |-plot_consechrs_stid_variable_threshold.py    (plots the consecutive climatology data per station)
                       |                              |                           |
                       |                              |                           |-plot_percentiles_stid_variable.py            (plots the percentile data per station)
                       |                              |
                       |                              |
                       |                              |                           |-FFWI_data          ( folder with data records of the running six hour mean FFWI)
                       |                              |                           |
                       |                              |-dataFiles ----------------|-KBDI_data          ( folder with stations KBDI values from ~2010 to today)
                       |                              |                           |
                       |                              |                           |-percentiles        ( folder with the percentiles csv's for each station)
                       |                              |                           |
                       |                              |                           |-station_occurances ( folder with the outputs from Alex compute_conse* python script)
                       |                              |                           
                       |                              |
StationClimatology-----|-ScriptsAndData --------------|                           |-graph_extremePercentiles.py         ( This plots the last months and week data and extreme events)
                       |                              |                           |
                       |                              |                           |-graph_extremePercentiles_24Hour.py  ( This plots the last 24 hours data and the extreme events)
                       |                              |                           |
                       |                              |                           |-graph_extremePercentiles_KBDI.py    ( This plots the current years KBDI values for mulitple stations)
                       |  (any data (png or csv) and  |-james_Python_Scripts -----|
                       |   the scripts used to make   |                           |-currentYearPercentile.py            ( This plots the current fire seasons percentile graph )
                       |   them)                      |                           |
                       |                              |                           |-FFWI_compute_percentile.py          ( This takes the 6hr avg data and computes the daily percentile data)
                       |                              |                           |
                       |                              |                           |-FFWI_getData.py                     ( This calls the api and calculates the 6hr running avg)
                       |                              |                           |
                       |                              |                           |-KBDI_compute_percentile.py          ( This calls the KBDI csv and computes daily percentile data)
                       |                              |                           |
                       |                              |                           |-KBDI_getData.py                     ( This calls the api and calculates the KBDI values)
                       |                              |                           
                       |                              |
                       |                              |
                       |                              |                           |-extremePercentilePics       ( all outputted graphs from extremePercentile.py)
                       |                              |-pngFiles------------------|
                       |                              |                           |-stationClimatologicalPics   ( all outputted graphs from Alex_Python_Scripts and compute_percentile_FFWI)
                       |                              |                           |
                       |                              |                           |-yearlyPercentilePics        ( all outputted graphs from currentYearPercentile)
                       |                              |                           |
                       |                              |                           |-currentYearPercentile       ( outputted graphs for the KBDI index)
                       |                              |                           |
                       |                              |                           |-fireLine.jpg                ( backgroud header picture for webpages)
                       |                              |
                       |                              |
                       |                              |                                                      
                       |                              |-runMultipleStations.csh ( This is a tsch script that goes through all the stations and computes percentiles and consectuive hour data)
                       |                              
                       |
                       |
                       |-index.html                ( webpage to show graphs of current data and current year, (homepage of the project))
                       |-currentDataJava.js        ( javascript for index.html; used to get the right picture and description)
                       |
                       |-stationClimatology.html   ( webpage for climatolgical graphs of the different stations)
                       |-stationClimatologyJava.js ( javascript code for stationClimatology page)
                       |
                       |-KBDI_Index.html           ( webpage for displaying the current years KBDI values of selected stations)
                       |-KBDIJava.js               ( javascript code for KBDI page)
                       |
                       |-stationLocation.html      ( webpage describing locations and station information)
                       |-stylesheet.css            ( css style sheet for all RMP webpages)
                       

_________________________________________________________________________________________________________________________________________________________________________________________________________________________

cron Tasks: created on the Meso3 server
            
            # set to run 2:00 or 2am everyday
            2 0 * * * /uufs/chpc.utah.edu/common/home/u1269218/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/james_Python_Scripts/graph_extremePercentiles.py

            ### WE ARE NOT RUNNING THIS AT THE MOMENT###
            # set to run 23:00 or 11pm everyday
            #0 23 * * * /uufs/chpc.utah.edu/common/home/u1269218/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/james_Python_Scripts/currentYearPercentile.py

            # set to run every hour at min 0
            0 * * * * /uufs/chpc.utah.edu/common/home/u1269218/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/james_Python_Scripts/graph_extremePercentiles_24Hour.py

            # set to run daily at 5am
            5 0 * * * /uufs/chpc.utah.edu/common/home/u1269218/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/james_Python_Scripts/graph_extremePercentiles_KBDI.py


            # Set this to run on the 4th day of each month at 1am, takes ~10hr to run
            0 1 4 * * /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/runMultipleStations.csh





Flow chart:
        1. This is used to get the data for the indices that we are computing and showing via the webpage
            -FFWI_getData.py
            -KBDI_getData.py

        2. The following scripts create the base climatology CSV files that the rest of evertyhing is built off of.
            -compute_consechrs_stid_variable_threshold.py
            -compute_percentiles_stid_variable.py
            -FFWI_compute_percentile.py
            -KBDI_compute_percentile.py
        
        3. These scripts create the pictures generated from the CSV files from step 2 that will be shown on the webpages
            -plot_consechrs_stid_variable_threshold.py
            -plot_percentiles_stid_variable.py
            #-currentYearPercentile.py
            -graph_extremePercentiles.py
            -graph_extremePercentiles_24Hour.py
            -graph_extremePercentiles_KBDI.py

        4. These webpages then provide access to the png files
            -index.html
            -KBDI_Index.html
            -stationClimatology.html
            -stationLocation.html


