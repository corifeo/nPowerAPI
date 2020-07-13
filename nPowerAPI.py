#!/usr/bin/env python

import requests
import base64
import datetime
import json


INVOICES = False
MONTHLY_USAGE = False

# Fill your credentials in the authentication payload
payload = {
'userid':'',
'password':''
}

# API authentication header is your username in b64
cookieName = base64.b64encode(str.encode(payload['userid'])).decode().strip('=')

headers =  {
    'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
}

session = requests.Session()
login = session.post('https://www.npower.com/at_home/applications/npower.web.login/api/session', data=payload, headers=headers)
config = session.get('https://www.npower.com/apps/config.json', headers=headers, cookies=login.cookies)
headers['Authorization'] = login.cookies[cookieName]

apilogin = session.get('https://api2.npower.com/authenticate/check', headers=headers)
contract = session.get('https://api2.npower.com/contractaccount', headers=headers)
contract_detail = contract.json()

# List all contract associated with the account
for contract in contract_detail:
    print('Found contract {} for customer {} with and status {}'.format(contract['Number'], contract['BPN'], contract['Status']))

contract_id = contract_detail[0]['Number']
today = datetime.datetime.today()
start_period = today - datetime.timedelta(days=180)

info_customer = session.get('https://api2.npower.com/customer/{}'.format(contract_id), headers=headers)
user_detail = info_customer.json()
print('Hi {} {}, customer number {}'.format(user_detail[0]['Firstname'], user_detail[0]['Lastname'], user_detail[0]['BPN'],))

if INVOICES:
    invoices = session.get('https://api2.npower.com/transaction/invoices/{}'.format(contract_id), headers=headers) 
    invoices_list = invoices.json()
    for invoice in invoices_list:
        print('Invoce from {} to {} for amount {}'.format(invoice['From'], invoice['To'], invoice['Amount']))

if MONTHLY_USAGE:
    monthlyusage = session.get('https://api2.npower.com/SmartInsights/{}/monthlyusageforyear?year={}'.format(contract_id, today.year), headers=headers) 
    usage_detail = monthlyusage.json()

    for fuel_type in usage_detail['FuelData']:
        for entry in fuel_type['Data']:
            print('Fuel: {}, Year: {}, Month: {}, Usage: {}, Estimated: {}'.format(fuel_type['Fuel'], usage_detail['Year'], entry['Month'], 
                                                                                entry['Consumption'], entry['IsEstimated']))

readings = session.get('https://api2.npower.com/usage/{}?from={}&to={}'.format(contract_id, start_period.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')), headers=headers) 
meter_readings = readings.json()

for meter in meter_readings:
    print('Contract: {}, Meter: {}'.format(meter['ContractNumber'], meter['SerialNumber']))
    for read in meter['MeterReads']:
        print('Date: {}, Type: {}, Read: {}, Plausible: {}'.format(read['ReadingDate'], read['ReadingType'], read['Reading'], read['IsPlausible']))

meter_info = session.get('https://api2.npower.com/usage/{}/meterinformation'.format(contract_id), headers=headers) 
meter_list = meter_info.json()

for meter in meter_list['MeterInformations']:
    print('Contract: {}, Meter: {}, Fuel: {} MPXN: {}'.format(meter['ContractNo'], meter['SerialNo'], meter['FuelType'], meter['MPXN']))
