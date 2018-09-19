"""generate_google_credentials

A helper file that takes in the given Google credentials, and produces a usable credentials file.

First, generate a set of API keys on the
[Google API Dashboard](https://console.developers.google.com).

This is done by making a new project, then making a new set of credentials under
"Credentials". After giving it any name, download the config file and rename it
to `client_secret.json`, before running the included
`generate_google_credentials.py` script on it, to make the final authentication
file. This final `credentials.json` should then be put in your config folder.
"""
import warnings
from os import path

from oauth2client import client, file, tools

SCOPES = "https://www.googleapis.com/auth/calendar"
CREDENTIALS_PATH = ""
FORCE_REGEN = False

warnings.filterwarnings("error")


def generate_credentials():
    """generate_credentials

    Generate the credentials.json file needed for OAuth login.
    """

    secret_file = path.join(CREDENTIALS_PATH, "client_secret.json")

    if not path.isfile(secret_file):
        print("Can't find client_secret.json.")
        print("Set CREDENTIALS_PATH to the path directory in the script.")
        return

    creds = None

    try:
        store = file.Storage(path.join(CREDENTIALS_PATH, "credentials.json"))
        creds = store.get()
    except UserWarning:
        print("No credentials file found, generating...")

    if creds and not creds.invalid and not FORCE_REGEN:
        print("Credentials are valid, exiting.")
        print("Set FORCE in the script to re-generate.")
        return

    flow = client.flow_from_clientsecrets(
        path.join(CREDENTIALS_PATH, "client_secret.json"), SCOPES
    )
    creds = tools.run_flow(flow, store)

    return


if __name__ == "__main__":
    generate_credentials()
