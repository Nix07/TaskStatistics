import requests
import json
import datetime
from dateutil.relativedelta import relativedelta
import sys


"""
Idea:
-> Get the api-token, username and month as input.
-> Get phId using "user.search".
-> Get all the subscribed tasks of the user using "maniphest.search".
-> Using "maniphest.gettasktransactions" get the subscription date. 
-> Using the input month, count the number of subscription week-wise. 
"""


def check_python3():
	"""Check that Python 3 is used for execution."""
	pythonVersion = sys.version_info[:3]
	return (pythonVersion[0] == 3)


def get_phId(userName, apiToken):
	"""Fetch the phId corresponding to the username."""
	data = {
  		'api.token': apiToken,
  		'constraints[usernames][0]': userName
	}

	response = requests.post(
		'https://phabricator.wikimedia.org/api/user.search', data=data)
	try:
		json_response = json.loads(response.text)
		return json_response['result']['data'][0]['phid']
	except:
		return -1


def get_tasksId(userName, apiToken):
	"""Fetch all the subscribed tasks of the user corresponding to the username."""
	data = {
	  'api.token': apiToken,
	  'constraints[subscribers][0]': userName,
  	  'order[order]': 'id'
	}

	response = requests.post(
		'https://phabricator.wikimedia.org/api/maniphest.search', data=data)
	try:
		json_response = json.loads(response.text)
		
		tasksId = []
		for each in json_response['result']['data']:
			tasksId.append(int(each["id"]))
		return tasksId
	except:
		return -1


def get_date_of_subscription(taskId, phId, apiToken):
	"""Fetch date of subscription for the task corresponding to taskId."""
	data = {
  		'api.token': apiToken,
  		'ids[0]': taskId
	}

	response = requests.post(
		'https://phabricator.wikimedia.org/api/maniphest.gettasktransactions', 
		data=data)
	try:
		json_response = json.loads(response.text)
		for each in json_response['result'][str(taskId)]:
			if each["transactionType"] == "core:subscribers":
				if phId not in each['oldValue'] and phId in each["newValue"]:
					return each["dateCreated"]
	except:
		print('Error occured while fetching subscription date!')
		return -1


def create_timeFrame(timeFrame):
	"""Check the validity of entered date."""
	try:
		month = int(timeFrame[0:2])
		if timeFrame[2] != '-':
			raise
		year = int(timeFrame[3:7])
		return datetime.datetime(year, month, 1)
	except:
		print('Invalid Date!')
		return 1


if __name__ == '__main__':
	"""Command line entry point."""
	taskSubscribedDate = {}
	date = 1

	if check_python3():
		apiToken = input('Enter the API Token: ')
		userName = input('Enter the username: ')
		while date == 1:
			timeFrame = input('Enter the month and year (MM-YYYY): ')
			date = create_timeFrame(timeFrame)

		phId = get_phId(userName, apiToken)
		if phId != -1:
			subscribedTasksId = get_tasksId(userName, apiToken)
			if subscribedTasksId != -1:
				for taskId in subscribedTasksId:
					taskSubscribedDate[taskId] = (
						datetime.datetime.fromtimestamp(
							int(get_date_of_subscription(taskId, phId, 
														 apiToken)))
						)

				endDate = date + relativedelta(months=1)
				date = date + relativedelta(weeks=1)
				weekCount = 1
				print('+------+----------------+')
				print('| Week |  Subscription  |')
				print('+------+----------------+')
				while date <= endDate:
					count = 0
					for taskId, subsciptionDate in taskSubscribedDate.items():
						if subsciptionDate <= date:
							count += 1
					print('|  ' + str(weekCount) + '   |' + 
						  '       ' + str(count) + '{}'.format('       |' 
						  if count > 9 else '        |'))
					weekCount += 1 
				
					date += datetime.timedelta(weeks=1)	

				print('+------+----------------+')
			else:
				print('Error occured while fetching tasks Ids!')
		else:
			print('Error occured while fetching phId!')
	else:
		print('Please use Python 3')