import os
import asyncio
import json
from hfc.fabric import Client

# Setup fabric connection.
eventloop = asyncio.get_event_loop()
fabric_cli = Client(net_profile=os.environ['SAM_FABRIC_PROFILE'])
fabric_user = cli.get_user(os.environ['SAM_FABRIC_ORG'], os.environ['SAM_FABRIC_USER'])
cli.new_channel(os.environ['SAM_FABRIC_CHANNEL'])

# Stubs for chaincode functions in blossom...
def ReportSwID(asset_id: str, license: str, tag: str):
    swid_obj = {
        'primary_tag': 'swid-1',
        'xml': tag,
        'asset': asset_id,
        'license': license,
        'lease_expiration': ''
    }
    args = [ json.dumps(swid_obj), os.environ['SAM_AGENCY'] ]

    return loop.run_until_complete(cli.chaincode_invoke(
        requestor=fabric_user,
        channel_name=os.environ['SAM_FABRIC_CHANNEL'],
        peers=[os.environ['SAM_FABRIC_PEER']],
        args=args,
        cc_name=os.environ['SAM_CHAINCODE_NAME'],
        fcn='ReportSwID',
        waitForEvent=True
    ))

def Checkout(asset_id: str, count: int):
    args = [ asset_id, os.environ['SAM_AGENCY'], count ]

    return loop.run_until_complete(cli.chaincode_invoke(
        requestor=fabric_user,
        channel_name=os.environ['SAM_FABRIC_CHANNEL'],
        peers=[os.environ['SAM_FABRIC_PEER']],
        args=args,
        cc_name=os.environ['SAM_CHAINCODE_NAME'],
        fcn='Checkout',
        waitForEvent=True
    ))

def Checkin(asset_id: str, licenses: list):
    args = [ asset_id, licenses, os.environ['SAM_AGENCY'] ]

    return loop.run_until_complete(cli.chaincode_invoke(
        requestor=fabric_user,
        channel_name=os.environ['SAM_FABRIC_CHANNEL'],
        peers=[os.environ['SAM_FABRIC_PEER']],
        args=args,
        cc_name=os.environ['SAM_CHAINCODE_NAME'],
        fcn='Checkout',
        waitForEvent=True
    ))

def Assets():
    return loop.run_until_complete(cli.chaincode_invoke(
        requestor=fabric_user,
        channel_name=os.environ['SAM_FABRIC_CHANNEL'],
        peers=[os.environ['SAM_FABRIC_PEER']],
        args=[],
        cc_name=os.environ['SAM_CHAINCODE_NAME'],
        fcn='Assets',
        waitForEvent=True
    ))
