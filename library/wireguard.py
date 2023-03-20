#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: my_wireguard_module

short_description: This module manages Wireguard interfaces and peers.

version_added: "1.0.0"

description: This module manages Wireguard interfaces and peers. It can add, update or remove peers.

options:
    interface:
        description: The name of the wireguard interface.
        required: true
        type: str
    peer_public_key:
        description: The public key of the peer to add, update or remove.
        required: false
        type: str
    peer_allowed_ips:
        description: A list of IP ranges allowed for the peer.
        required: false
        type: list
        elements: str
    state:
        description: The desired state of the peer.
        required: true
        choices: [ present, absent ]
    new:
        description:
            - Control to demo if the result of this module is changed or not.
            - Parameter description can be a list as well.
        required: false
        type: bool

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Add a new peer to the specified interface
- name: Add a new peer to the specified wireguard interface
  my_namespace.my_collection.my_wireguard_module:
    interface: wg0
    peer_public_key: qWwmbYlLsvxCxNtj4H4A/n4t0dei9g3q3Z1FjDzNUYk=
    peer_allowed_ips:
      - 10.0.0.2/32
    state: present

# Remove an existing peer from the specified interface
- name: Remove an existing peer from the specified wireguard interface
  my_namespace.my_collection.my_wireguard_module:
    interface: wg0
    peer_public_key: qWwmbYlLsvxCxNtj4H4A/n4t0dei9g3q3Z1FjDzNUYk=
    state: absent
'''

RETURN = r'''
original_message:
    description: The original interface and peer params that were passed in.
    type: dict
    returned: always
    sample: {'interface': 'wg0', 'peer_public_key': 'qWwmbYlLsvxCxNtj4H4A/n4t0dei9g3q3Z1FjDzNUYk=', 'peer_allowed_ips': ['10.0.0.2/32'], 'state': 'present'}
message:
    description: The output message that the wireguard module generates.
    type: str
    returned: always
    sample: 'Peer added successfully'
'''

# from ansible.module_utils.basic import AnsibleModule
# import os



# import os

# def add_wireguard_peer(interface, peer_public_key, peer_allowed_ips):
#     # Define the path to the WireGuard interface configuration file
#     config_file_path = '/etc/wireguard/{}.conf'.format(interface)

#     # Define the configuration for the new peer
#     peer_config = '\n[Peer]\nPublicKey = {}\nAllowedIPs = {}'.format(
#         peer_public_key,
#         ','.join(peer_allowed_ips)
#     )

#     # Append the new peer configuration to the configuration file
#     with open(config_file_path, 'a') as config_file:
#         config_file.write(peer_config)

#     # Restart the WireGuard interface to apply the changes
#     os.system('systemctl restart wg-quick@{}'.format(interface))

# import subprocess

# def restart_wireguard_interface(interface):
#     cmd = f"sudo wg-quick down {interface} && sudo wg-quick up {interface}"
#     subprocess.run(cmd, shell=True, check=True)


# import subprocess
# import json

# def peer_exists(interface, peer_public_key, peer_allowed_ips):
#     cmd = ["sudo", "wg", "show", interface, "dump"]
#     output = subprocess.check_output(cmd, universal_newlines=True)

#     for line in output.splitlines():
#         parts = line.strip().split("\t")
#         if len(parts) == 3 and parts[1] == peer_public_key:
#             # Peer public key matches, now check allowed IPs
#             existing_allowed_ips = json.loads(parts[2])
#             if set(existing_allowed_ips) == set(peer_allowed_ips):
#                 return "Peer with public key {} and allowed IPs {} already exists.".format(peer_public_key, peer_allowed_ips)
#             elif set(peer_allowed_ips) & set(existing_allowed_ips):
#                 return "IPs {} in peer allowed IPs already used by another peer.".format(set(peer_allowed_ips) & set(existing_allowed_ips))
#             else:
#                 return None

#     return "Peer with public key {} not found.".format(peer_public_key)

#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
import os
import re
import subprocess

def add_peer_to_wg_config(module, interface: str, peer_public_key: str, peer_allowed_ips: list, comment: str) -> None:
    
    # First, stop the interface
    stop_wg_interface(module, interface)


    # Add the new peer configuration to the file
    
    config_file = f'/etc/wireguard/{interface}.conf'
    with open(config_file, 'a') as f:
        f.write(f'\n[Peer]\nPublicKey={peer_public_key}\nAllowedIPs={",".join(peer_allowed_ips)}\n# {comment}\n')
    start_wg_interface(module, interface)


def split_wg_config(config_file):
    with open(config_file, 'r') as f:
        config = f.read()

    blocks = []
    current_block = ''
    for line in config.splitlines():
        if line.startswith('[') and current_block:
            blocks.append(current_block.strip())
            current_block = ''
        current_block += line + '\n'
    if current_block:
        blocks.append(current_block.strip())

    return blocks


def contains_public_key(block, public_key):
    for line in block.splitlines():
        if public_key in line:# if line.startswith('PublicKey=') and line.strip().split('=')[1] == public_key:
            return True
    return False


def remove_peer_from_wg_config(module, interface: str, peer_public_key: str) -> None:
    config_file = f'/etc/wireguard/{interface}.conf'
    
    # First, stop the interface
    stop_wg_interface(module, interface)
    
    blocks = split_wg_config(config_file)
    filtered_blocks = [block for block in blocks if not contains_public_key(block, peer_public_key)]
    new_config = '\n\n'.join(filtered_blocks)

    with open(config_file, 'w') as f:
        f.write(new_config)

    start_wg_interface(module, interface)


def stop_wg_interface(module, interface):
    # Check if interface is up
    cmd = ['ip', 'link', 'show', interface]
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    if rc==0:
        cmd = ['wg-quick', 'down', interface]
        if not module.check_mode:
            rc, stdout, stderr = module.run_command(cmd, check_rc=True)
            if rc != 0:
                module.fail_json(msg=f"Failed to bring down {interface}: {stderr}")

def restart_wg_interface(module, interface):
    stop_wg_interface(module, interface)
    start_wg_interface(module, interface)

def start_wg_interface(module, interface):
    # Check if interface is up
    cmd = ['ip', 'link', 'show', interface]
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    if rc!=0:
        cmd = ['wg-quick', 'up', interface]
        rc, stdout, stderr = module.run_command(cmd, check_rc=True)
        if rc != 0:
            module.fail_json(msg=f"Failed to bring up {interface}: {stderr}")

def check_peer_existence(module, interface: str, peer_public_key: str) -> str:
    config_file = f'/etc/wireguard/{interface}.conf'
    with open(config_file, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if peer_public_key in line:# re.match(r'^PublicKey=' + peer_public_key, line):
            return 'Peer already exists with this public key'
    return ''

def run_module():
    module_args = dict(
        interface=dict(type='str', required=True),
        peer_public_key=dict(type='str', required=True),
        peer_allowed_ips=dict(type='list', required=True),
        comment=dict(type='str', required=False),
        state=dict(type='str', required=True, choices=['present', 'absent']),
        check_mode=dict(type='bool', required=False, default=False)
    )

    result = dict(
        changed=False,
        message='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    interface = module.params['interface']
    peer_public_key = module.params['peer_public_key']
    peer_allowed_ips = module.params['peer_allowed_ips']
    comment = module.params.get('comment')
    state = module.params['state']
    check_mode = module.params['check_mode']

    if state == 'present':
        # Check if peer already exists
        existence_message = check_peer_existence(module, interface, peer_public_key)
        if existence_message:
            result['message'] = existence_message
            module.fail_json(msg=existence_message)

        # Add new peer to config
        if not check_mode:
            add_peer_to_wg_config(module, interface, peer_public_key, peer_allowed_ips, comment)
        result['changed'] = True
        result['message'] = f'Peer added to {interface}'

    elif state == 'absent':
        # Remove peer from config
        if not check_mode:
            remove_peer_from_wg_config(module, interface, peer_public_key)
        result['changed'] = True
        result['message'] = f'Peer removed from {interface}'

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
