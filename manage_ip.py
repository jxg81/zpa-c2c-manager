import requests
import json
import csv
import platform

from const import ZPA_USERNAME, ZPA_PASSWORD

def get_platform():
    sys_type = platform.system()
    WINDOWS = 'c:\Windows\System32\Drivers\etc\hosts'
    DARWIN = '/private/etc/hosts'
    UNIX = '/etc/hosts'
    if sys_type == 'Darwin':
        print(f'Mac OS detected\nWriting host entries to {DARWIN}')
        result = DARWIN
    elif sys_type == 'Windows':
        print(f'Windows detected\nWriting host entries to {WINDOWS}')
        result = WINDOWS
    else:
        print(f'Nix detected\nWriting host entries to {UNIX}')
        result = UNIX
    return result
    
def process_add_hosts(csv_file):
    with open(csv_file, newline='') as f:
        data=list(csv.DictReader(f, delimiter=',',fieldnames=['IP', 'Name']))
    return data
        
    
def zpa_login():
    login_data={'username': ZPA_USERNAME,
                'password': ZPA_PASSWORD,
                'sp-login':'false',
                'signin-remember-me':'false',
                'passcode':'',
                'language':'eng'}

    login_url = 'https://us1-zpa-authn.private.zscaler.com/authn/v1/oauth/token?grant_type=USER'

    login=requests.post(url=login_url, data=login_data)
    login_data=json.loads(login.text)
    customer_id=login_data['customerId']
    auth_token=login_data["Z-AUTH-TOKEN"]
    return customer_id, auth_token

def get_ip_bindings(customer_id, auth_token):
    csv_url=f'https://iparsread.private.zscaler.com/ipars/v1/customers/{customer_id}/ipBindings/export'
    csv_data={"timeZoneId":"AEST","timeZoneStr":"Australia/Melbourne","filterDtoList":[],"sortBy":{"sortName":"ip","sortOrder":"ASC"}}
    csv_headers={'Authorization': f'Bearer {auth_token}', 'Content-Type': 'application/json'}
    csv_response=requests.post(url=csv_url, json=csv_data, headers=csv_headers)
    result=list(csv.DictReader(csv_response.text.splitlines(), delimiter=',',quotechar='"'))
    return result

def write_hosts_file(ip_bindings: dict, file_path: str, add_hosts: dict=None):
    with open(file_path, 'w+') as f:
        for binding in ip_bindings:
            f.write(f'{binding["Zscaler IP"]}\t{binding["Client Hostname"]}\r\n')
        if add_hosts:
            for host in add_hosts:
                f.write(f'{host["IP"]}\t{host["Name"]}\r\n')

def manage_hosts_file(override_file=None, add_hosts=None):
    if override_file:
        file_path = override_file
    else:
        file_path = get_platform()
    customer_id, auth_token = zpa_login()
    ip_bindings = get_ip_bindings(customer_id, auth_token)
    if add_hosts:
        add_hosts=process_add_hosts(add_hosts)
    write_hosts_file(ip_bindings, file_path, add_hosts=add_hosts)