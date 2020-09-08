import requests
import json
import cloudant, hashlib, uuid
def main(payload):
    #user verification
    #Parse payload
    username = str(payload['body'].get('username'))
    password = str(payload['body'].get('password'))
    role = str(payload['body'].get('role'))
    
    success = False
    message = ''
    sessionCode = ""
    schema = "..."
    #Verify payload
    if username == "None" or password == "None" or role == "None":
        success = False
        message = 'Payload is not valid. One of username, password, usage, or role is missing.'
    else:
        success, message = verifyUser(username, password, role)
        if success:
            sessionCode = getSessionCode()
          
            
    
    return {
        "body": {
            "success": success,
            "message": message,
            "sessionCode":sessionCode
          
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
def getSessionCode():
    url = 'https://dde-us-south.analytics.ibm.com/daas/v1/session'
    my_web_domain = 'https://connectedfarmsweb.mybluemix.net'#PUT YOUR WEBSITE HERE
    my_authorization = 'Basic ZGUyNTQ5MzAtNzBjNC00OGEyLWJmYWYtY2Q4MmNhZTkwYzViOjI1ZmE5N2ZjNDE5OGYwMzEzYTMxODEzOTJmNGNlZWFhYzQwNDIyYzU=',
                        #I think this came from using Swagger to create a sample cognos embedded session and using the authenitcation created there
                        #should start with: 'Basic (randomcharacters)...'
    headers = {
        'accept': 'application/json',
        'authorization': 'Basic ZGUyNTQ5MzAtNzBjNC00OGEyLWJmYWYtY2Q4MmNhZTkwYzViOjI1ZmE5N2ZjNDE5OGYwMzEzYTMxODEzOTJmNGNlZWFhYzQwNDIyYzU=',
        'Content-Type': 'application/json'
    }
    
    data = {
        "expiresIn": 3600,
        "webDomain": my_web_domain
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    return response.json()['sessionCode']