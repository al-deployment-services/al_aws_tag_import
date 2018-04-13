#Original code : https://github.com/ryanholland/tools
from __future__ import print_function
from datetime import datetime
import boto3, json, requests, os
from base64 import b64decode

#request API call static Params
HEADERS = {'content-type': 'application/json'}
ALERT_LOGIC_API_URL = ''
ALERT_LOGIC_LOG_API_URL = ''
ALERT_LOGIC_TM_API_URL = ''

#Alert Logic source tag is a single value, while AWS has K:V based tags
#change to True if you want to capture both Key and Value, false is just value
USE_TAG_DELIMITER = True

#If set to true this is the char that will seperate the key and value in Alert Logic UI
#you can customize this char
DELIMITER = ":"
#format AWS tags for Alert Logic consumption and overrite tags on Alert Logic sources
#use the AWS instance "Name" for Alert Logic source name

def update_appliance_name(id, tags, API_KEY, ec2_instance_id):
	name = ec2_instance_id
	newTag = ""
	for tag in tags:
		if tag['Key'] != 'Name':
			if newTag != "":
				newTag =  newTag + ','
			newTag =  newTag + '{"name":'
			if USE_TAG_DELIMITER:
				newTag = newTag + '"' + tag['Key'] + DELIMITER + tag['Value']
			else:
				newTag = newTag + '"' + tag['Key'] + " " + tag['Value']
			newTag = newTag + '"}'
		else:
			name = str(tag['Value'])

	if newTag == "":
		tag_update = json.dumps({"appliance": {"name": name}})
	else:
		jsonNewTag = '{"appliance":{"name":"'+str(name)+'","tags": ['+str(newTag)+']}}'
		tag_update = json.loads(jsonNewTag)
		tag_update = json.dumps(tag_update)

	R = requests.post(ALERT_LOGIC_TM_API_URL + str(id), headers=HEADERS, auth=(API_KEY,''),data = tag_update)
	return R.status_code

def update_source_name(id, tags, API_KEY, ec2_instance_id):
	name = ec2_instance_id
	newTag = ""
	for tag in tags:
		if tag['Key'] != 'Name':
			if newTag != "":
				newTag =  newTag + ','
			newTag =  newTag + '{"name":'
			if USE_TAG_DELIMITER:
				newTag = newTag + '"' + tag['Key'] + DELIMITER + tag['Value']
			else:
				newTag = newTag + '"' + tag['Key'] + " " + tag['Value']
			newTag = newTag + '"}'
		else:
			name = str(tag['Value'])

	if newTag == "":
		tag_update = json.dumps({"protectedhost": {"name": name}})
	else:
		jsonNewTag = '{"protectedhost":{"name":"'+str(name)+'","tags": ['+str(newTag)+']}}'
		tag_update = json.loads(jsonNewTag)
		tag_update = json.dumps(tag_update)
	R = requests.post(ALERT_LOGIC_API_URL + str(id), headers=HEADERS, auth=(API_KEY,''),data = tag_update)
	return R.status_code

def get_log_source(instance_id, API_KEY):
	params = {'search': instance_id}
	R = requests.get(ALERT_LOGIC_LOG_API_URL, params=params, headers=HEADERS, auth=(API_KEY, ''))
	output = R.json()
	if output is None:
		print ("Recieved invalid JSON for query to Log API for instance-id: %s \n Requests Output: %s" % (instance_id, R.text))
		return None, False
	if output['sources']:
		if 'syslog' in output['sources'][0]:
			return output['sources'][0]['syslog']['id'], False
		elif 'eventlog' in output['sources'][0]:
			return output['sources'][0]['eventlog']['id'], True
	return None, False

def update_log_source_name(id, tags, isWin, API_KEY, ec2_instance_id):
	name = ec2_instance_id
	newTag = ""
	for tag in tags:
		if tag['Key'] != 'Name':
			if newTag != "":
				newTag =  newTag + ','
			newTag =  newTag + '{"name":'
			if USE_TAG_DELIMITER:
				newTag = newTag + '"' + tag['Key'] + DELIMITER + tag['Value']
			else:
				newTag = newTag + '"' + tag['Key'] + " " + tag['Value']
			newTag = newTag + '"}'
		else:
			name = str(tag['Value'])
	if not isWin:
		if newTag == "":
			tag_update = json.dumps({"syslog": {"name": name, "method" : "agent"}})
		else:
			jsonNewTag = '{"syslog":{"name":"'+str(name)+'","method": "agent", "tags": ['+str(newTag)+']}}'
			tag_update = json.loads(jsonNewTag)
			tag_update = json.dumps(tag_update)
		R = requests.post(ALERT_LOGIC_LOG_API_URL + '/syslog/' + str(id), headers=HEADERS, auth=(API_KEY,''),data = tag_update)
		return R.status_code

	else:
		if newTag == "":
			tag_update = json.dumps({"eventlog": {"name": name}})
		else:
			jsonNewTag = '{"eventlog":{"name":"'+str(name)+'", "tags": ['+str(newTag)+']}}'
			tag_update = json.loads(jsonNewTag)
			tag_update = json.dumps(tag_update)
		R = requests.post(ALERT_LOGIC_LOG_API_URL + '/eventlog/' + str(id), headers=HEADERS, auth=(API_KEY,''),data = tag_update)
		return R.status_code


def lambda_handler(event, context):
	CUST_ID = os.environ["CID"]
	DC = os.environ["DC"]
	REPLACE = os.environ["REPLACE"]

	event['apikey'] = boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ["API_KEY"]))['Plaintext']
	global ALERT_LOGIC_API_URL, ALERT_LOGIC_LOG_API_URL, ALERT_LOGIC_TM_API_URL
	if DC == "DENVER":
		ALERT_LOGIC_API_URL = 'https://publicapi.alertlogic.net/api/tm/v1/' + CUST_ID +'/protectedhosts/'
		ALERT_LOGIC_LOG_API_URL = 'https://publicapi.alertlogic.net/api/lm/v1/' + CUST_ID + '/sources/'
		ALERT_LOGIC_TM_API_URL = 'https://publicapi.alertlogic.net/api/tm/v1/' + CUST_ID +'/appliances/'

	elif DC == "ASHBURN":
		ALERT_LOGIC_API_URL = 'https://publicapi.alertlogic.com/api/tm/v1/' + CUST_ID +'/protectedhosts/'
		ALERT_LOGIC_LOG_API_URL = 'https://publicapi.alertlogic.com/api/lm/v1/' + CUST_ID + '/sources/'
		ALERT_LOGIC_TM_API_URL = 'https://publicapi.alertlogic.com/api/tm/v1/' + CUST_ID +'/appliances/'

	elif DC == "NEWPORT":
		ALERT_LOGIC_API_URL = 'https://publicapi.alertlogic.co.uk/api/tm/v1/' + CUST_ID +'/protectedhosts/'
		ALERT_LOGIC_LOG_API_URL = 'https://publicapi.alertlogic.co.uk/api/lm/v1/' + CUST_ID + '/sources/'
		ALERT_LOGIC_TM_API_URL = 'https://publicapi.alertlogic.co.uk/api/tm/v1/' + CUST_ID +'/appliances/'

	list_of_aws_ec2 = []
	number_of_updates = 0
	number_of_failed_updates = 0
	number_of_log_updates = 0
	number_of_tm_updates = 0
	number_of_failed_log_updates = 0
	number_of_failed_tm_updates = 0
	client = boto3.client('ec2')
	regions = client.describe_regions()
	#loop through all region and store the instance metadata
	print ("Script start, pulling all regions : " + str(datetime.now()))
	for region in regions['Regions']:
		client = boto3.client('ec2', region_name=region['RegionName'])
		reservations = client.describe_instances()
		for res in reservations['Reservations']:
			for inst in res['Instances']:
				if 'Tags' in inst.keys():
					list_of_aws_ec2.append(inst)

	#call Alert Logic sources API and get sources detail
	print ("Starting API calls : " + str(datetime.now()))
	params = {'search': 'i-'}
	if(len(list_of_aws_ec2) == 0 ):   #skip hitting our API if there's no instance in the AWS account
			print("Skipping as EC2 returned no instances in this AWS account")
	else:
		R = requests.get(ALERT_LOGIC_API_URL, params=params, headers=HEADERS, auth=(event['apikey'], ''))
		output = R.json()

		#R = requests.get(ALERT_LOGIC_TM_API_URL, params=params, headers=HEADERS, auth=(event['apikey'], ''))
		R = requests.get(ALERT_LOGIC_TM_API_URL, params=params, headers=HEADERS, auth=(event['apikey'], ''))
		tm_output = R.json()

		#proccess AWS instances looking for matches in Alert Logic (by instance ID)
		if output["protectedhosts"]:
			index = 0
			for index in range(len(output["protectedhosts"])):
				if (len(output["protectedhosts"][index]["protectedhost"]["tags"]) == 0) or (REPLACE == 'True'):
					#make sure PHOST has instance ID metadata
					if 'ec2_instance_id' in output["protectedhosts"][index]["protectedhost"]["metadata"]:
						#search for ec2 instance with similar metadata
						loop_counter=0
						for x in list_of_aws_ec2:
							loop_counter = loop_counter + 1
							if x['InstanceId'] == output["protectedhosts"][index]["protectedhost"]["metadata"]["ec2_instance_id"] :
								if len(x['Tags']) > 0:
									phost_update = x
									tempID = output["protectedhosts"][index]["protectedhost"]["id"]
									#get corresponding log sources ID for the instance
									logID, isWin = get_log_source(output["protectedhosts"][index]["protectedhost"]["metadata"]["ec2_instance_id"],event['apikey'])
									# call update tags and store httpcode
									httpCode = update_source_name(tempID,phost_update['Tags'],event['apikey'], x['InstanceId'])
									httpCodeLog = ""
									# call update to sources DB for LM
									if logID is not None:
										httpCodeLog = update_log_source_name(logID, phost_update['Tags'], isWin,event['apikey'], x['InstanceId'])
									if httpCode == 200:
										number_of_updates = number_of_updates + 1
									if httpCode == 400 or httpCode == 500:
										number_of_failed_updates = number_of_failed_updates + 1
										print ("Update of Instance: %s using Protected Host ID: %s failed with return code: %s" % (output["protectedhosts"][index]["protectedhost"]["metadata"]["ec2_instance_id"], tempID, str(httpCode)))
									if httpCodeLog == 200:
										number_of_log_updates = number_of_log_updates + 1
									if httpCodeLog == 400 or httpCodeLog == 500:
										number_of_failed_updates = number_of_failed_updates + 1
										print ("Update of Instance: %s using Log Source ID: %s failed with return code: %s" % (output["protectedhosts"][index]["protectedhost"]["metadata"]["ec2_instance_id"], logID, str(httpCode)))
									break

		if tm_output["appliances"]:
			index = 0
			for index in range(len(tm_output["appliances"])):
				if (len(tm_output["appliances"][index]["appliance"]["tags"]) == 0) or (REPLACE == 'True'):
					#make sure APPLIANCE has instance ID metadata
					if 'ec2_instance_id' in tm_output["appliances"][index]["appliance"]["metadata"]:
						#search for ec2 instance with similar metadata
						loop_counter=0
						for x in list_of_aws_ec2:
							loop_counter = loop_counter + 1
							if x['InstanceId'] == tm_output["appliances"][index]["appliance"]["metadata"]["ec2_instance_id"] :
								if len(x['Tags']) > 0:
									tm_update = x
									tempID = tm_output["appliances"][index]["appliance"]["id"]
									# call update tags and store httpcode
									httpCode = update_appliance_name(tempID,tm_update['Tags'],event['apikey'], tm_update['InstanceId'])
									if httpCode == 200:
										number_of_tm_updates = number_of_tm_updates + 1
									if httpCode == 400 or httpCode == 500:
										number_of_failed_tm_updates = number_of_failed_tm_updates + 1
										print ("Update of Instance: %s using Appliance ID: %s failed with return code: %s" % (tm_output["appliances"][index]["appliance"]["metadata"]["ec2_instance_id"], tempID, str(httpCode)))
									break

	print ("Script ended : " + str(datetime.now()))
	return "Successfully updated " + str(number_of_updates ) + " protectedhosts and " + str(number_of_log_updates) + " log sources. " + str(number_of_failed_updates) + " failed protectedhosts and " + str(number_of_failed_log_updates) + " failed log sources" + " and successfully updated " + str(number_of_tm_updates ) + " appliances and " + str(number_of_failed_tm_updates) + " failed appliances"
