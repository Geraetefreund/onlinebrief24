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

class onlinebrief24API:

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
        return f'Balance: {response.json()['data']['balance']} EUR'

    def invoices(self):
        url = self.base_url + '/invoices'
        response = requests.get(url, headers=self.headers, json=self.payload_auth)
        invoices = response.json()['data']['invoices']
        print('There are currently {len(invoices} invoices.')
        for inv in invoices:
            print(f'id: {inv['id']}, invoice date: {inv['invoice_date'].split(' ')[0]}')
        #return response.json()['data']['invoices']

    def get_invoice(self, invoice_id):
        url = self.base_url + f'/invoices/{invoice_id}'
        response = requests.get(url, headers=self.headers, json=self.payload_auth)
        invoice_date = response.json()['data']['invoice_date'].split(' ')[0]
        base64_data = response.json()['data']['base64_data']
        pdf_data = base64.b64decode(base64_data)
        pdf_filename = f"ob24-Rechnung-{invoice_date}.pdf"
        with open(pdf_filename, "wb") as file:
            file.write(pdf_data)
            print(f'✅ Invoice successfully saved: {pdf_filename}')
        #return response.json()
    
    def open_pdf(self, pdf_filename):
        with open(f'{pdf_filename}', 'rb') as file:
            pdf_data = file.read()
        return pdf_data

    def base64_encode(self, pdf_data):
        base64_encoded = base64.b64encode(pdf_data).decode("utf8")
        return base64_encoded

    def md5_checksum(self, base64_data):
        md5_checksum = hashlib.md5(base64_data.encode('utf-8')).hexdigest()
        return md5_checksum

    def send_letter(self, pdf_filename):
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
        response = requests.post(f"{self.base_url}/printjobs", headers=self.headers, json=payload)

        return response

if __name__ == '__main__':
    ob = onlinebrief24API()
