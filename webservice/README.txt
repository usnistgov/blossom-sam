Add new admin user and system token by doing the following:
python3
import service.sam
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
curl -u admin:admin --request POST --header "Content-Type: application/json" --data '{"name": "helloWashington", "version": "1.0.0", "arch": "x86_64", "os": "ubuntu" }' http://localhost:8080/admin/addSoftware

Add key:
base64 path/to/keyfile
# fill in output from previous commmand in the key below, or just use the one I have here:
curl -u admin:admin --request POST --header "Content-Type: application/json" --data '{"key": "sxYgpkt/Qyv7v3nCEOj4nQ==" }' http://localhost:8080/admin/addKey/ubuntu/x86_64/helloWashington/1.0.0

Download software:
curl -o inst.zip --header "Authorization: Bearer testToken" http://localhost:8080/installer/ubuntu/x86_64/helloWashington/1.0.0

Download key:
curl -o inst.key --header "Authorization: Bearer testToken" http://localhost:8080/key/ubuntu/x86_64/helloWashington/1.0.0

Demonstrate key is what you fed in:
base64 inst.key
# output should match the key above in the addkey call