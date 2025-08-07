# OnlineBrief24 Wrapper

Python CLI wrapper for onlinebrief24.de REST API.
 - send letters
 - show balance
 - list/download invoices
 - list/delete printjobs
 - list account transactions (payins/payouts)

## Requirements:
 * .env file with credentials
 * requirements.txt


### Usage
~~~
usage: ob24 <command> [<args>] [-h|--help]

options:
  -h, --help      show this help message and exit

Available commands:
  <command>
    send          Send a letter
    balance       Print balance
    invoices      List or Download invoices
    printjobs     List/Delete print jobs
    transactions  List account transactions

Examples:
  ob24 send my_letter.pdf --color --duplex (default: b&w, simplex)
  ob24 invoices list --last 3 (default: all)
  ob24 balance 
  ob24 printjobs delete <id>

Use 'ob24 <command> -h' for detailed help on a specific command.'
~~~

### .env file
Please make sure to .gitignore your secrets.

~~~
API_KEY="{your api key}"
API_SECRET="{your api secret}"
~~~
