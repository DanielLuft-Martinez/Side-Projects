#!/usr/bin/env python
# coding: utf-8

# In[1]:


# standard comments and imports
# jsut the basics
import string
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import random
import datetime
import boto3

#
import argparse
import re
import os
import shutil

# In[ ]:


"""
So far this has mostly been a follow allong, which is all well and good. A nice warm up, with some fun api usage.
Now to put a little bit of spin on it.
"""

"""
Ideally, it should be a fully functioning script.
This means, proper inputs and optionals. File and Dir handling. Error handling. 
Maybe some other interesting features, while staying within the scope.
"""
"""
As a new more interesting project has come to mind, I'd like to get this to a stopping point asap.
and as such, all options and args will be read in by file rather then by a tedium of cli options
so now we'll just run it with 
prog.py filename
and be done with it... at least for now.
though to be honest this project holds very little intrigue
"""

# In[ ]:





# In[39]:
try:

	parser = argparse.ArgumentParser(prog='stockvisualizer.py', 
		description = 'Retrieve and Visualize lookback data for selected stocks.\n\r curretnly uses a config file',
		usage='%(prog)s config [options]')

	parser.add_argument('config', help='the config file')
	
	# gonna leave these here for future deving, but probably useless
	parser.add_argument('-A','--AMAZON', action='store_true', help='Upload results to an Amazon s3 bucket')
	parser.add_argument('-c','--clean', action='store_true', help='run cleanly in current dir, leaving no extra files or dirs')
	parser.add_argument('-f','--file', action='store_true', help='take stock args from file input instead')
	parser.add_argument('-l','--lookback-length', action='store_true', help='the number of {scale} to lookback and retrieve data.\n\r single integer.\n\r often limited by iexcloud api.')
	parser.add_argument('-s','--lookback-scale', action='store_true', help='the lettter of {scale} to lookback and retrieve data.\n\r choices:\n\r m (month)\n\r d (day) \n\r y (year)\n\r often limited by iexcloud api.')
	parser.add_argument('-u','--unique', action='store_true', help='uniquely date output files')



	args = parser.parse_args()
	
	
	config = open(args.config, 'r')
	
	





	plt.rc('figure', figsize=(40, 40))


	# In[3]:
	
	
	
	# burn some lines in an ugly manor
	config.readline()
	config.readline()
	config.readline()
	
	# api keys
	
	# use iex cloud SANDBOX for testing iexcloud.sandbox.key.txt'
	# use iex cloud for metered use iexcloud.key.txt'

	# IEX
	iex_api_key_file = config.readline().strip()
	IEX_API_KEY = ""
	with open(iex_api_key_file, 'r') as file:
		IEX_API_KEY = file.readline()

	config.readline()
	# AWS
	aws_api_key_file = config.readline().strip()
	AWS_ACCESS_KEY = ''
	AWS_SECRET_KEY = ''
	with open(aws_api_key_file, 'r') as file:
		AWS_ACCESS_KEY  =  file.readline()[15:-1]
		AWS_SECRET_KEY = file.readline()[13:]

	session = boto3.Session(
	aws_access_key_id=AWS_ACCESS_KEY,
	aws_secret_access_key=AWS_SECRET_KEY
	)

	# aws bucket name
	config.readline()
	bucket = config.readline().rstrip()

	# In[30]:



	# EDIT HERE
	config.readline()
	tickers = config.readline().strip().split(",")

	# MATCHING CONSTANTS
	config.readline()
	COMPANY_TYPES = config.readline().rstrip()
	config.readline()
	grouping = config.readline().rstrip()

	config.readline()
	LOOKBACK_LENGTH = config.readline().rstrip()
	config.readline()
	years = config.readline().rstrip()

	

	# In[31]:

	dirname = f'{grouping}_data_imgs'
	os.mkdir(dirname)


	# In[32]:


	tickers_string = ''
	for x in tickers:
		tickers_string += x+","
	tickers_string = tickers_string[:-1]

	# """AGREGATE DESIRED TICKERS"""
	tickers_string


	# In[33]:


	# creating endpoints
	endpoints = 'chart'
	# limited by paywall

	# form http request
	HTTP_req = f'https://cloud.iexapis.com/stable/stock/market/batch?symbols={tickers_string}&types={endpoints}&range={years}&token={IEX_API_KEY}'
	
	config.readline()
	sandbox = config.readline().rstrip()
	if(sandbox == "sandbox"):
		# sandbox url for testing
		HTTP_req = f'https://sandbox.iexapis.com/stable/stock/market/batch?symbols={tickers_string}&types={endpoints}&range={years}&token={IEX_API_KEY}'


	# In[35]:


	data = pd.read_json(HTTP_req)


	# In[36]:


	series_dict = {}

	for ticker in tickers:
		series_dict.update({ticker : pd.DataFrame(data[ticker]['chart'])['close']})
		
	series_list = [pd.DataFrame(data[ticker]['chart'])['close'] for ticker in tickers]

	series_list.append(pd.DataFrame(data[ticker]['chart'])['date'])
								
	col_names = tickers.copy()
	col_names.append('Date')
			
	data_concat = data.copy()
	data_concat = pd.concat(series_list, axis=1)
		
	data_concat.columns = col_names

	data_concat
	data_concat.set_index('Date', inplace = True)


	# In[37]:

	# ?!?!@?
	# get_ipython().run_line_magic('matplotlib', 'inline')


	# In[ ]:





	# In[40]:


	fig = plt.figure()


	ax = fig.add_subplot(111)

	ax.boxplot(data_concat.T)

	plt.title(f'Boxplot of {COMPANY_TYPES} Stock Prices ({LOOKBACK_LENGTH} lookback)', fontsize = 50)

	ticks = range(1, len(data.columns)+1)
	labels = list(data.columns)




	plt.xticks(ticks,labels, fontsize = 50)
	plt.yticks(fontsize = 50)





	ax.plot([1],[1])
	ax.tick_params(top='off', bottom='off', left='off', right='off', labelleft='on', labelbottom='on')

	today = datetime.datetime.now()

	fig.savefig(f'{grouping}_data_imgs/boxplot-{str(today.date())}.png')
	
	fig.clear()
	plt.clf()
	plt.close(fig)
	plt.close()
	

	# In[41]:


	dates_full = data_concat.index.to_series()
	dates_full = [str(pd.to_datetime(d)) for d in dates_full]


	# In[42]:


	if 'y' in years:
		dates = [ str(x[5:-9]+'-'+x[2:4]).replace("-",'/') for x in dates_full]
		range_points = []
		month = ''
		for i,d in enumerate(dates):
			if month == '':
				month = d[0:2]
				range_points.append(i)
			if month != d[0:2]:
				month = d[0:2]
				range_points.append(i)
		labels = True        
		if len(range_points) > 12:
	#         labels = False
			less_points = []
			for i,p in enumerate(range_points):
				if i%(int(len(range_points)/12)) == 0:
					less_points.append(p)
			range_points = less_points[:]
	else:
		dates = [ str(x[5:-9]+'-'+x[2:4]).replace("-",'/') for x in dates_full]
		range_points = [0]
		mdec = len(dates)/10
		for i,d in enumerate(dates):
			if len(d) % mdec == 0:
				range_points.append(i)


	# In[43]:




	for ticker in tickers:
		stock_prices = data_concat[ticker]    

		#Add titles to the chart and axes
		plt.title(f'{COMPANY_TYPES} Stock Pricees ({LOOKBACK_LENGTH} Lookback)', fontsize=50)
		plt.ylabel("Stock Price", fontsize=50)
		plt.xlabel("Date", fontsize=50)
		plt.xticks(range_points[1:], fontsize = 35)
		plt.yticks(fontsize=45)
	   

		#Generate the plot
		plt.plot(dates, stock_prices, linewidth=7.0) 
	  
		
		plt.legend(tickers,fontsize = 40)
		
		
	today = datetime.datetime.now()

	plt.savefig(f'{grouping}_data_imgs/lineplot-{str(today.date())}.png')
	
	
	plt.clf()
	plt.close()

	# In[44]:


	plt.hist(data_concat.transpose(), bins = 50, rwidth=1)
	plt.legend(data.columns,fontsize=50)
	plt.title(f'A Histogram of Daily Closing {COMPANY_TYPES} Prices ({LOOKBACK_LENGTH} Lookback)', fontsize = 50)
	plt.ylabel("Observations", fontsize = 50)
	plt.xlabel("Stock Prices", fontsize = 50)
	plt.xticks(fontsize = 45)
	plt.yticks(fontsize=45)


	today = datetime.datetime.now()

	plt.savefig(f'{grouping}_data_imgs/histogram-{str(today.date())}.png')
	
	plt.clf()
	plt.close()


	# In[45]:


	s3 = session.resource('s3')
	s3.meta.client.upload_file(f'{grouping}_data_imgs/boxplot-{str(today.date())}.png', 
							   bucket, 
							   f'{grouping}_data_imgs/boxplot-{str(today.date())}.png', 
							   ExtraArgs={'ACL':'public-read'})
	s3.meta.client.upload_file(f'{grouping}_data_imgs/lineplot-{str(today.date())}.png', 
							   bucket, 
							   f'{grouping}_data_imgs/lineplot-{str(today.date())}.png', 
							   ExtraArgs={'ACL':'public-read'})
	s3.meta.client.upload_file(f'{grouping}_data_imgs/histogram-{str(today.date())}.png', 
							   bucket, 
							   f'{grouping}_data_imgs/histogram-{str(today.date())}.png', 
							   ExtraArgs={'ACL':'public-read'})


	# In[197]:
except Exception as e:
	print(e)

# this is some pretty lazy error handling, but it technicly counts




	# In[ ]:





	# In[ ]:




