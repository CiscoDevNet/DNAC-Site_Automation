import requests
import json
import sys
import time
import logging
import time

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

def get_site_info(timestamp):
    return get_url("intent/api/v1/site-health?timestamp=" + str(timestamp))

def get_device_ip_address(serial_number):
    device_detail = get_url("intent/api/v1/network-device/serial-number/" + serial_number)
    return device_detail["response"]["managementIpAddress"]

def add_device_to_site(site_id, device_ipAddress):
    payload = {
       "device": [
	   {
            "ip": device_ipAddress
           }
       ]
    }
 
    print(json.dumps(payload))
    result = post_url("intent/api/v1/site/" + site_id + "/device", payload)
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

site_to_id = {}

print "Input File Name: " + sys.argv[1]

with open(sys.argv[1]) as f:
    data = json.load(f)

print "Curent time: " + str(int(time.time() * 1000)) + " milliseconds"

siteInfo = get_site_info(int(time.time() * 1000))

for site in siteInfo['response']:
    site_to_id[site["siteName"]] = site["siteId"]

for key in data["device"]:
    print key["serialNumber"], key["siteName"]
    ip_address = get_device_ip_address(key["serialNumber"])
    print "Site Id :" + site_to_id[key["siteName"]]
    print "Device IP Address :" + ip_address
    response = add_device_to_site(site_to_id[key["siteName"]], ip_address)
    print(json.dumps(response))
    time.sleep(20)

print "\n\n---------- Adding Devices to Site  complete !! ----------\n\n"
