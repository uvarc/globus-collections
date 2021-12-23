#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 11:09:50 2021

@author: khs3z
"""
import argparse
import globus_sdk
import pandas as pd
import access


HOST_ENDPOINTS = 'uva#main-DTN'
SCOPE_OPTIONS = ['shared-by-me', 'my-endpoints'] #'shared-with-me'
ENDPOINT_KEEP = ['host_endpoint', 'host_endpoint_id', 'id', 'host_path', 'sharing_target_root_path', 'display_name', 'description']
ACL_KEEP = ['acl id', 'path', 'permissions', 'principal', 'principal_type', 'role_id', 'role_type', 'collection id']
IDENTITY_KEEP = ['name', 'username', 'id']


def get_endpoint_acls(tc, filter_scope, host_endpoints=[]):
    if len(host_endpoints) > 0:
        endpoints = [ep for ep in tc.endpoint_search(filter_scope=filter_scope) if ep['host_endpoint'] in host_endpoints]
    else:
        endpoints = [ep for ep in tc.endpoint_search(filter_scope=filter_scope)]
    try:
        acls = {ep['id']:tc.endpoint_acl_list(ep['id']) for ep in endpoints}
    except:
        acls = {}
    return endpoints,acls
    

def get_identities(ac, gc, endpoints, acllist):
    id_dfs = []
    for ep in endpoints:
        ep_id = ep['id']
        if len(acllist) > 0 and ep['id'] in acllist.keys():        
            for data in acllist[ep_id]['DATA']:
                if data['principal_type'] == 'group':
                    groupinfo = gc.get_group(group_id=data['principal']).data
                    identity = {'id':[groupinfo['id']], 'name':[groupinfo['name']]}
                    i_df = pd.DataFrame(identity)
                else:    
                    personinfo = ac.get_identities(ids=data['principal']).data['identities']
                    i_df = pd.DataFrame(personinfo)
                    #i_df['principal_type'] = ['identity'] * len(i_df)
                id_dfs.append(i_df)
    if len(id_dfs) > 0:
        id_df = pd.concat(id_dfs)
        id_df = id_df.drop_duplicates()
    else:
        id_df = pd.DataFrame(data={}, columns=IDENTITY_KEEP)
    return id_df


def endpoint_dataframe(endpoints):
    for ep in endpoints:
        # convert list into comma separated string
        ep['my_effective_roles'] = ",".join(ep['my_effective_roles'])
    ep_df = pd.concat([pd.DataFrame(ep, index=[0]) for ep in endpoints]) 
    ep_df = ep_df[ENDPOINT_KEEP]
    ep_df = ep_df.drop_duplicates()
    ep_df = ep_df.rename(columns={"id": "collection id"})
    return ep_df


def acl_dataframe(endpoints, acllist):
    acl_dfs = []
    for ep in endpoints:
        if len(acllist) > 0 and ep['id'] in acllist.keys():
            acl_df = pd.DataFrame(acllist[ep['id']]['DATA'])
            acl_df['collection id'] = [ep['id']] * len(acl_df)
            #acl_df['collection name'] = [ep['display_name']] * len(acl_df)
            acl_dfs.append(acl_df)
    if len(acl_dfs) > 0:
        df = pd.concat(acl_dfs)
        df = df.rename(columns={'id':'acl id'})
    else:
        df = pd.DataFrame(data={}, columns=ACL_KEEP)
    return  df


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoints", default=HOST_ENDPOINTS, help="comma separated list of endpoint names")
    parser.add_argument("-s", "--scope", default=SCOPE_OPTIONS[0], choices=SCOPE_OPTIONS, help="output file")
    parser.add_argument("-o", "--output", default="collections.csv", help="output file")
    return parser.parse_args()


def main():
    args = parse_args()
    scope = args.scope
    endpoint_names = args.endpoints.split(",")
    output_file = args.output

    # set up clients
    client_id = access.get_client_id()
    client = globus_sdk.NativeAppAuthClient(client_id)
    client.oauth2_start_flow()

    ac = access.get_auth_client(client)
    gc = access.get_groups_client(client)
    tc = access.get_transfer_client(client)
    
    print ("Client initialization successful.")
    print (f"Checking these endpoints: {','.join(endpoint_names)}")
    print (f"Applied filter: {scope}")

    # get endpoint and ACL info
    eps,acls = get_endpoint_acls(tc, filter_scope=scope, host_endpoints=endpoint_names)
    if len(eps) == 0:
        print ("Endpoint does not exit or no collections found.")
    else:    
        print (f"Found these shared collections on {','.join(endpoint_names)}:")
        for ep in eps:
            print (f"\t{ep['display_name']}, {ep['id']}, owner: {ep['owner_string']}")
            
        # create dataframes for endpoint, acls, and identities   
        ep_df = endpoint_dataframe(eps)
        ep_df.to_csv('my-collections.csv')
    
        acl_df = acl_dataframe(eps, acls)
        acl_df.to_csv('acls.csv')
        
        id_df = get_identities(ac, gc, eps, acls)
        id_df.to_csv('identities.csv')
        
        acl_id_df = acl_df.merge(id_df, left_on='principal', right_on='id', how='left')    
        acl_id_ep_df = acl_id_df.merge(ep_df, left_on='collection id', right_on='collection id', how='left')
        acl_id_ep_df = acl_id_ep_df[ENDPOINT_KEEP + ACL_KEEP + IDENTITY_KEEP]
        acl_id_ep_df.to_csv(output_file)
        print (f"Collection information saved in {output_file}")


if __name__ == '__main__':
    main()
