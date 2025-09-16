# OnlineBrief24 CLI

A Python command-line tool for sending letters via the [OnlineBrief24](https://www.onlinebrief24.de) service.  

## Features 
 - Authenticate with OnlineBrief24 using credentials stored in `.env`
 - Send PDF letters directly from the command line
 - Check print jobs and account balance
 - Simple CLI interface with clear arguments
 - Designed to be extended for automation (i.e, cron, scripts, makefiles)

## Getting Started

### Requirements:
 - Python 3.11+
 - `pip` for dependency installation
 - An active [OnlineBrief24](https://www.onlinebrief24.de) account

### Installation

 - clone the repo
 - create and activate venv: `python3 -m venv venv && source venv/bin/activate`
 - install dependencies: `pip3 install -r requirements.txt`


### Usage
```sh
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
```

### .env file
Create a `.env` file in the project root:

```sh
API_KEY="your OnlineBrief24 API key"
API_SECRET="your OnlineBrief24 API secret"
```
Never comit `.env` files with reald credentials. They are ignored by `.gitignore`.

## Development
 - Code written in Python and structured for easy extension.
 - Uses `.env` for credential management.

## Future Improvements
 - Functionality split into API client & CLI logic for scalability.
 - Add tests (mocking API responses)
 - Add better error handling and logging

