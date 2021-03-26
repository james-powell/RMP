# ~u1269218/anaconda3/bin/python3.7 

"""
Author  : James Powell
Date    : 11/30/2020
Purpose : Script to calculate the Hot-Dry-Windy Index for part of Utah.
          Logs into AWS space to get HRRR data and then computes the HDW and
          makes a graph for it 
"""
#---------------------------------------------------------------------------#
# Import modules
import numpy as np

import cartopy
import cartopy.crs as ccrs
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib.cm as mcm
import xarray as xr

import numcodecs as ncd
import s3fs

#-----------------------------------------------------------------------------#
# global variables

# Constants
L_v     = 2.5e6     #J/kg
R_v     = 461       #J/(K kg)
R_d     = 287       #J/(K kg)
c_p     = 1004      #J/(K kg)
epsilon = 0.622

filePath = '/uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData'
#filePath = 'C:/Users/u1269218/Documents/Mesowest/RockyMtnPowerStudy'

# This is the file that houses the latitude and longitude data for the zarr HRRR files
latLon_data = '/uufs/chpc.utah.edu/common/home/horel-group7/Pando/hrrr/HRRR_latlon.h5'
x = xr.open_dataset(latLon_data)
lat = x.latitude.data
lon = x.longitude.data

#-----------------------------------------------------------------------------#
# findChunk: Input Lat/Lon you are interested in to find chunk
#            This function was written by Taylor McCorkle
#-----------------------------------------------------------------------------#
def findChunk(latPoint,lonPoint):
    absLat = np.abs(lat - latPoint)
    absLon = np.abs(lon - lonPoint)
    c = np.maximum(absLon,absLat)
    index = np.where(c == c.min())

    x = int(index[0])
    y = int(index[1])
    
    # Divide by chunk size - ignoring remainder
    chunkX = (x//150)
    chunkY = (y//150)
    
    return chunkX, chunkY

#-----------------------------------------------------------------------------#
# getLatLons: Get your latitude and longitudes for your chunk
#             This function was written by Taylor McCorkle
#-----------------------------------------------------------------------------#
def getLatLons(chunkX,chunkY):
    x0 = chunkX*150
    y0 = chunkY*150
    xRange = x0+150
    yRange = y0+150
    
    chunkLats = lat[x0:xRange,y0:yRange]
    chunkLons = lon[x0:xRange,y0:yRange]
    
    return chunkLats, chunkLons

#-----------------------------------------------------------------------------#
# getAllLatLon_Dictionary: This gets the latitudes and longitudes for all four
#                          chunks and stores them in a dictionary
#-----------------------------------------------------------------------------#
def getAllLatLon_Dictionary(initial_latitudes, initial_longitudes, geographical_location):
    # Dictionary to store lat and lon data for each of the 4 chunks
    latLon_dictionary = {}
    # dictionary to store the chunk id for each of the 4 chunks
    chunkID_dictionary  = {}

    # This loop will get lat and lons and chunk ID for each cooresponding chunk
    for int_lat, int_lon, int_loc in zip(initial_latitudes, initial_longitudes, geographical_location):
    
        x, y = findChunk(int_lat, int_lon)
        # store chunk ID in dictionary in the right format
        chunkID_dictionary['chunkID_' + str(int_loc) ] = '{}.{}'.format(x,y)

        # get the lat and lons for this chunk and store them in the dictionary
        latLon_dictionary['Lats_' + str(int_loc)], latLon_dictionary['Lons_' + str(int_loc)] = getLatLons(x,y)
    
    return (chunkID_dictionary, latLon_dictionary)

#-----------------------------------------------------------------------------#
# getAWS_Keys: This code returns the access and secrect key required to 
#              log into AWS space. Done for security. This code was 
#              written by Zach Reick
#-----------------------------------------------------------------------------#
def getAWS_Keys():
    # get the access and secret key from text doc
    arr2 = []
    with open("/uufs/chpc.utah.edu/common/home/u0845413/python_scripts/AWS.txt", "r+") as f:
        for line in f:
            arr2.append(line)

    val1 = arr2[0].split(" = ")
    val2 = arr2[1].split(" = ")

    # Populate to key fields
    parser = val1[1]
    parser2 = val2[1]
    # Need to remove blank line in output
    med = parser.splitlines()
    med2 = parser2.splitlines()
    access_key = med[0]
    secret_key = med2[0]
    
    return(access_key, secret_key)

#-----------------------------------------------------------------------------#
# decompressChunk: this decompress the chunk data and returns it in a array
#                  with the shape   (n, 150, 150)
#-----------------------------------------------------------------------------#
def decompressChunk(data_filePath, chunkID, which_f):
    #buf = ncd.blosc.decompress(open(data_filePath+chunkID, 'rb').read())
    #print('data_filePath: ', data_filePath)
    #print('chunkID: ', chunkID)
    buf = ncd.blosc.decompress(fs.open(data_filePath+chunkID, 'rb').read())

    if which_f == 'f4':
        chunk = np.frombuffer(buf, dtype='<f4')
    else:
        chunk = np.frombuffer(buf, dtype='<f2')
    #print(len(chunk))

    #if len(chunk) == 810000:
    #    n = 36
    #elif len(chunk) == 405000:
    #    n = 18
    #elif len(chunk) == 765000:
    #    n = 34
    #elif len(chunk) == 382500:
    #    n = 17
    #elif len(chunk) == 22500:
    #    n = 1

    hrrr_data = np.reshape(chunk,((150,150)))
    #print(np.shape(hrrr_data))
    return(hrrr_data)

#-----------------------------------------------------------------------------#
# calcVPD: This calculates the Vaper Pressure Deficit (e_s - e) for a given 
#           location. If it is above the surface, it drops it adiabatically
#           to the surface before computing VPD
#-----------------------------------------------------------------------------#
def calcVPD(ground_level, parcel_level, T, RH ): 
    # Make sure T is in Kelvin
    if T < 150:
        T = T + 273.15
    else:
        pass

    # Makes sure RH is not in percentage form
    if RH < 1:
        RH = RH * 100
    else: 
        pass
    
    # Make sure the pressures are in hPa not in Pa
    if ground_level > 1200: 
        ground_level = ground_level / 100
    elif parcel_level > 1200:
        parcel_level = parcel_level / 100
    else:
        pass

    # if we are computing it for the surface layer we dont need to drop it 
    # adiabatically first
    if parcel_level == ground_level:
        e_s = 6.112 * np.exp( (L_v/R_v) * (1/273.15 - 1/T) )

        e = RH * e_s / 100


    # if the air is at a different level we need to lower it adiabatically
    # then compute the VPD
    else:
        ### get the temp of the parcel at the ground level
        # get the potential temp
        theta = T * ((1000/parcel_level) ** (R_d/c_p))

        #now convert that to a temperature at the ground level
        T_ground = theta / ((1000/ground_level) ** (R_d/c_p))
        #print('T_ground: ',  T_ground)

        ### Now get w since it is conserved in order to find RH
        # find e_s  and then e for the parcel w
        e_s_parcel = 6.112 * np.exp( (L_v/R_v) * (1/273.15 - 1/T) )
        e_parcel   = RH * e_s_parcel / 100
        #print('e_s_parcel: ', e_s_parcel,'\te_parcel: ', e_parcel)

        w = epsilon * ( e_parcel / ( parcel_level - e_parcel ) )
        #print('w: ', w)

        # Now solve for e at the ground_level
        e = ( w * ground_level / epsilon) / (1 + (w / epsilon) )

        # solve for e_s at the ground level
        e_s = 6.112 * np.exp( (L_v/R_v) * (1/273.15 - 1/T_ground) )

    #print('e_s: ', e_s,'\te: ', e)

    VPD = e_s - e

    if VPD < 0:
        print('ERROR: VPD VALUE LESS THAN ZERO: ' + str(round(VPD,2)) )

    return(VPD)

#-----------------------------------------------------------------------------#
# calcWindSpeed: Compute the wind speed from u and v-components, needs (m/s) 
#-----------------------------------------------------------------------------#
def calcWindSpeed( u, v): 
    wind_speed = np.sqrt( u**2 + v**2 )
    return(wind_speed)

#-----------------------------------------------------------------------------#
# findNearestPressureLevel: This will take in a pressure level and find the 
#                           closest pressure level rounded to 25 hPa
#-----------------------------------------------------------------------------#
def findNearestPressureLevel(sfc_pres, base = 25):
    # Make sure the sfc_pres is in hPa and not in Pa
    if sfc_pres > 1200:
        sfc_pres = sfc_pres / 100
    else:
        pass

    # Math to round to the nearest 25 hPa
    nearestP_level = base * round(sfc_pres / base)
    
    # if its close to sea level Pressure we will need to return 100mb since
    # the pressure files only have down to 1000
    # THIS WILL NEED TO BE CHANGED AT SOME POINT TO DIRECT THEM TO THE SURFACE FILE INSTEAD THIS IS BETTER LOGIC THAN 1000
    if nearestP_level > 1000:
        print('---------HAD A RETURNED PRESSURE LEVEL OF %s----------' %(nearestP_level))
        return (1000)
    else:
        return(nearestP_level)

#-----------------------------------------------------------------------------#
# getLevelData: find the data for each pressure level and calculate the Vapor
#               Pressure Deficit and the real wind speed and return this. In 
#               order to make this run faster that data will then be stored in 
#               a dictionary.
#-----------------------------------------------------------------------------#
def getLevelData( levels, levelData ):
    VPDs = []
    wind = []

    # Loop through each level above the ground and get
    for level in levels:
        # trying to just find TEMP because if its in there than the rest will be also
        if str(level)+'TMP' in levelData.keys():
            #print('--this level already has data, pulling it from the dictionary')
            level_temp  = levelData[str(level)+'TMP']
            level_RH    = levelData[str(level)+'RH']
            level_windU = levelData[str(level)+'UGRD']
            level_windV = levelData[str(level)+'VGRD']

        else:
            #print('--This is not found in the dictionary pulling it from AWS space')
            # Get the paths for the different variables we need
            level_temp  = zarr_bin + '%s_%sz_prs.zarr/%smb/TMP/%smb/TMP/'   %(stringDate, date.hour, int(level), int(level) )
            level_RH    = zarr_bin + '%s_%sz_prs.zarr/%smb/RH/%smb/RH/'     %(stringDate, date.hour, int(level), int(level) )
            level_windU = zarr_bin + '%s_%sz_prs.zarr/%smb/UGRD/%smb/UGRD/' %(stringDate, date.hour, int(level), int(level) )
            level_windV = zarr_bin + '%s_%sz_prs.zarr/%smb/VGRD/%smb/VGRD/' %(stringDate, date.hour, int(level), int(level) )

            level_temp  = decompressChunk(level_temp , ID, 'f2')
            level_RH    = decompressChunk(level_RH   , ID, 'f2')
            level_windU = decompressChunk(level_windU, ID, 'f2')
            level_windV = decompressChunk(level_windV, ID, 'f2')

            # Now store this information in the levelData dictionary so we dont have to pull it again in the future
            levelData[str(level) + 'TMP' ] = level_temp 
            levelData[str(level) + 'RH'  ] = level_RH   
            levelData[str(level) + 'UGRD'] = level_windU
            levelData[str(level) + 'VGRD'] = level_windV                           

        # Okay now we got the data from this level calculate the VPD
        VPDs.append( calcVPD( sfc_pres, level, level_temp[i][j], level_RH[i][j] )) 
        wind.append( calcWindSpeed( level_windU[i][j], level_windV[i][j] ))
        #print('levelData.keys(): ', levelData.keys())
    
    return(VPDs, wind, levelData)

#-----------------------------------------------------------------------------#
#  setUpConditionsForGraph: this sets up base for the graph
#-----------------------------------------------------------------------------#
def setUpConditionsForGraph():
    # set up things for the map
    lakes = cartopy.feature.NaturalEarthFeature('physical', 'lakes', '10m',
                                            facecolor='none')

    states = cartopy.feature.NaturalEarthFeature(
                category='cultural', scale='50m', facecolor='none',
                name='admin_1_states_provinces_shp')

    # set which colors are going to be used in the color map
    bcol = mcm.get_cmap('YlOrRd')

    # Set up the projection for the data
    datacrs = ccrs.PlateCarree()
    
    # This gets the number of levels of shading for the countour graph
    levels = np.linspace(cmin, cmax, 100)

    return( lakes, states, bcol, datacrs, levels)

#-----------------------------------------------------------------------------#
# graphHDWI: This function takes in the data needed and the other settings
#            in order to graph the HDWI
#-----------------------------------------------------------------------------#
def graphHDWI(HDW_dictionary, latLon_dictionary, lakes, states, bcol, datacrs, lvls, cmin, cmax, string_date, run ):
    
    fig,ax = plt.subplots(figsize=(10,10),subplot_kw={'projection': datacrs})

    ax.set_extent([-114.5,-108.55,36.56, 42.45])
    #ax.set_extent([-118,-106,34, 45])

    # loop to plot each chunk HDW
    for loc, HDW_key in zip(geo_location, HDW_dict):
        #plt.contour(latLon_dict['Lons_' + str(loc)], latLon_dict['Lats_' + str(loc)], HDW_dict[HDW_key] ,cmap=bcol, transform=datacrs, levels=lvls, linewidths=0.6)
        plt.contourf(latLon_dictionary['Lons_' + str(loc)], latLon_dictionary['Lats_' + str(loc)], HDW_dictionary[HDW_key] ,cmap=bcol, transform=datacrs, levels=lvls) #, alpha=0.4)

    ax.add_feature(states,edgecolor='black',zorder=100,linewidth=3)

    ax.add_feature(lakes,edgecolor='darkblue',zorder=98,linewidth=2.0)
    ax.set_title('HRRR HDWI for %s' %(stringDate) ,fontsize=30)

    cbar = plt.colorbar(orientation='horizontal', pad = 0.01, aspect = 25)
    #cbar.set_label('HDWI Values', fontsize=16,pad = 0.1)
    cbar.set_ticks([np.arange(cmin, cmax, 50)])


    plot_file = '%s/pngFiles/HDWI_HRRR_Pics/%s_HDWI_Utah_run%sz.png' %(filePath, string_date[4:], run)
    plt.savefig(plot_file)


###############################################################################
#################### Get chunk ID's and lat and lons ##########################
###############################################################################
# Get 4 chunks that make up the data used for Utah
geo_location = [ 'NE',  'NW',  'SE',   'SW']
initial_lats = [   41,    41,    37,    36 ]
initial_lons = [-111., -115., -110., -114. ]

chunkID_dict, latLon_dict = getAllLatLon_Dictionary(initial_lats, initial_lons, geo_location)

###############################################################################
################## LOG INTO AWS SPACE TO GET THE DATA #########################
###############################################################################
ACCESS_KEY, SECRET_KEY = getAWS_Keys()

# Add region for header
region = 'us-west-1'

# Establish a working path for idx file creation using s3fs
fs = s3fs.S3FileSystem( key = ACCESS_KEY, secret = SECRET_KEY,
                        client_kwargs = dict(region_name = region))

###############################################################################
##################### CALCULATE THE HDW FOR EACH RUN ##########################
###############################################################################

# initial variables
date = datetime(2020,10,31, 19)
stringDate = datetime.strftime(date, '%Y%m%d')

#print(fs.ls('s3://hrrrzarr/prs/%s/%s_%sz_prs.zarr/' % (stringDate, stringDate, date.hour)))

# HDW index values will be stored here
HDW_dict = {'HDW_NE': np.zeros((150, 150)), 'HDW_NW': np.zeros((150, 150)), 
            'HDW_SE': np.zeros((150, 150)), 'HDW_SW': np.zeros((150, 150))  }

# we need to know the min and max HDW value for the graph
# ==> store that in the cmin and cmax variables
cmin = 0
cmax = 0

# This creates a loop to go through this day from UTC 12 - 00
######## This will need to be changed back to 1 eventually when other days are in AWS
while str(date.hour) != '0':
    #try:
    print('\n_________________________________________STARTING ON THE RUN %s__________________________________________' %(date.hour))
    stringDate = datetime.strftime(date, '%Y%m%d')

    #print(fs.ls('s3://hrrrzarr/prs/')) #%s/%s_%sz_prs.zarr/' % (stringDate, stringDate, date.hour)))

    # Base working diretory
    zarr_bin     = 's3://hrrrzarr/prs/%s/' %(stringDate) 
    zarr_bin_sfc = 's3://hrrrzarr/sfc/%s/' %(stringDate)

    sfc_pres_path = zarr_bin_sfc + '%s_%sz_anl.zarr/surface/PRES/surface/PRES/' % (stringDate, date.hour)
    # dictionary to store the surface pressure for the 4 chunks
    sfc_pres_dict = {}

    # This loop will go thorugh each sfc pressure level and compute the HDW index for that chunk
    for int_loc, HDW_key, ID in zip(geo_location, HDW_dict.keys(), chunkID_dict.values()):

        # Get the surface pressure level for this chunk and store it in the dictionary
        sfc_pres_dict['sfc_pres_'+str(ID)] = decompressChunk(sfc_pres_path, ID, 'f4')
        
        print('starting to compute values for %s Utah' %(int_loc))
        # Variables for loop
        i = 0   # row
        j = 0   # column
        
        # Create a dictionary that will hold the data for different levels as you use them
        # this will save time so you dont have to keep opening the same files in AWS again
        level_Data = {}

        # Now create a loop to go through each member of sfc_pressures chunk and calculate the 
        # HDW index for it
        while i < 150:
            j = 0
            while j < 150:
                # check if it is in the bounds of Utah
                if (36.53 < latLon_dict['Lats_' + str(int_loc)][i][j] < 42.47) and (-114.55 < latLon_dict['Lons_' + str(int_loc)][i][j] < -108.5):
                    
                    # get one value of pressure and find its closest pressure level
                    sfc_pres = findNearestPressureLevel( sfc_pres_dict['sfc_pres_'+str(ID)][i][j] )
                    #print('sfc_pres: ', sfc_pres)
                    
                    # if its greater than 800 hPa use the 4 layers above it
                    if sfc_pres > 800:
                        # This creates a list of the 4 pressure levels above and including the surface level
                        pres_levels = np.arange(sfc_pres, sfc_pres - 76,  -25)
                    
                    # if its less than or equal to 800 hPa use the 3 layers above it
                    elif sfc_pres <= 800:
                        # This creates a list of the 4 pressure levels above and including the surface level
                        pres_levels = np.arange(sfc_pres, sfc_pres - 51,  -25)

                    #calls the function that will calculate the VPD and the wind speed for each pressure level and returns those values
                    VPD_list, wind_list, level_Data = getLevelData( pres_levels, level_Data)
                        
                    # Get the max value from any level for the corresponding list
                    max_VPD  = np.max( VPD_list  )
                    max_wind = np.max( wind_list )
                
                    # Compute the HDW for this spot
                    HDW_value = max_VPD * max_wind

                    # If the value for this run is greater than the previous HDW value for that point replace it
                    # We want the max HDW value throughout the day
                    if HDW_value > HDW_dict[HDW_key][i][j]:
                        HDW_dict[HDW_key][i][j] = HDW_value
                    
                    #print('run:%s \t HDW[%i][%i]: ' %(date.hour, i,j),  HDW[i][j])
                    #print('\n')
                
                # If the value is not in Utah save time and dont caculate the HDW
                else:
                    HDW_dict[HDW_key][i][j] = np.nan

                j += 1
            i += 1

        #print('HDW_dict[%s]: ' %(HDW_key), HDW_dict[HDW_key])
        
        # Now that we have the values find the max and min        
        if cmax < np.nanmax(HDW_dict[HDW_key]):
            cmax = np.nanmax(HDW_dict[HDW_key])

        if cmin > np.nanmin(HDW_dict[HDW_key]):
            cmin = np.nanmin(HDW_dict[HDW_key])
                       
    #date = date + timedelta(hours = 1)

    #print('cmax: ', cmax)
    #print('cmin: ', cmin)


    ############################################################################### 
    ################ PLOT THE HDW INDEX VALUES FOR THIS CHUNK #####################
    ############################################################################### 

    # Set up base conditions
    lakes, states, bcol, datacrs, lvls = setUpConditionsForGraph()

    graphHDWI(HDW_dict, latLon_dict, lakes, states, bcol, 
                    datacrs, lvls, cmin, cmax, stringDate, date.hour)

    date = date + timedelta(hours = 1)
