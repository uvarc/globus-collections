#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 14 00:00:01 2021

@author: khs3z
"""
import globus_sdk
from globus_sdk import GroupsClient, AuthClient, GroupsClient
import toml
import os


CLIENT_TOML = ".client.toml"
AUTH_TOML = ".auth.toml"
TRANSFER_TOML = ".transfer.toml"
GROUPS_TOML = ".groups.toml"
TOKENS_TOML = ".tokens.toml"

GLOBUS_SDK_TUTORIAL = "https://globus-sdk-python.readthedocs.io/en/stable/tutorial.html"
DEVELOPER_PAGE = "https://auth.globus.org/v2/web/developers"


def create_authorizer(tokens_file, key, client):
    token_data = toml.load(tokens_file)
    auth_rt = token_data[key]["refresh_token"]
    auth_at = token_data[key]["access_token"]
    expiration = token_data[key]["expires_at_seconds"]

    authorizer = globus_sdk.RefreshTokenAuthorizer(
                auth_rt, client, access_token=auth_at, expires_at=expiration)
    return authorizer

  
def get_auth_client(client):
    auth_authorizer = create_authorizer(TOKENS_TOML, 'auth', client)
    ac = AuthClient(authorizer=auth_authorizer)
    return ac


def get_groups_client(client):
    groups_authorizer = create_authorizer(TOKENS_TOML, 'groups', client)
    gc = GroupsClient(authorizer=groups_authorizer)
    return gc


def get_transfer_client(client):
    transfer_authorizer = create_authorizer(TOKENS_TOML, 'transfer', client)
    tc = globus_sdk.TransferClient(authorizer=transfer_authorizer)
    return tc


def get_client_id(f=CLIENT_TOML):
    try:
        client_id = toml.load(f)['client_id']
    except:
        print (f"Could not find or read Client ID from {CLIENT_TOML} file.\n")
        print (f"If you haven't done so already, register a Globus app and get a Client ID as described here: {GLOBUS_SDK_TUTORIAL}\n")
        print (f"If your already registered the app, you can look up your Client ID here: {DEVELOPER_PAGE}")
        client_id = input("Please enter your client ID: ").strip()
        with open(CLIENT_TOML, "w") as f:
            toml.dump({"client_id": client_id}, f)
    return client_id
    
    
def create_tokens(client_id):
    client = globus_sdk.NativeAppAuthClient(client_id)
    client.oauth2_start_flow(refresh_tokens=True, requested_scopes=["openid", "profile", "email", "urn:globus:auth:scope:transfer.api.globus.org:all", GroupsClient.scopes.all])
    authorize_url = client.oauth2_get_authorize_url()
    print(f"Please go to this URL and log in: {authorize_url}")
    auth_code = input("Please enter the Native App Authorization Code you get after login: ").strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)
    
    globus_auth_data = token_response.by_resource_server["auth.globus.org"]
    globus_transfer_data = token_response.by_resource_server["transfer.api.globus.org"]
    globus_groups_data = token_response.by_resource_server["groups.api.globus.org"]

    tokens = {'auth': globus_auth_data, 'transfer': globus_transfer_data, 'groups': globus_groups_data}
    with open(TOKENS_TOML, "w") as f:
        toml.dump(tokens, f)
            
    print ("Client ID and tokens saved successfully.")
        
if __name__ == '__main__':
    client_id = get_client_id()
    create_tokens(client_id)