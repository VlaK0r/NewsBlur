#!/usr/bin/env python3

import os
import time
import sys
import subprocess
import digitalocean

TOKEN_FILE = "/srv/secrets-newsblur/keys/digital_ocean.token"
# TOKEN_FILE = "/srv/secrets-newsblur/keys/digital_ocean.readprod.token"

try:
    api_token = open(TOKEN_FILE, 'r').read().strip()
except IOError:
    print(f" ---> Missing Digital Ocean API token: {TOKEN_FILE}")
    exit()

# Install from https://github.com/do-community/do-ansible-inventory/releases
ansible_inventory_cmd = f'do-ansible-inventory -t {api_token} --out /srv/newsblur/ansible/inventories/digital_ocean.ini'
subprocess.call(ansible_inventory_cmd, 
                shell=True)

exit() # Too many requests if we run the below code

do = digitalocean.Manager(token=api_token)
droplets = do.get_all_droplets()

print("\n ---> Checking droplets: %s\n" % (' '.join([d.name for d in droplets])))


def check_droplets_created():
    i = 0
    droplets = do.get_all_droplets()

    for instance in droplets:
        if instance.status == 'new':
            print(".", end=' ')
            sys.stdout.flush()
            i += 1
            time.sleep(i)
            break
    else:
        print(" ---> All booted!")
        return True

i = 0
while True:
    if check_droplets_created():
        break