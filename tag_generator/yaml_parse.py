# This script prints a simple swid tag from a yaml file

# Tag Generating code partially sourced from https://github.com/strongswan/swidGenerator

# Import neccessary functions, many from strongswan's swidGenerator
from generators.swid_generator import create_software_identity_element
from package_info import PackageInfo
from xml.etree import ElementTree as ET
import yaml

#
stream = open('manifest.yaml', 'r')

#
manifest = yaml.load(stream)['manifest']
    
# Initialize the XML string to be used in swid tag
XML_DECLARATION = '<?xml version="1.0" encoding="utf-8"?>'

# Generate swid tag based on command-line arguments and environment
software_identity = create_software_identity_element(
    {
        "schema_location": False,
        "package_info": PackageInfo(manifest['software'], version = str(manifest['version'])),
        "xml_lang": manifest['language'],
        "os_string": manifest['os']['distro'] + " " + str(manifest['os']['version']),
        "architecture": manifest['architecture'],
        "id_prefix": manifest['os']['distro'] + "_" + str(manifest['os']['version']) \
        + '-' + manifest['architecture'] + '-',
        "entity_name": "blossom-sam",
        "regid": "blossom-sam.com",
        "meta_for": "os",
        "full": False
    })

# Generate utf8-encoded xml bytestring and print
swidtag = ET.tostring(software_identity, encoding='utf-8').replace(b'\n', b'')
print(XML_DECLARATION.encode('utf-8') + swidtag)
