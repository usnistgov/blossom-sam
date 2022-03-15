Add new admin user and system token by doing the following:
python3
import service.sam
service.sam.db.create_all()
service.sam.add_admin('admin', 'admin')
service.sam.add_system('testSystem', 'testToken')
quit()

Both of the above service lines should return True on success.
If you change the credentials above, adjust them in all commands below.

Run the service from this directory with the command:
python3 service/sam.py

Run the commands below in another terminal on the same system:
Add new software (make sure to copy zip file to the
/opt/blossom-sam/installers/ubuntu/x86_64/helloWashington/1.0.0 directory as
sam.pkg):
curl -u admin:admin --request POST --header "Content-Type: application/json" --data '{"name": "helloWashington", "version": "1.0.0", "arch": "x86_64", "os": "ubuntu", "blossom_asset": "asset1" }' http://localhost:8080/admin/addSoftware

Add key manually:
python3 -u -c 'import sys, base64; data=open("path/to/keyfile", "rb").read(); print(str(base64.urlsafe_b64encode(data), "ascii"))'
# fill in output from previous commmand in the key below, or just use the one I have here:
curl -u admin:admin --request POST --header "Content-Type: application/json" --data '{"key": "sxYgpkt/Qyv7v3nCEOj4nQ==" }' http://localhost:8080/admin/addKey/ubuntu/x86_64/helloWashington/1.0.0

Request keys from blockchain:
curl -u admin:admin --request POST --header "Content-Type: application/json" --data '{"count": 2 }' http://localhost:8080/admin/reqKeys/ubuntu/x86_64/helloWashington/1.0.0

Fetch keys from blockchain after request has been approved:
curl -u admin:admin --request POST http://localhost:8080/admin/getKeys/ubuntu/x86_64/helloWashington/1.0.0

Download software:
curl -o inst.zip --header "Authorization: Bearer testToken" http://localhost:8080/installer/ubuntu/x86_64/helloWashington/1.0.0

Download key:
curl -o inst.key --header "Authorization: Bearer testToken" http://localhost:8080/key/ubuntu/x86_64/helloWashington/1.0.0

Demonstrate key is what you fed in:
python3 -u -c 'import sys, base64; data=open("inst.key", "rb").read(); print(str(base64.urlsafe_b64encode(data), "ascii"))'
# output should match the key above in the addkey call

Register a SWID tag with the service (assuming the tag is in a file called "swid_tag"):
cat swid_tag | python3 -c 'import sys, base64; data=sys.stdin.read().encode("utf8"); print(str(base64.urlsafe_b64encode(data), "ascii"))'
curl -X POST -F 'SWID_TAG=VALUE FROM PREVIOUS COMMAND GOES HERE' -F 'LICENSE=B64 KEY VALUE GOES HERE' --header "Authorization: Bearer testToken" http://localhost:8080/swid/ubuntu/x86_64/helloWashington/1.0.0
