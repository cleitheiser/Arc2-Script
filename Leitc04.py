""" This script will create a workspace folder, ask for user input for file location. It sets the environmental variables
such as the scratch and working geodatabase. It also asks for user input if the file is on the local machine, if it is not
it will download a file from an website (http only) and extract it to the workspace folder. It reads the spatial reference
of the file and if it is not the preferred one it will project it and if it is unknown, it will define the projection. 

Note: Written in Python 2"""

#---------------------------------------------------------------------------------------------------------
##Import Modules
#---------------------------------------------------------------------------------------------------------

import requests 
import zipfile
import StringIO
import os
import urllib
import arcpy
import sys
import re

#-------------------------------------------------------------------------------------------------------------
##Create a workspace folder
#-------------------------------------------------------------------------------------------------------------

#Creates a new workspace folder
CreateFolder = raw_input('Do you want to create a new folder? (y/n)  ')
if CreateFolder.startswith('Y') or CreateFolder.startswith('y'):
    folder = str(raw_input('Enter folder name: '))
    path = str(raw_input('Enter the workspace location path, i.e. C:\Users\admin\Documents   '))
    os.makedirs(os.path.join(path,folder))
    print 'Workspace Created'

#Set the workspace to a current folder
elif CreateFolder.startswith('N') or CreateFolder.startswith('n'):
    OldFolder = raw_input('Do you have a working folder? (y/n)')
    if OldFolder.startswith('Y') or OldFolder.startswith('y'):
        folder = str(raw_input('Enter folder name: '))
        path = str(raw_input('Enter the workspace location path, i.e. C:\Users\admin\Documents   '))
        print 'Done'
    else:
        print 'What are you trying to do here'
        pass
else:
    pass

#-------------------------------------------------------------------------------------------------------------
##Set up the workspaces, both working geodatabase the scratch gdb
#-------------------------------------------------------------------------------------------------------------

# Initialize Variables
folderloc = os.path.join(path, folder)
out_folder_path = folderloc

print 'Lets set up the workspace'

# Create a Working Geodatabase (NOTE: several geodatabases can be created but they must have unique names)
default_gdb = str(raw_input('Enter the name of the working geodatabase: '))+'.gdb'
arcpy.env.workspace = os.path.join(folderloc, default_gdb)
arcpy.env.overwriteOutput = True
arcpy.CreateFileGDB_management(out_folder_path, default_gdb)

#Create the Scratch Geodatabase (NOTE: only one scratch geodatabase can be created)
arcpy.env.scratchWorkspace = folderloc
arcpy.env.scratchGDB
    
print 'Geodatabases created'

#---------------------------------------------------------------------------------------------------------
## Ask for input to see if the file is on the local disk or if it will have to be downloaded from a website 
#---------------------------------------------------------------------------------------------------------

#currently http only

process = str(raw_input('Do you currently have the file downloaded to your local machine? (y/n): ' ))

if process.startswith('Y') or process.startswith('y'):
    print 'Proceed'
    pass   

# This will go to a website and find the specified file and download it to a local machine. 
# this has been tested with a zipped shapefile and a zipped csv. It works where the file is on an http site but has not been  
# vetted for use with an ftp site. For the purpose of this test case visit https://extranet.gov.ab.ca/srd/geodiscover/srd_pub/LAT/FWDSensitivity/ 
# and download the file PipingPloverWaterbodies.zip.

elif process.startswith('N') or process.startswith('n'):
    website = str(raw_input('Enter the url of the website: '))
    #extractloc = folderloc#str(raw_input('Enter the location you want your extracted file, i.e. /Users/admin/Downloads: '))
    download = str(raw_input('Enter the name of the file, including the extension: '))
    
    #If the file is a zip file download it, unzip it, and extract it to the specified location
    if download.endswith('zip'):
        r = requests.get(website+download, stream=True)
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        z.extractall(folderloc)
    else:
        urllib.urlretrieve(website+download)
        os.chdir(folderloc)
    print 'File extracted'
     
else:
    print 'Error: Please enter y or n'


#--------------------------------------------------------------------------------------------------------------
##Find the shapefile's projection information and either define it if it is unknown or project it
#--------------------------------------------------------------------------------------------------------------

# Initialize variables
filename_no_ext = os.path.splitext(download)[0]
folder = os.listdir(folderloc)

#remove the extension from the filename and then split the words in the string into a list, of the last item in the list
#is in the filename this filename is selected and saved as a variable for the project function below
for infile in folder: 
    ext = os.path.splitext(infile)[-1]
    filenamesplit = re.findall('[A-Z][^A-Z]*', filename_no_ext)
    if ext == '.shp':
        if filenamesplit[-1] in infile:
            filename = infile

#Initialize Variables
Infeature = os.path.join(folderloc, filename)
Spatial_Ref = arcpy.Describe(Infeature).spatialReference

print 'The current projection is', Spatial_Ref.name

# Create a function to project a shapefile
def Project():
    Outshape = raw_input('Name of the output shapefile: ')
    Outfeature = os.path.join(folderloc, default_gdb, Outshape)
    print 'Please refer to http://spatialreference.org/ref/epsg/ to find the unique EPSG code for the spatial reference'
    OutCS = arcpy.SpatialReference(int(input('Enter the desired EPSG code: ')))
    arcpy.Project_management(Infeature, Outfeature, OutCS)

# If there is currently no projection define one
if Spatial_Ref.name == 'unknown':
    print 'Please refer to http://spatialreference.org/ref/epsg/ to find the unique EPSG code for the spatial reference'
    SR = arcpy.SpatialReference((int(input('Enter the desired EPSG code: '))))
    newsr = arcpy.DefineProjection_management(Infeature, SR)
    print 'Projection Defined'
else:
    pass

# Ask for user input and change the projection utilizing EPSG codes
project = raw_input('Do you want to change the projection (y/n)')
if project.startswith('y') or project.startswith('Y'):
    Project()
else:
    pass

#Add a 'do while' loop to continue asking for input until the user breaks the loop
Repeat = ''
while True:
    Repeat =  raw_input('Would you like to project another Shapefile? (y or n to quit)')
    if Repeat == 'n':
        break
    Project
print 'Done'

#------------------------------------------------------------------------------------------------------------------------
## FUTURE WORK
#------------------------------------------------------------------------------------------------------------------------

#could not get this part running so I will look at this again in the future.

# arcpy.env.workspace = folderloc
# questionclip = (raw_input('Do you want to clip this shapefile? (Y/N): '))
# if questionclip.startswith('Y') or questionclip.startswith('y'):
# #     Shapename = raw_input('Name of the output shapefile: ')
#     inshp = 'C:\Users\admin\Documents\BoundaryFile\Boundary.shp'
#     clipshp = 'C:\Users\admin\Documents\BoundaryFile\Buildings.shp'
#     output = os.path.join(folderloc, default_gdb)
#     arcpy.Clip_analysis(inshp, clipshp, output)
# elif questionclip.startswith('N') or questionclip.startswith('n'):
#     pass
# else:
#     print 'Error: Please enter Y or N'



# In the future

#     arcpy.FeatureClassToShapefile_conversion(["county", "parcels", "schools"],"C:/output")
#     arcpy.env.scratchWorkspace = folderloc
#     print 'Done'
