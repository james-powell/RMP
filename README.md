# RMP
Project  : Rocky Mtn Power 2020 (John Horel has said the webpages may be the start to do other work into station climatology besides just this)

Author   :  James Powell

Purpose  : Help develop tools to better predict wildfire conditions. It will be avaible via my public_html for communication purposes.
           Webpage link is found here http://home.chpc.utah.edu/~u1269218/RMP/

Last Edit: 12/7/2020

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
            import cgitb

            Just need for the HDWI_compute.py (this uses HRRR model data output and requires more libraries)
            import cartopy
            import cartopy.crs as ccrs
            import matplotlib.cm as mcm
            import xarray as xr
            import numcodecs as ncd
            import s3fs
                  

cron Tasks: created on the Meso3 server from University of Utah CHPC resource

            # set to run 2:00 or 2am everyday
            0 2 * * * /uufs/chpc.utah.edu/common/home/u1269218/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/james_Python_Scripts/graph_extremePercentiles.py

            # set to run every hour at min 0
            0 * * * * /uufs/chpc.utah.edu/common/home/u1269218/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/james_Python_Scripts/graph_extremePercentiles_24Hour.py

            # set to run every day at 3am
            0 3 * * * /uufs/chpc.utah.edu/common/home/u1269218/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/james_Python_Scripts/graph_extremePercentiles_sinceMay.py

            # set to run daily at 5am
            0 5 * * * /uufs/chpc.utah.edu/common/home/u1269218/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/james_Python_Scripts/graph_extremePercentiles_KBDI.py


            # Set this to run on the 4th day of each month at 1am, takes ~21 hr to run
            0 1 4 * * /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/runMultipleStations.csh > /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/output.txt 2>&1





Flow chart:

            1. This is used to get the data for the indices that we are computing and showing via the webpage
                -FFWI_getData.py
                -KBDI_getData.py
            2. The following scripts create the base climatology CSV files that the rest of evertyhing is built off of. (Alex's scripts also pull data for selected variables)
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
                -CD_otherMWStns.html
                -HDWI_Index.html
                -index.html
                -KBDI_Index.html
                -SC_otherMWStns.html
                -stationClimatology.html
                -stationLocation.html


