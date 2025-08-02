#!/usr/bin/env python3
# Helper script for onlinebrief24.de API
# 2025-07-29

""" check if the venv is activated 
    if active venv, sys.prefix != sys.base_prefix """
import sys
if sys.prefix == sys.base_prefix:
    print("ERROR: venv not activated")
    sys.exit(1)

""" check if .env file is present"""
import os
if not os.path.exists('.env'):
    print('ERROR: .env file missing.')
    sys.exit(1)

import argparse
import base64
import hashlib
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class OnlineBrief24API:

    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv('API_SECRET')
        self.base_url = "https://api.onlinebrief24.de/v1"
        self.headers = { 'Content-Type': 'application/json' }
        self.payload_auth = {
            'auth': {
                'apiKey': f'{self.api_key}',
                'apiSecret': f'{self.api_secret}',
                'mode': 'live'
                }
        }

    def balance(self):
        url = self.base_url + '/balance'
        response = requests.get(url, headers=self.headers, json=self.payload_auth)
        return f"Balance: {response.json()['data']['balance']} EUR"

    def list_invoices(self):
        url = self.base_url + '/invoices'
        response = requests.get(url, headers=self.headers, json=self.payload_auth)
        invoices = response.json()['data']['invoices']
        for inv in invoices:
            print(f"id: {inv['id']}, invoice date: {inv['invoice_date'].split(' ')[0]}")

    def get_invoice(self, invoice_id):
        url = self.base_url + f'/invoices/{invoice_id}'
        response = requests.get(url, headers=self.headers, json=self.payload_auth)
        invoice_date = response.json()['data']['invoice_date'].split(' ')[0]
        base64_data = response.json()['data']['base64_data']
        pdf_data = base64.b64decode(base64_data)
        pdf_filename = f"ob24-Rechnung-{invoice_date}.pdf"
        with open(pdf_filename, "wb") as file:
            file.write(pdf_data)
            print(f'Invoice successfully saved: {pdf_filename}')
    
    def open_pdf(self, pdf_filename):
        with open(f'{pdf_filename}', 'rb') as file:
            pdf_data = file.read()
        return pdf_data

    def base64_encode(self, pdf_data):
        return base64.b64encode(pdf_data).decode("utf8")

    def md5_checksum(self, base64_data):
        return hashlib.md5(base64_data.encode('utf-8')).hexdigest()

    def send_letter(self, pdf_filename, mode='live'):
        pdf_data = self.open_pdf(pdf_filename)
        base64_encoded = self.base64_encode(pdf_data)
        md5_checksum = self.md5_checksum(base64_encoded)

        payload = {
            **self.payload_auth,
            "letter": {
                "base64_file": base64_encoded,
                "base64_file_checksum": md5_checksum,
                "filename_original": os.path.basename(pdf_filename),
                "specification": {
                    "color": "1",
                    "mode": "simplex",
                    "shipping": "auto"
                }
            }
        }
        
        payload['auth']['mode'] = mode
        
        response = requests.post(f"{self.base_url}/printjobs", headers=self.headers, json=payload)

        if response.status_code == 200:
            print(f'Letter successfully submitted.')

            items = response.json()['data']['items'][0]
            print(f"Status: {items['status']}")
            print(f"Address: {items['address']}")
            print(f"Cost: {items['amount'] + items['vat']} EUR")
            print(self.balance())
           
        else:
            print(f'Response status code: {response.status_code}')
            return response.json()

    def list_printjobs(self, filter='all'):
        url = self.base_url + '/printjobs'
        match filter :
            case 'all':
                print('filter: all')
            case 'hold': # angehaltene Auftraege
                print('filter: hold')
                url += '?filter=hold'
            case 'done': # verarbeitete Auftraege
                print('filter: done')
                url += '?filter=done'
            case 'draft': # Aufträge im Warenkorb
                print('filter: draft')
                url += '?filter=draft'
            case 'queue': # Aufträge in der Warteschlange
                print('filter: queue')
                url += '?filter=queue'
            case 'canceled': # Aufträge in der Warteschlange
                print('filter: canceled')
                url += '?filter=canceled'
            case _:
                print(f'ERROR: unrecognized filter: {filter}')
            
        response = requests.get(url, json=self.payload_auth)
        data = response.json()['data']['printjobs']
        return data


    def delete_printjob(self, id):
        url = self.base_url + f'/printjobs/{id}'
        response = requests.delete(url, json=self.payload_auth)
        return response.json()

    def transactions(self, filter='payins'):
        url = self.base_url + f'/transactions?{filter}'
        response = requests.get(url, json=self.payload_auth)
        if response.status_code == 200:
            return response.json()['data']['transactions']

def main():
    print(api.balance())

if __name__ == '__main__':
    api = OnlineBrief24API()
    main()
