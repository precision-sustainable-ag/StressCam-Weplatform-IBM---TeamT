import cloudant, hashlib, uuid
'''
payload schema:
    body
        username: user's username
        password: user's password
        usage: determines what is the purpose of this call. Can be 'login' or 'create_account'.
        role: 'farmer' or 'researcher' or 'both'. Needed if the databse is partitioned. Otherwise would only need in create_account.
output schema:
    body
        success: Used by frontend to determine if login was a success. Can be True or False.
        message: string providing some description of how call went. If success is False, an error message will be here.
        role: the role of the user who successfully logged in or created an account. If success if False, role is invalid.
'''
def main(payload):
    #Parse payload
    username, password = str(payload['body'].get('username')), str(payload['body'].get('password'))
    usage, role = str(payload['body'].get('usage')), str(payload['body'].get('role'))
    
    success = False
    message = ''
    #Verify payload
    if username == "None" or password == "None" or usage == "None" or role == "None":#(usage == 'create_account' and role == None):
        success = False
        message = 'Payload is not valid. One of username, password, usage, or role is missing.'
    else:
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
        if usage == 'create_account':
            if id in db:
                success = False
                message = 'Failed to create user. Username already exists.'
            else:
                doc = db.create_document({
                    '_id':id,
                    'username':username,
                    'hashed_password': hashed_password,
                    'salt': salt,
                    'role': role,
                })
                success = True
                message = 'Successfully create user: "'+username+'".'
        elif usage == 'login':
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
        else:
            success = False
            message = 'Usage is not valid. Expected: login or create_account'
        client.disconnect()
    
    return {
        "body": {
                "success":success,
                "message":message,
                "role":role
            }    
        }

       

