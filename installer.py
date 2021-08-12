# This file is for functions necessary for installing software

# importing required modules
from unzipper import unzip
from zipfile import ZipFile
import tempfile
import sys
import yaml
import pwd
import grp
import os
import requests

# Function for installing software from zip file
def install(fileName):

    # opening the zip file in READ mode
    with ZipFile(fileName, 'r') as zip:
        
        # extracting all the files
        with tempfile.TemporaryDirectory() as tempdir:
            zip.extractall(tempdir)

            # Open the manifest yaml file
            stream = open(tempdir + "/manifest.yaml", 'r')

            # Extract the manifest from the yaml file
            manifest = yaml.load(stream)['manifest']
            assets = manifest['assets']
    
            print(assets)
    
            # Install all assets
            for asset in assets:

                # Retrieve the user and group marked to be the file owner
                user, group = asset['owner'].split(':')

                # Retrieve the user and group ids
                uid = pwd.getpwnam(user).pw_uid
                gid = grp.getgrnam(group).gr_gid

                # Initialize the destination path
                path =  asset['dest'] + '/'
        
                # Complete the path, possibly changing the file name
                if 'destFilename' in asset:

                    # Add the new file name
                    path += asset['destFilename']

                else:

                    # Do not change the filename
                    path += asset['filename']

                # Move the file
                os.rename(tempdir +'/' + asset['filename'], path)

                # Update the owner of the file
                os.chown(path, uid, gid)

                # Update the permissions of the file
                os.chmod(path, asset['permissions'])

    
# Function for installing a key
def install_key(distro, architecture, software, version, dest, baseURL, token):

    # Call web service to get key

    # Define headers
    headers = {
        'Authorization': 'Bearer ' + token,
    }

    # This needs to be adjusted
    # Get the key
    response = requests.get(
        baseURL + '/key/' + distro \
        + '/' + architecture + '/' + software \
        + '/' + version,
        headers=headers)
    
    # install key 

    # Move the key
    with open(dest, "wb") as f:
        f.write(response.content)

# Function for downloading software
def download_software(distro, architecture, software, version, baseURL, token):

    # Call web service to download software

    # Define headers
    headers = {
        'Authorization': 'Bearer ' + token,
    }

    # Get the software
    response = requests.get(
        baseURL + '/installer/' + distro \
        + '/' + architecture + '/' + software \
        + '/' + version,
        headers=headers)

    # Save the software to a file
    with open(software + '.zip', "wb") as f:
        f.write(response.content)

# Function for submitting swid tags
def submit_tag(distro, architecture, software, version, baseURL, token, swid_tag):

    headers = {
        'Authorization': 'Bearer ' + token,
    }

    files = {
        'SWID_TAG': (None, swid_tag),
    }

    # Get the software
    response = requests.get(
        baseURL + '/swid/' + distro \
        + '/' + architecture + '/' + software \
        + '/' + version,
        headers=headers, files = files)

    # Save the software to a file
    with open(software + '.zip', "wb") as f:
        f.write(response.content)
