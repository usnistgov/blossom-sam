import os
import sys
import json
from subprocess import Popen, PIPE, TimeoutExpired

# Timeout in seconds from the time we send our data to the helper to when we
# give up on getting a response.
BLOCKCHAIN_TIMEOUT=10

# Absolute path to the golang helper program.
BLOSSOM_HELPER_PATH = '/opt/blossom/bin/blossom-helper'

# Returns None on error, the returned data from the blockchain on success.
def _call_helper(call_info: dict):
    data = json.dumps(call_info).encode('utf-8')
    print('Sending transaction to blockchain...\n')

    with Popen(BLOSSOM_HELPER_PATH, stdin=PIPE, stdout=PIPE, stderr=PIPE) as p:
        try:
            out, err = p.communicate(data, BLOCKCHAIN_TIMEOUT)
        except TimeoutExpired:
            p.kill()
            out, err = p.communicate()
            print('Timeout communicating with helper...\n', file=sys.stderr)
            return None

        if p.returncode != 0:
            print('Blockchain returned error code %d...\n' % p.returncode,
                  file=sys.stderr)
            print('stdout: ' + out.decode('utf-8') + '\n', file=sys.stderr)
            print('stderr: ' + err.decode('utf-8') + '\n', file=sys.stderr)
            return None

    return out.decode('utf-8')

def _tx_create(func: str, args: list, transient: dict) -> dict:
    tx = {
        'identity': {
            'cert': os.environ['SAM_FABRIC_CERT'],
            'key': os.environ['SAM_FABRIC_KEY'],
            'msp': os.environ['SAM_FABRIC_ORG']
        },
        'profile': os.environ['SAM_FABRIC_PROFILE'],
        'channel': os.environ['SAM_FABRIC_CHANNEL'],
        'contract': os.environ['SAM_CHAINCODE_NAME'],
        'endorser': os.environ['SAM_FABRIC_PEER'],
        'function': func,
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
