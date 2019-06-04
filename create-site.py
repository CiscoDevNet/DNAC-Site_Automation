import requests
import json
import sys
import time
import logging

from dnac_config import DNAC, DNAC_PORT, DNAC_USER, DNAC_PASSWORD
from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()

# -------------------------------------------------------------------
# Custom exception definitions
# -------------------------------------------------------------------
class TaskTimeoutError(Exception):
    pass

class TaskError(Exception):
    pass

# API ENDPOINTS
ENDPOINT_TICKET = "ticket"
ENDPOINT_TASK_SUMMARY ="task/%s"
RETRY_INTERVAL=2

# -------------------------------------------------------------------
# Site Create functions - Area, Building, Floor(to be added)
# -------------------------------------------------------------------

def create_area_request(area_name, area_parentName):
    payload = {
    "type": "area",
    	"site": {
            "area": {
            	"name": area_name,
            	"parentName": area_parentName
            }
    	}
    }
    
    print(json.dumps(payload))
    result = post_url("system/api/v1/site", payload)
    return result

def create_bld_request(area_name, area_parentName, bld_name, bld_address):
    payload = {
    "type": "building",
        "site": {
            "area": {
                "name": area_name,
                "parentName": area_parentName
            },
            "building": {
                "name": bld_name,
                "address": bld_address
            }
        }
    }

    print(json.dumps(payload))
    result = post_url("system/api/v1/site", payload)
    return result

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def get_url(url):
    url = create_url(path=url)
    print(url)
    token = get_auth_token()
    headers = {'X-auth-token' : token['token']}
    try:
        response = requests.get(url, headers=headers, verify=False)
    except requests.exceptions.RequestException as cerror:
        print("Error processing request", cerror)
        sys.exit(1)

    return response.json()

def create_url(path, controller_ip=DNAC):
    """ Helper function to create a DNAC API endpoint URL
    """

    return "https://%s:%s/dna/%s" % (controller_ip, DNAC_PORT, path)

def get_auth_token(controller_ip=DNAC, username=DNAC_USER, password=DNAC_PASSWORD):
    """ Authenticates with controller and returns a token to be used in subsequent API invocations
    """

    login_url = "https://{0}:{1}/api/system/v1/auth/token".format(controller_ip, DNAC_PORT)
    result = requests.post(url=login_url, auth=HTTPBasicAuth(DNAC_USER, DNAC_PASSWORD), verify=False)
    result.raise_for_status()

    token = result.json()["Token"]
    return {
        "controller_ip": controller_ip,
        "token": token
    }

def post_url(url, payload):
    token = get_auth_token()
    url = create_url(path=url)
    headers= { 
	'x-auth-token': token['token'], 
	'content-type' : 'application/json',
	'__runsync': "true",
    	'__timeout': "30",
    	'__persistbapioutput': "true"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
    except requests.exceptions.RequestException  as cerror:
        print ("Error processing request", cerror)
        sys.exit(1)

    return response.json()

#-----------------------------------------
# Main function
#-----------------------------------------

print "File Name " + sys.argv[1]

with open(sys.argv[1]) as f:
    data = json.load(f)

for key in data["area"]:
    print key["name"], key["parentName"]
    response = create_area_request(key["name"], key["parentName"])
    print(json.dumps(response))

print "\n\n---------- Area Creation complete !! ----------\n\n"

for key in data["building"]:
    print key["area_name"], key["area_parentName"], key["bld_name"], key["bld_address"]
    response = create_bld_request(key["area_name"], key["area_parentName"], key["bld_name"], key["bld_address"])
    print(json.dumps(response))

print "\n\n---------- Building Creation complete !! ----------\n\n"

print "\n\n---------- Site Creation complete !! ----------\n\n"
