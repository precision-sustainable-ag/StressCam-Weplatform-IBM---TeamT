import requests
import json
import cloudant, hashlib, uuid
import http.client

def main(payload):
    #user verification
    #Parse payload
    username = str(payload['body'].get('username'))
    password = str(payload['body'].get('password'))
    role = str(payload['body'].get('role'))
    noderedPayload = str(payload["body"].get('noderedPayload'))
    cameraNumber = str(payload["body"].get('cameraNumber'))
    success = False
    message = ''
    noderedResponse = "..."
    commandType = "..."
    if not noderedPayload == "None" 
    #Verify payload
    if username == "None" or password == "None" or role == "None"  or cameraNumber =='None':
        success = False
        message = 'Payload is not valid. One of username, password, usage, or role is missing.'
    else:
        success, message = verifyUser(username, password, role)
        if success:
            if payload["body"].get("checkCamera")==None:
                noderedResponse = getnodered(noderedPayload, cameraNumber)
            else:
                noderedResponse = checkCamera(cameraNumber)
            

    
    return {
        "body": {
            "success": success,
            "message": message, 
            "noderedResponse": noderedResponse,
            "commandType": commandType
        }
    }
def verifyUser(username, password, role):
    #Verify the user/pass combination
    #Calculate hashed password
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()
    #Begin accessing the database
    cloudant_api_key = "bsideentsamedgediabsidst"
    cloudand_password = "27412e333c315bfc445b9dacf112ec5b2ec00878"
    cloudant_account = 	"5d99de7b-6366-4dce-829c-1055baad93e6-bluemix"
    db_name = "user-db"
    
    client = cloudant.Cloudant(cloudant_api_key, cloudand_password, account=cloudant_account, connect=True, auto_renew=True)
    db = client[db_name]
    #Determine usage
    id = role+':'+username
    
    if id in db:
        doc = db[id]
        #Recalculate hashed password
        salt = doc['salt']
        hashed_password = hashlib.sha512(str(password + salt).encode('utf-8')).hexdigest()
        if hashed_password == doc['hashed_password']:
            role = doc['role']
            success = True
            message = 'Successfully logged in as user: '+username+' with role: '+role+'.'
        else:
            success = False
            message = 'Failed to login. Password incorrect.'
    else:
        success = False
        message = 'Failed to login. Username with that role not found.'
    
    client.disconnect()
    
    return success, message
    
def getnodered(noderedPayload, cameraNumber):
    
    url = "https://connectedfarmsnodered.mybluemix.net/command"+cameraNumber
    headers = {
        'accept': 'application/json',
        'Content-Type': "application/x-www-form-urlencoded"
    }
    
    

    
    response = requests.post(url, headers=headers, data=noderedPayload)
    
    return response.status_code
    
def checkCamera(cameraNumber):
    
    url = "https://connectedfarmsnodered.mybluemix.net/camera"+cameraNumber
    headers = {
        'accept': 'application/json',
        

    }
    
    #response = requests.get(url, headers=headers, timeout=10, data="")

    #return True
    conn = http.client.HTTPSConnection("connectedfarmsnodered.mybluemix.net")

    payload = ""

    conn.request("GET", "/camera"+cameraNumber, payload)

    res = conn.getresponse()
    data = res.read()

    return(data.decode("utf-8"))

