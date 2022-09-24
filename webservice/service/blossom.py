import os
import sys
import json
import requests

BLOCKCHAIN_HELPER_ADDR = 'http://localhost:8080/'

# Returns None on error, the returned data from the blockchain on success.
def _call_helper(call_info: dict):
    print('Sending transaction to blockchain...\n')
    resp = requests.post(BLOCKCHAIN_HELPER_ADDR + "invoke", json=call_info)

    if resp.response_code < 200 or resp.response_code >= 300:
        print('Blockchain helper returned error code ' + str(resp.response_code))
        return None

    return resp.text

def _tx_create(func: str, args: list, transient: dict) -> dict:
    tx = {
        'identity': os.environ['SAM_FABRIC_IDENTITY'],
        'name': func,
        'args': args,
    }

    if transient is not None:
        tx['transient'] = transient

    return tx

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
    tx = _tx_create('ReportSwID', [], args)
    return _call_helper(tx)

def RequestCheckout(asset_id: str, count: int):
    args = { 'checkout': json.dumps({ 'asset_id': asset_id, 'amount': count }) }
    tx = _tx_create('RequestCheckout', [], args)
    return _call_helper(tx)

def GetLicenses(asset_id: str):
    args = [ os.environ['SAM_FABRIC_USER'], asset_id ]
    tx = _tx_create('Licenses', args, None)
    return _call_helper(tx)

def Checkin(asset_id: str, licenses: list):
    args = { 'asset_id': asset_id, 'licenses': licenses }
    realargs = { 'checkin': json.dumps(args) }
    tx = _tx_create('InitiateCheckin', [], realargs)
    return _call_helper(tx)

def GetAssets():
    tx = _tx_create('Assets', [], None)
    return _call_helper(tx)

def GetAssetInfo(asset_id: str):
    tx = _tx_create('AssetInfo', [ asset_id ], None)
    return _call_helper(tx)
