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
        self.payload_auth = {
            'auth': {
                'apiKey': f'{self.api_key}',
                'apiSecret': f'{self.api_secret}',
                'mode': 'live'
                }
        }

        if not self.api_key or not self.api_secret:
            print('ERROR: API credentials missing in .env')
            sys.exit(1)

    def open_pdf(self, filename):
        try:
            with open(filename, 'rb') as file:
                pdf_data = file.read()
            return pdf_data
        except Exception as e:
                print(f"ERROR: Exception {e}")
                return None

    def base64_encode(self, pdf_data):
        return base64.b64encode(pdf_data).decode("utf8")

    def md5_checksum(self, base64_data):
        return hashlib.md5(base64_data.encode('utf-8')).hexdigest()

    def request(self, method, url, payload):
        try:
            response = requests.request(method, url, json=payload)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f'Request error: {e}')
            return None

    def balance(self):
        url = self.base_url + '/balance'
        response = self.request('get', url, self.payload_auth)
        return response.json()['data']['balance']

    def list_invoices(self):
        url = self.base_url + '/invoices'
        response = self.request('get', url, self.payload_auth)
        return response.json()['data']['invoices']
        
    def get_invoice(self, invoice_id):
        url = self.base_url + f'/invoices/{invoice_id}'
        response = self.request('get', url, self.payload_auth)
        invoice_date = response.json()['data']['invoice_date'].split(' ')[0]
        base64_data = response.json()['data']['base64_data']
        pdf_data = base64.b64decode(base64_data)
        pdf_filename = f"ob24-Rechnung-{invoice_date}.pdf"
        try:
            with open(pdf_filename, "wb") as file:
                file.write(pdf_data)
                print(f'Invoice successfully saved: {pdf_filename}')
        except Exception as e:
            return f"Error: Exception as {e}"
    
    def send_letter(self, pdf_filename, mode='live', color=False, duplex=False):
        pdf_data = self.open_pdf(pdf_filename)
        if pdf_data is None: # just to be extra sure...
            print('ERROR: Could not read PDF file.')
            return
        base64_encoded = self.base64_encode(pdf_data)
        md5_checksum = self.md5_checksum(base64_encoded)

        payload = {
            **self.payload_auth,
            "letter": {
                "base64_file": base64_encoded,
                "base64_file_checksum": md5_checksum,
                "filename_original": os.path.basename(pdf_filename),
                "specification": {
                    "color": "4" if color else "1",
                    "mode": "duplex" if duplex else "simplex",
                    "shipping": "auto"
                }
            }
        }

        
        payload['auth']['mode'] = mode
        url = self.base_url + '/printjobs'
        response = self.request('post', url, payload)

        if response.status_code == 200:
            print(f'Letter submitted successfully.')

            items = response.json()['data']['items'][0]
            print(f"Status: {items['status']}")
            print(f"Address: {items['address']}")
            print(f"Cost: {items['amount'] + items['vat']} EUR")
            print(f'OnlineBrief24 remaining balance: {self.balance()} EUR')
           
        else:
            print(f'Response status code: {response.status_code} - {response.text}')

    def list_printjobs(self, filter='all'):
        url = self.base_url + '/printjobs'
        match filter :
            case 'all':
                pass
            case 'hold': # angehaltene Auftraege
                url += '?filter=hold'
            case 'done': # verarbeitete Auftraege
                url += '?filter=done'
            case 'draft': # Aufträge im Warenkorb
                url += '?filter=draft'
            case 'queue': # Aufträge in der Warteschlange
                url += '?filter=queue'
            case 'canceled': # Aufträge in der Warteschlange
                url += '?filter=canceled'
            case _:
                print(f'ERROR: unrecognized filter: {filter}')
            
        response = self.request('get', url, self.payload_auth)
        return response.json()['data']['printjobs']


    def delete_printjob(self, id): # int
        url = self.base_url + f'/printjobs/{id}'
        response = self.request('delete', url, self.payload_auth)
        return response.json()

    def transactions(self, filter='payins'):
        url = self.base_url + f'/transactions?{filter}'
        response = self.request('get', url, self.payload_auth)
        return response.json()['data']['transactions']

def main():
    parser = argparse.ArgumentParser(
        prog = 'ob24',
        description= """
Send letters and manage printjobs via OnlineBrief24 CLI Tool
Examples:
  ob24 <command> -h
  ob24 send my_letter.pdf --color --duplex (default: b&w, simplex)
  ob24 balance 
  ob24 invoices list --last 3 (default: all)
  ob24 printjobs list -f draft
  ob24 printjobs delete <id>
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

    subparsers = parser.add_subparsers(
        title='Availabe commands',
        dest='command',
        required=True,
        metavar = ''
    )

    send_parser = subparsers.add_parser(
        'send',
        help = 'Send a letter',
        description='Send a PDF letter via OnlineBrief24.de',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    send_parser.add_argument('filename', help='PDF file to send')
    send_parser.add_argument('-m', '--mode', choices=['live', 'test'], default='live', help='use test for debug')
    send_parser.add_argument('--color', action='store_true', help=' Enable color printing. (Default is b&w)')

    send_parser.add_argument('--duplex', action='store_true', help='Enable duplex printing. (Default is simplex)')





    balance_parser = subparsers.add_parser('balance', help='Print balance')

    invoices_parser = subparsers.add_parser('invoices',  help='List/Download invoices')
    invoices_subparsers = invoices_parser.add_subparsers(dest='invoices_command', required=True)

    invoices_list = invoices_subparsers.add_parser('list', help='List invoices')
    invoices_list.add_argument(
        '-l', '--last',
        type = int,
        default = None,
        help = 'Only show the last N invocies'
    )

    invoices_get = invoices_subparsers.add_parser('get', help='Download invoice')
    invoices_get.add_argument(
        'id',
        type=int,
        help='Invoice ID to download'
    )
    
    printjobs_parser = subparsers.add_parser('printjobs', help='List/Delete print jobs')
    printjobs_subparsers = printjobs_parser.add_subparsers(dest = 'printjobs_command', required=True)

    printjobs_list = printjobs_subparsers.add_parser('list', help='List printjobs')
    printjobs_list.add_argument(
        '-f', '--filter',
        choices=['all', 'hold', 'done', 'draft', 'queue', 'canceled'],
        default='all',
        help='Filter prinjobs by status'
    )

    printjobs_delete = printjobs_subparsers.add_parser('delete', help = 'Delete a printjob')
    printjobs_delete.add_argument('id', type=int, help = 'Printjob ID to delete')


    transactions_parser = subparsers.add_parser('transactions', help='List account transactions')
    # payouts not supported yet
    #transactions_parser.add_argument(
    #    '-f', '--filter',
    #    default = 'payins',
    #    choices=['payins', 'payouts', 'all'],
    #    help='Filter transactions (default: payins)'
    #)

    args = parser.parse_args()

    if args.command == 'balance':
        print(f'OnlineBrief24 remaining balance: {api.balance()} EUR')

    elif args.command == 'send':
        api.send_letter(
            args.filename,
            mode=args.mode,
            color=args.color,
            duplex=args.duplex
        )


    elif args.command == 'invoices':
        if args.invoices_command == 'list':
            invoices = api.list_invoices()
            if args.last:
                invoices = invoices[:args.last]
            print(json.dumps(invoices, indent=2))
        elif args.invoices_command == 'get':
            api.get_invoice(args.id)

    elif args.command == 'printjobs':
        if args.printjobs_command == 'list':
            jobs = api.list_printjobs(filter=args.filter)
            print(json.dumps(jobs, indent=2))

        elif args.printjobs_command == 'delete':
            result = api.delete_printjob(args.id)
            print(json.dumps(result, indent=2))

    elif args.command == 'transactions':
        transactions = api.transactions()
        print(json.dumps(transactions, indent=2))


if __name__ == '__main__':
    api = OnlineBrief24API()
    main()
