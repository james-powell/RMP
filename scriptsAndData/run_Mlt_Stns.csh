#!/bin/tcsh
#
# Author  : James Powell
# Date    : 5/26/2020
# Purpose : Script to download multiple stations climetology and plot the information
#   	    This script will be used to call Alex python scripts for the different 
#   	    stations

#---------------------------------------------------------------------------------------#

# A list of all of the stations so far
set list1 = ("KSLC" "UT5" "UT3" "KIJ" "UTJUN" "UTHEB" "KHCR" "PGRU1" "KCDC" "UTBLK" "BHCU1" "LPRU1" "UTLGP" "BBN" "KHIF" "PC010" "PC016" "PC018" "PC021" "PC022" "PC023" "PC024" "PC025" "PC032" "PC033" "PC034" "UTSTR" "UTPLC" "UTMFS" "UTASG" "SND" "PCPD" "UTPCY" "HERUT" "P056C" "P057C" "UTSVC" "MTMET" "UT9")
set ctr = 1


# For list1 set the while loop condition to 40
while ( $ctr < 40 )
echo "-----------Starting Station:" $list1[$ctr] "--------------"


# Run the code to compute the consechrs hours for windspeed windgust and RH
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/compute_consechrs_stid_variable_threshold.py $list1[$ctr] wind_speed_set_1 20 A 6
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/compute_consechrs_stid_variable_threshold.py $list1[$ctr] wind_gust_set_1 25.8 A 6
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/compute_consechrs_stid_variable_threshold.py $list1[$ctr] relative_humidity_set_1 30 B 6

# Run the code to compute the percentile for wind and temprh
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/compute_percentiles_stid_variable.py $list1[$ctr] wind
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/compute_percentiles_stid_variable.py $list1[$ctr] temprh

# Plot the Figures for consechrs
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/plot_consechrs_stid_variable_threshold.py $list1[$ctr] wind_speed_set_1 20 A 6
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/plot_consechrs_stid_variable_threshold.py $list1[$ctr] wind_gust_set_1 25.8 A 6
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/plot_consechrs_stid_variable_threshold.py $list1[$ctr] relative_humidity_set_1 30 B 6

# Plot the figures for Percentiles
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/plot_percentiles_stid_variable.py $list1[$ctr] wind_speed_set_1
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/plot_percentiles_stid_variable.py $list1[$ctr] wind_gust_set_1
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/plot_percentiles_stid_variable.py $list1[$ctr] relative_humidity_set_1


#---------------------------------------------------------------------------------------#
# This section is for the FFWI Index #
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/james_Python_Scripts/FFWI_getData.py $list1[$ctr]
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/james_Python_Scripts/FFWI_compute_percentile.py $list1[$ctr]
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/plot_percentiles_stid_variable.py $list1[$ctr] FFWI


echo "-----------Done With Station:" $list1[$ctr] "--------------"
@ ctr++
end


#---------------------------------------------------------------------------------------#
# this section is for the KBDI index, we can only compute it for a select number of stns
set KBDI_list = ("KSLC" "KCDC" "PGRU1" "LPRU1") # "KHIF" not doing this station anymore till next year

set stn = 1

while( $stn < 5)
echo "-----------Starting Station:" $KBDI_list[$stn] " For the KBDI information --------"

###Get the KBDI data and compute the percentiles ###
# Not running this one since the graph python function updates the csv file with the new values
#~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/james_Python_Scripts/KBDI_getData.py $KBDI_list[$stn]

~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/james_Python_Scripts/KBDI_compute_percentile.py $KBDI_list[$stn]

# Plot the figure
~/anaconda3/bin/python3.7 /uufs/chpc.utah.edu/common/home/u1269218/public_html/RMP/scriptsAndData/Alex_Python_Scripts/plot_percentiles_stid_variable.py $KBDI_list[$stn] KBDI

echo "-----------Done With Station:" $KBDI_list[$stn] "--------------"

@ stn++
end

 
echo " All Done ;)"

