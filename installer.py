# This file is for functions necessary for installing software

# importing required modules
from unzipper import unzip
import yaml
import pwd
import grp
import os

# Function for installing software from zip file
def install(fileName):

    # Unzip the file
    unzip(fileName)

    # Open the manifest yaml file
    stream = open("manifest.yaml", 'r')

    # Extract the manifest from the yaml file
    assets = yaml.load(stream)['manifest']['assets']

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
        os.rename(asset['filename'], path)

        # Update the owner of the file
        os.chown(path, uid, gid)

        # Update the permissions of the file
        os.chmod(path, asset['permissions'])

    
