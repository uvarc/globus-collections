# globus-collections

A set of Python scripts that uses the Globus SDK to query information about a users Globus collections.

# Installation

Install Python 3, cd into the top directory of the cloned repository and run this command:
```
pip install -r requirements
```

For installation in user space, add the `--user` flag like so:
```
pip install --user -r requirements
```

# Usage

The Globus SDK requires registration of a Globus app with client ID and app authorization code. The authorization information can be stored in user specific access tokens. To get started, follow steps (1) and (2) below to register the app and create your access tokens. If you already did this, skip to step (3). 

1. Register a Globus app

    Log in at https://globus.org and register a Globus app as described here https://globus-sdk-python.readthedocs.io/en/stable/tutorial.html. This will set up a Client ID. If you already registered an app, you can look up the client ID here https://auth.globus.org/v2/web/developers. Copy the client ID to your clipboard.

2. Create access tokens

    Run the access.py script like so:
    ```
    python access.py
    ```
    Enter the client ID when prompted. The script will output a URL to login and retrieve an authorization code. Enter the authorization code when prompted. Your client ID and access tokens will be saved in the current directory in the `.client.toml` and `.tokens.toml` files respectively.

3. Retrieve Globus endpoint information

    The `get_collections.py` script is used to retrieve your endpoint information. It attempts to read your client ID and access tokens from the hidden `.client.toml` and `.tokens.toml` files. If these files don't exist, you'll be walked through steps (1) & (2) again to recreate them.
    
    By default, the script will retrieve collections shared by you on the uva#mainDTN. The retrieved information is saved in a set of csv files.
    
    Run the `python get_collections.py -h` to see available runtime options.
