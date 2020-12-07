///////////////////////////////////////////////////////////////////////////////////
/* Author: James Powell                                                          */
/* Date:   7/10/2020                                                             */
/* Purpose: This is the Java script for the station Climatology webpage          */
///////////////////////////////////////////////////////////////////////////////////
// this is the file path to the png files
var filePath = "./scriptsAndData/pngFiles/stationClimatologicalPics/";


//*******************************************************************************//
// findPicture: this gets the values that the user selected from the dropdown
//              menu and passes them to the getPicture function
//*******************************************************************************//
function findPageInfo() 
{

    var selstID = document.getElementById("station");
    var stID1 = selstID.options[selstID.selectedIndex].value;

    var selvarType = document.getElementById("variable");
    var varType1 = selvarType.options[selvarType.selectedIndex].text;

    var selgraphType = document.getElementById("graphType");
    var graphType1 = selgraphType.options[selgraphType.selectedIndex].text;

    getPicture( stID1, varType1, graphType1);
    getDescrip( stID1, varType1, graphType1);
    getTable( stID1 );    
}


//*******************************************************************************//
// getPicture: This takes in three variables to find the path to the correct
//             picture file
//*******************************************************************************//
function getPicture(stID, variable, graphType)
{
    // create an image object
    var x = new Image();

    // For wind speed
    if (variable == "Wind Speed")
    {
        // Takes care of the graph type the user wants
        if (graphType == "Percentile")
        {
            // create the file path to the user selected image 
            var string = filePath + stID +"_plot_percentiles_wind_speed_set_1.png";
            x.src = string;
            x.setAttribute("alt", "Having trouble loading " +string);
        }

        else
        {
            // create the file path to the user selected image 
            var string = filePath + stID +"_consec_6_occurence_dailycount_A20_wind_speed_set_1.png";
            x.src = string;
            x.setAttribute("alt", "Having trouble loading " +string);

        }
        
    }

    // For wind gust
    else if (variable == "Wind Gust")
    {
        // Takes care of the graph type the user wants
        if (graphType == "Percentile")
        {
            // create the file path to the user selected image
            var string = filePath + stID +"_plot_percentiles_wind_gust_set_1.png";
            x.src = string;
            x.setAttribute("alt", "Having trouble loading " +string);
        }

        else
        {
            // create the file path to the user selected image
            var string = filePath + stID +"_consec_6_occurence_dailycount_A25.8_wind_gust_set_1.png";
            x.src = string;
            x.setAttribute("alt", "Having trouble loading " +string);
        }
    }

    // For FFWI
    else if (variable == "Fosberg Fire Weather Index")
    {
        // Takes care of the graph type the user wants
        if (graphType == "Percentile")
        {
            // create the file path to the user selected image
            var string = filePath + stID +"_plot_percentiles_FFWI.png";
            x.src = string;
            x.setAttribute("alt", "Having trouble loading " +string);
        }

        else
        {
            // create the file path to the user selected image
            var string = filePath + "FFWIerror.png";
            x.src = string;
            x.setAttribute("alt", "Having trouble loading " +string);
        }
    }

    // For relative humdidity
    else 
    {
        // Takes care of the graph type the user wants
        if (graphType == "Percentile")
        {
            // create the file path to the user selected image
            var string = filePath + stID +"_plot_percentiles_relative_humidity_set_1.png";
            x.src = string;
            x.setAttribute("alt", "Having trouble loading " +string);
        }

        else
        {
            // create the file path to the user selected image
            var string = filePath + stID +"_consec_6_occurence_dailycount_B30_relative_humidity_set_1.png";
            x.src = string;
            x.setAttribute("alt", "Having trouble loading " +string);
        }
    }
    
    // This adds the image object into the body (look for ID imgSpot)
    document.getElementById("imgSpot").innerHTML = "<img id=\"imageBorder\" src=" + x.src + ">";

}


//*******************************************************************************//
// getInfo: This will get the right description for the graph
//          picture file
//*******************************************************************************//
function getDescrip(stID, variable, graphType)
{
    // For wind speed
    if (variable == "Wind Speed")
    {
        // Takes care of the graph type the user wants
        if (graphType == "Percentile")
        {
            // create the file path to the user selected image 
            var string = "Percentile graphs highlight the typical conditions (50th percentile or median) observed near that time of year based on the available data record. For wind speed the frequency of extreme winds is shown by the 90th, 95th, and 99th percentile values.";
        }

        else
        {
            // create the file path to the user selected image 
            var string = "The upper panel of the Consecutive Hours graphs highlight how many days on that calendar date on which 6 or more hours exceeded the specified conditions. The lower panel is simply the percentage of days during the entire record on which those conditions are met.";
        }
        
    }

    // For wind gust
    else if (variable == "Wind Gust")
    {
        // Takes care of the graph type the user wants
        if (graphType == "Percentile")
        {
            // create the file path to the user selected image
            var string = "Percentile graphs highlight the typical conditions (50th percentile or median) observed near that time of year based on the available data record. For wind gust, the frequency of extreme winds is shown by the 90th, 95th, and 99th percentile values.";
        }

        else
        {
            // create the file path to the user selected image
            var string = "The upper panel of the Consecutive Hours graphs highlight how many days on that calendar date on which 6 or more hours exceeded the specified conditions. The lower panel is simply the percentage of days during the entire record on which those conditions are met.";
        }
    }

    // For FFWI
    else if (variable == "Fosberg Fire Weather Index")
    {
        // Takes care of the graph type the user wants
        if (graphType == "Percentile")
        {
            // create the file path to the user selected image
            var string = "Percentile graphs highlight the typical conditions (50th percentile or median) observed from the 6 hr running mean near that time of year based on the available data record. For the Fosberg Fire Weather Index (FFWI), the frequency of extreme winds is shown by the 90th, 95th, and 99th percentile values.";
        }

        else
        {
            // create the file path to the user selected image
            var string = "The upper panel of the Consecutive Hours graphs highlight how many days on that calendar date on which 6 or more hours exceeded the specified conditions. The lower panel is simply the percentage of days during the entire record on which those conditions are met.";
        }
    }

    // For relative humdidity
    else 
    {
        // Takes care of the graph type the user wants
        if (graphType == "Percentile")
        {
            // create the file path to the user selected image
            var string = "Percentile graphs highlight the typical conditions (50th percentile or median) observed near that time of year based on the available data record. For relative humidity, the frequency of extreme dry conditions is shown by the 10th, 5th, and 1st percentile.";
        }

        else
        {
            // create the file path to the user selected image
            var string = "The upper panel of the Consecutive Hours graphs highlight how many days on that calendar date on which 6 or more hours exceeded the specified conditions. The lower panel is simply the percentage of days during the entire record on which those conditions are met.";

        }
    }

    // This adds the description into the boy
    document.getElementById("descripSpot").innerHTML = string;    
}


//*******************************************************************************//
// getTable: This will get the description table from the Station Location Page
//*******************************************************************************//
function getTable(stID)
{    
    var divElement = document.getElementById('iframe').contentWindow.document.getElementById(stID);
    document.getElementById("tableSpot").innerHTML = divElement.innerHTML;

}


//*******************************************************************************//
// 
//*******************************************************************************//


//*******************************************************************************//
// dateDiff: Code taken from https://www.scriptol.com/javascript/dates-difference.php#:~:text=Difference%20between%20two%20dates%20in%20years&text=For%20example%2C%20the%20age%20of,toFixed(0).
//           pass in two dates (format D Month YYYY) returns diff of years
//*******************************************************************************//
function dateDiff(dateold, datenew)
{
  var ynew = datenew.getFullYear();
  var mnew = datenew.getMonth();
  var dnew = datenew.getDate();
  var yold = dateold.getFullYear();
  var mold = dateold.getMonth();
  var dold = dateold.getDate();
  var diff = ynew - yold;
  if(mold > mnew) diff--;
  else
  {
    if(mold == mnew)
    {
      if(dold > dnew) diff--;
    }
  }
  return diff;
}

