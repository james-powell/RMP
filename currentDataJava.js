///////////////////////////////////////////////////////////////////////////////////
/* Author: James Powell                                                          */
/* Date:   7/10/2020                                                             */
/* Purpose: This is the Java script for the currentData webpage for use by RMP   */
///////////////////////////////////////////////////////////////////////////////////

filePathToPics = './scriptsAndData/pngFiles/'


//*******************************************************************************//
// findPageInfo():  For the yearly percentile page
//              this gets the values that the user selected from the dropdown
//              menu and passes them to the getPicture function
//*******************************************************************************//
function findPageInfo() 
{
    var selstID = document.getElementById("station");
    var stID1 = selstID.options[selstID.selectedIndex].value;

    var selvarType = document.getElementById("variable");
    var varType1 = selvarType.options[selvarType.selectedIndex].text;

    var selPeriod = document.getElementById("period");
    var period = selPeriod.options[selPeriod.selectedIndex].value;

    getPictures( stID1, varType1, period );
    getDescrip(  stID1, varType1, period );
    getTable( stID1 );
    
}

//*******************************************************************************//
// getPicture: This takes in three variables to find the path to the correct
//             picture file
//*******************************************************************************//
function getPictures(stID, variable, period)
{
    // add code later to automate getting the current year
    var thisYear = '2020';
    // create an image object
    var picYear   = new Image();
    var picRecent = new Image();
    // For wind speed
    if (variable == "Wind Speed")
    {
        //// create the file path to the user selected image 
        //var string = filePathToPics + 'yearlyPercentilePics/' + stID + "_" + thisYear + "_Percentile_wind_speed.png";
        //picYear.src = string;
        //picYear.setAttribute("alt", "Having trouble loading " +string); 

        // create the file path to the user 2nd selected image 
        var string1 = filePathToPics + 'extremePercentilePics/' + stID + "_" + thisYear + "_Extreme_wind_speed_" + period + ".png";
        picRecent.src = string1;
        picRecent.setAttribute("alt", "Having trouble loading " +string1);
    }

    // For wind gust
    else if (variable == "Wind Gust")
    {
        //// create the file path to the user selected image
        //var string = filePathToPics + 'yearlyPercentilePics/' + stID + "_" + thisYear + "_Percentile_wind_gust.png";
        //picYear.src = string;
        //picYear.setAttribute("alt", "Having trouble loading " +string);

        // create the file path to the user 2nd selected image 
        var string1 = filePathToPics + 'extremePercentilePics/' + stID + "_" + thisYear + "_Extreme_wind_gust_" + period + ".png";
        picRecent.src = string1;
        picRecent.setAttribute("alt", "Having trouble loading " +string1);
    }

    // For FFWI
    else if (variable == "Fosberg Fire Weather Index")
    {
        //// create the file path to the user selected image
        //var string = filePathToPics + 'yearlyPercentilePics/' + stID + "_" + thisYear + "_Percentile_FFWI.png";
        //picYear.src = string;
        //picYear.setAttribute("alt", "Having trouble loading " +string);

        // create the file path to the user 2nd selected image 
        var string1 = filePathToPics + 'extremePercentilePics/' + stID + "_" + thisYear + "_Extreme_FFWI_" + period + ".png";
        picRecent.src = string1;
        picRecent.setAttribute("alt", "Having trouble loading " +string1);
    }

    // For relative humdidity
    else 
    {
        //// create the file path to the user selected image
        //var string = filePathToPics + 'yearlyPercentilePics/' + stID + "_" + thisYear + "_Percentile_relative_humidity.png";
        //picYear.src = string;
        //picYear.setAttribute("alt", "Having trouble loading " +string);

        // create the file path to the user 2nd selected image 
        var string1 = filePathToPics + 'extremePercentilePics/' + stID + "_" + thisYear + "_Extreme_relative_humidity_" + period + ".png";
        picRecent.src = string1;
        picRecent.setAttribute("alt", "Having trouble loading " +string1);
    }
    
    // This adds the image object into the body (look for ID imgSpot)
    //document.getElementById("imgSpot").innerHTML = "<img id=\"imageBorder\" src=" + picYear.src + ">";
    // This adds the image object into the body (look for ID imgSpot)
    document.getElementById("imgSpot1").innerHTML = "<img id=\"imageBorder\" src=" + picRecent.src + ">";

}


//*******************************************************************************//
// getDescrip: This will get the right description for the graph
//             picture file
//*******************************************************************************//
function getDescrip( stID, variable, period)
{
    // Since the PC* stations do not have a long enough record to compare the variables we will 
    // use these other stations that are near them to compare too.
    var compareDir = {
        "PC010": 'UTASG',    "PC016": 'KCDC', 
        "PC018": 'PCPD' ,    "PC021": 'UT5', 
        "PC022": 'UT3'  ,    "PC023": 'UTMFS', 
        "PC024": 'KHCR' ,    "PC025": 'UTSTR', 
        "PC032": 'UT3'  ,    "PC033": 'UTPLC', 
        "PC034": 'UTPCY',    
        //"P056C": 'UTSVC',    "P057C": 'MTMET',    //Moved sometime and now dont have any stations close that are similar climatologically
        "PC053": 'UTBLK',    "PC054": 'BHCU1',    //Added 10/13/2020 
        "PC058": 'MTMET',    "PC059": 'UTSVC',    //Added 11/06/2020
    }

    // if the period is sinceMay we need to change it so the description is more 
    // user friendly
    if (period == "sinceMay"){
        period = " current fire season, aka (since May 1), "
    }

    // Beccause we had to change it for the above we need to add these transition 
    // words to help the flow of the sentance
    else{
        period = " last " + period + " of "
    }

    if (stID == "PC010" || stID == "PC018"){
        // For wind speed
        if (variable == "Wind Speed")
        {
            // Explanation for the Wind Speed recent graph
            var string = "This graph shows the " +period+ " data from " +stID+ ". The red data points highlight times when the " +variable+ " exceeded the threshold. No percentile line is shown for this graph since there is no suitable station close to " + stID+ ".";
            // Explanation for the current year Wind Speed Graph
            var string1 = "This shows an overview of the current years " +variable+ " percentile trend. The percentile values are from the daily mean " +variable+ ".";
        }

        // For wind gust
        else if (variable == "Wind Gust")
        {
            // Explanation for the Wind Speed recent graph
            var string = "This graph shows the " +period+ " data from " +stID+ ". The red data points highlight times when the " +variable+ " exceeded the threshold. No percentile line is shown for this graph since there is no suitable station close to " + stID+ ".";
            // Explanation for the current year Wind Speed Graph
            var string1 = "This shows an overview of the current years " +variable+ " percentile trend. The percentile values are from the daily maximum " +variable+ ".";
        }

        // For FFWI
        else if (variable == "Fosberg Fire Weather Index")
        {
            // Explanation for the Wind Speed recent graph
            var string = "This graph shows the " +period+ " data from " +stID+ ". This data comes from the 6-hr. running mean of the Fosberg Fire Weather Index (FFWI). The red data points highlight times when the FFWI exceeded the threshold. No percentile line is shown for this graph since there is no suitable station close to " + stID+ ".";
            // Explanation for the current year Wind Speed Graph
            var string1 = "This shows an overview of the current years " +variable+ " percentile trend. The percentile values are from the daily mean FFWI.";
        }

        // For relative humdidity
        else 
        {
            // Explanation for the Wind Speed recent graph
            var string = "This graph shows the " +period+ " data from " +stID+ ". The red data points highlight times when the " +variable+ " was under the threshold. The orange dashed line is the 5th percentile values observed near that time of year based on the available data record.";
            // Explanation for the current year Wind Speed Graph
            var string1 = "This shows an overview of the current years " +variable+ " percentile trend. The percentile values are from the daily mean " +variable+ ".";
            
            var PC_descripLine = "<br>Due to the shortness of the data record at " +stID+ " the percentile data is retreived from " +compareDir[stID]+ " because of its proximity and similar climate to " + stID + ".";
            string += PC_descripLine;
        }
    }
    
    else{
        // For wind speed
        if (variable == "Wind Speed")
        {
            // Explanation for the Wind Speed recent graph
            var string = "This graph shows the " +period+ " data from " +stID+ ". The red data points highlight times when the " +variable+ " exceeded the threshold. The orange dashed line is the 95th percentile values observed near that time of year based on the available data record.";
            // Explanation for the current year Wind Speed Graph
            var string1 = "This shows an overview of the current years " +variable+ " percentile trend. The percentile values are from the daily mean " +variable+ ".";
        }

        // For wind gust
        else if (variable == "Wind Gust")
        {
            // Explanation for the Wind Speed recent graph
            var string = "This graph shows the " +period+ " data from " +stID+ ". The red data points highlight times when the " +variable+ " exceeded the threshold. The orange dashed line is the 95th percentile values observed near that time of year based on the available data record.";
            // Explanation for the current year Wind Speed Graph
            var string1 = "This shows an overview of the current years " +variable+ " percentile trend. The percentile values are from the daily maximum " +variable+ ".";
        }

        // For FFWI
        else if (variable == "Fosberg Fire Weather Index")
        {
            // Explanation for the Wind Speed recent graph
            var string = "This graph shows the " +period+ " data from " +stID+ ". This data comes from the 6-hr. running mean of the Fosberg Fire Weather Index (FFWI). The red data points highlight times when the FFWI exceeded the threshold. The orange dashed line is the 95th percentile values observed near that time of year based on the available data record.";
            // Explanation for the current year Wind Speed Graph
            var string1 = "This shows an overview of the current years " +variable+ " percentile trend. The percentile values are from the daily mean FFWI.";
        }

        // For relative humdidity
        else 
        {
            // Explanation for the Wind Speed recent graph
            var string = "This graph shows the " +period+ " data from " +stID+ ". The red data points highlight times when the " +variable+ " was under the threshold. The orange dashed line is the 5th percentile values observed near that time of year based on the available data record.";
            // Explanation for the current year Wind Speed Graph
            var string1 = "This shows an overview of the current years " +variable+ " percentile trend. The percentile values are from the daily mean " +variable+ ".";
        }

        var stID_PC = stID.substring(0,2);

        // This is to add information about Pacificorp Stations regarding the percentile information
        if (stID_PC == "PC" || stID_PC == "P0")
        {
            var PC_descripLine = "<br>Due to the shortness of the data record at " +stID+ " the percentile data is retreived from " +compareDir[stID]+ " because of its proximity and similar climate to " + stID + ".";
            string += PC_descripLine;
        }
    }
    
    // This adds the description into the body
    document.getElementById("descripSpotCurrent").innerHTML = string;
    //document.getElementById("descripSpotYear").innerHTML = string1;
}

//*******************************************************************************//
// getTable: This will get the description table from the Station Location Page
//*******************************************************************************//
function getTable(stID)
{    
    var divElement = document.getElementById('iframe').contentWindow.document.getElementById(stID);
    document.getElementById("tableSpot").innerHTML = divElement.innerHTML;

}