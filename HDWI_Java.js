///////////////////////////////////////////////////////////////////////////////////
/* Author: James Powell                                                          */
/* Date:   11/23/2020                                                            */
/* Purpose: This is the Java script for the HDWI webpage for use by RMP          */
///////////////////////////////////////////////////////////////////////////////////

filePathToPics = './scriptsAndData/pngFiles/'

//*******************************************************************************//
// findPageInfo: For the yearly percentile page this gets the values that the    //
//               user selected from the dropdown menu and passes them to the     //
//               getPicture function                                             //
//*******************************************************************************//
function findPageInfo() 
{
    var dateControl = document.querySelector('input[type="date"]');
    var graph_date = dateControl.value;

    // This grabs the month and the day from the date string in format YYYY-MM-DD
    var month = graph_date.substring(5,7)

    var day = graph_date.substring(8,10)

    getPictures( month, day );
    getDescrip( month, day );

    
}

//*******************************************************************************//
// getPicture: This takes in three variables to find the path to the correct     //
//             picture file                                                      //
//*******************************************************************************//
function getPictures(month, day)
{

    // create an image object
    var pic_HDWI = new Image();

    // create the file path to the users selected image 
    var string1 = filePathToPics + 'HDWI_HRRR_Pics/' + month + day + "_HDWI_Utah.png";
    pic_HDWI.src = string1;
    pic_HDWI.setAttribute("alt", "Having trouble loading " +string1);

    
    // This adds the image object into the body (look for ID imgSpot)
    //document.getElementById("imgSpot").innerHTML = "<img id=\"imageBorder\" src=" + picYear.src + ">";
    // This adds the image object into the body (look for ID imgSpot)
    document.getElementById("imgSpot1").innerHTML = "<img id=\"imageBorder\" src=" + pic_HDWI.src + ">";

}


//*******************************************************************************//
// getDescrip: This will get the right description for the graph                 //
//             picture file                                                      //
//*******************************************************************************//
function getDescrip( month, day)
{

    // Explanation for the Wind Speed recent graph
    var string = "This graph shows the HDWI values for the state of Utah on "+month+"/"+day+". This data comes from the maximum value of the HDWI from about 6am - 6pm. The white lines seen are an unfortunate byproduct of the zarr file format used to store the HRRR data, since the data is stored in sections to make acess easier, there is a resulting space in between the sections and is of no real consequence. The HDWI value next to the line is the value at the line"

    // This adds the description into the body
    document.getElementById("descripSpotCurrent").innerHTML = string;
    //document.getElementById("descripSpotYear").innerHTML = string1;
}

