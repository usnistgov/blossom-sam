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
def ReportSwID(primary_tag: str, asset_id: str, license: str, tag: str):
    obj = {
        'account': os.environ['SAM_FABRIC_USER'],
        'primary_tag': primary_tag,
        'asset': asset_id,
        'license': license,
        'xml': tag
    }
    args = { 'swid': json.dumps(obj) }

    return loop.run_until_complete(cli.chaincode_invoke(
        requestor=fabric_user,
        channel_name=os.environ['SAM_FABRIC_CHANNEL'],
        peers=[os.environ['SAM_FABRIC_PEER']],
        args=None,
        cc_name=os.environ['SAM_CHAINCODE_NAME'],
        fcn='ReportSwID',
        waitForEvent=True,
        transient_map=args
    ))

def RequestCheckout(asset_id: str, count: int):
    args = { 'checkout': json.dumps({ 'asset_id': asset_id, 'amount': count }) }

    return loop.run_until_complete(cli.chaincode_invoke(
        requestor=fabric_user,
        channel_name=os.environ['SAM_FABRIC_CHANNEL'],
        peers=[os.environ['SAM_FABRIC_PEER']],
        args=None,
        cc_name=os.environ['SAM_CHAINCODE_NAME'],
        fcn='RequestCheckout',
        waitForEvent=True,
        transient_map=args
    ))

def GetLicenses(asset_id: str):
    args = [ os.environ['SAM_FABRIC_USER'], asset_id ]

    return loop.run_until_complete(cli.chaincode_invoke(
        requestor=fabric_user,
        channel_name=os.environ['SAM_FABRIC_CHANNEL'],
        peers=[os.environ['SAM_FABRIC_PEER']],
        args=args,
        cc_name=os.environ['SAM_CHAINCODE_NAME'],
        fcn='Licenses',
        waitForEvent=True
    ))

def Checkin(asset_id: str, licenses: list):
    args = { 'asset_id': asset_id, 'licenses': licenses }
    realargs = { 'checkin': json.dumps(args) }

    return loop.run_until_complete(cli.chaincode_invoke(
        requestor=fabric_user,
        channel_name=os.environ['SAM_FABRIC_CHANNEL'],
        peers=[os.environ['SAM_FABRIC_PEER']],
        args=None,
        cc_name=os.environ['SAM_CHAINCODE_NAME'],
        fcn='InitiateCheckin',
        waitForEvent=True,
        transient_map=realargs
    ))

def GetAssets():
    return loop.run_until_complete(cli.chaincode_invoke(
        requestor=fabric_user,
        channel_name=os.environ['SAM_FABRIC_CHANNEL'],
        peers=[os.environ['SAM_FABRIC_PEER']],
        args=[],
        cc_name=os.environ['SAM_CHAINCODE_NAME'],
        fcn='Assets',
        waitForEvent=True
    ))

def GetAssetInfo(asset_id: str):
    return loop.run_until_complete(cli.chaincode_invoke(
        requestor=fabric_user,
        channel_name=os.environ['SAM_FABRIC_CHANNEL'],
        peers=[os.environ['SAM_FABRIC_PEER']],
        args=[ asset_id ],
        cc_name=os.environ['SAM_CHAINCODE_NAME'],
        fcn='AssetInfo',
        waitForEvent=True
    ))
