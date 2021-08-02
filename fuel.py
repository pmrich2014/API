#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 21:17:07 2021

@author: paulrichardson

Script pulls data from api and writes the data to a CSV file

Command Line Usage:
    With Arguments:
        python fuel.py -s '2021-01-01' -e '2021-01-31' -o 'contactData.csv'

    Using defaults:
        python fuel.py

    Help for arguments:
        python fuel.py -h
"""
import requests
import pandas as pd
import argparse
import sys
from datetime import date
import calendar

def getDates():
    # current year
    year = int(date.today().strftime("%Y"))
    # current month
    month = int(date.today().strftime("%m"))
    # last day of month
    lastDay = calendar.monthrange(year, month)[1]

    # default start and end date
    defaultSD = f'{year}-{month}-01' # first day of the month
    defaultED = f'{year}-{month}-{lastDay}' # last day of the month

    return defaultSD, defaultED

def validateArguments(defaultSD, defaultED):

    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()

    # query start date
    ap.add_argument("-s", "--startDate", default=defaultSD,
                help='Start date for API query YYYY-MM-DD. Default is last day of the month.')

    # query end date
    ap.add_argument("-e", "--endDate", default=defaultED,
                help='End date for API query YYYY-MM-DD. Defaults to first day of the month.')

    # query output filename
    ap.add_argument("-o", "--outputFile", default='contactData.csv',
                help= "File name for .csv output file. Default is contactData.csv")

    ap.add_argument("-v", "--verbose", default=1,
                help= "Turn script summary ON (1) or OFF (0).")

    # get arguments
    args = vars(ap.parse_args())

    # exit system if filename invalid
    filename = args['outputFile']

    if not filename.lower().endswith('csv'):
        sys.stderr.write(f'\n **** Output file must end with .csv - invalid filename: {filename} ****\n')
        sys.exit(1)  

    # Script parameters
    outputFile = args['outputFile']
    verbose = args['verbose']

    # Query Parameters
    startDate = args['startDate'] # start date
    endDate = args['endDate'] # end date
    token = 'XXXXXXXX-XXXXX-XXXXXXX-XXXXXXXX' # api creditionals

    #build url query
    url = f"https://leads.theonenet.work/api/api.cfm/{token}/avhdata/range?startdate={startDate}&enddate={endDate}"

    return url, startDate, endDate, outputFile, verbose

def apiCall(url):

    # response from api
    response = requests.get(url)

    # if successful write data to file
    if response.status_code == 200:
        # convert to json
        jsonData = response.json()
        return jsonData

    else:
        sys.stderr.write("\n **** Request to API Failed ****\n\n")
        sys.exit(1)


def writeCSV(jsonFile, outputFile):
    # parse data
    contactData = jsonFile['DATA']

    # convert to data frame
    df = pd.DataFrame(contactData)

    # number of reords
    numRecords = len(df)

    # if df is not empty
    if numRecords != 0:
        # write to csv
        df.to_csv(outputFile)
        return numRecords
    else:
        sys.stderr.write("\n **** No records returned. No file created. Check query dates. ****\n\n")
        sys.exit(1)

# Program Start / Execution

# step 1 - get default dates for current month
startDate, endDate = getDates()

# step 2 - get command line arguments
url, startDate, endDate, outputFile, verbose = validateArguments(startDate, endDate)

# step 3 - call api
jsonData = apiCall(url)

# step 4 - write file
numRecords = writeCSV(jsonData, outputFile)

if verbose == 1:
    # write output
    print('\n****************************************************')
    print(f'\n     File name created: {outputFile}')
    print(f'     Number of records: {numRecords}')
    print(f'     For Date Range: {startDate} TO {endDate}\n')
    print('****************************************************\n')
