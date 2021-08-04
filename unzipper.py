# This file is for functions necessary for unzipping files

# importing required modules
from zipfile import ZipFile
import sys

# Function for unzipping
def unzip(fileName):
    
    # opening the zip file in READ mode
    with ZipFile(fileName, 'r') as zip:
        # printing all the contents of the zip file
        zip.printdir()
        
        # extracting all the files
        # print('Extracting all the files now...')
        zip.extractall()
        #print('Done!')
