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
    else:
        flow = client.flow_from_clientsecrets(
            path.join(CREDENTIALS_PATH, "client_secret.json"), SCOPES
        )
        creds = tools.run_flow(flow, store)

    return


if __name__ == "__main__":
    generate_credentials()
