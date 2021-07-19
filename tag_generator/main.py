# This script prints a simple swid tag. It requires two command-line arguments.
# The first command-line argument is the name of the software.
# The second command-line argument is the version of the software.

# Tag Generating code partially sourced from https://github.com/strongswan/swidGenerator

# Import neccessary functions, many from strongswan's swidGenerator
from generators.swid_generator import create_software_identity_element
from package_info import PackageInfo
from xml.etree import ElementTree as ET
import sys, platform

# Initialize the XML string to be used in swid tag
XML_DECLARATION = '<?xml version="1.0" encoding="utf-8"?>'

# Generate swid tag based on command-line arguments and environment
software_identity = create_software_identity_element(
    {
        "schema_location": False,
        "package_info": PackageInfo(sys.argv[1], version = sys.argv[2]),
        "xml_lang": "en-US",
        "os_string": platform.linux_distribution()[0] + " " + platform.linux_distribution()[1],
        "architecture": platform.machine(),
        "id_prefix": platform.linux_distribution()[0] + "_" + platform.linux_distribution()[1] \
        + '-' + platform.machine() + '-',
        "entity_name": "blossom-sam",
        "regid": "blossom-sam.com",
        "meta_for": "os",
        "full": False
    })

# Generate utf8-encoded xml bytestring and print
swidtag = ET.tostring(software_identity, encoding='utf-8').replace(b'\n', b'')
print(XML_DECLARATION.encode('utf-8') + swidtag)
