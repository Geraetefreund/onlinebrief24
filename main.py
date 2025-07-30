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
        self.payload = {
            'auth': {
                'apiKey': f'{self.api_key}',
                'apiSecret': f'{self.api_secret}',
                'mode': 'test'
                }
        }

    def balance(self):
        url = self.base_url + '/balance'
        response = requests.get(url, headers=self.headers, json=self.payload)
        return f'Balance: {response.json()['data']['balance']} EUR'

    def invoices(self):
        url = self.base_url + '/invoices'
        response = requests.get(url, headers=self.headers, json=self.payload)
        return response.json()['data']['invoices']

    def get_invoice(self, invoice_id):
        url = self.base_url + f'/invoices/{invoice_id}'
        response = requests.get(url, headers=self.headers, json=self.payload)
        invoice_date = response.json()['data']['invoice_date'].split(' ')[0]
        base64_data = response.json()['data']['base64_data']
        pdf_data = base64.b64decode(base64_data)
        pdf_filename = f"ob24-Rechnung-{invoice_date}.pdf"
        with open(pdf_filename, "wb") as file:
            file.write(pdf_data)
            print(f'successfully saved {pdf_filename}')
        return response.json()


if __name__ == '__main__':
    ob = onlinebrief24API()
