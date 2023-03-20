# Ansible WireGuard Module: ansible_wrieguard
This Ansible module provides a simple way to manage WireGuard peer configurations on a Linux system. The module can add or remove peers from a given WireGuard interface configuration file, based on the provided parameters. 

This module uses `wg-quick` under the hood to manage the WireGuard interface. `wg-quick` is a helper script that simplifies the process of setting up and tearing down WireGuard interfaces. To use this module, you must have `wg-quick` installed on your system. If you don't have it, you can install it using your distribution's package manager. This module provides a simplified interface for managing WireGuard interfaces using `wg-quick`. It abstracts away many of the complexities involved in configuring and managing a WireGuard interface, allowing you to easily create, start, stop, and delete interfaces with just a few simple commands. Note that if you need more advanced functionality that is not provided by `wg-quick`, you may need to use the `wg` command directly. However, for most use cases, `wg-quick` should be sufficient.


##  Installation
This module does not require any additional installation steps, as it is a standalone Python script that can be run directly by Ansible.



## Usage
Here's an example playbook that demonstrates how to use the ansible_wrieguard module:

```yaml
- name: Add new WireGuard peer
  hosts: all
  tasks:
    - name: Add new WireGuard peer
      ansible_wrieguard:
        interface: wg0
        peer_public_key: <PEER_PUBLIC_KEY>
        peer_allowed_ips:
          - 10.0.0.2/32
        comment: "My new peer"
        state: present
```
This playbook adds a new peer to the wg0 interface configuration file. The peer_public_key parameter specifies the public key of the new peer, and peer_allowed_ips specifies the allowed IP addresses for the peer. The comment parameter is optional and can be used to add a comment to the new peer configuration.

To remove a peer, simply set the state parameter to absent, like this:

```yaml
- name: Remove existing WireGuard peer
  hosts: all
  tasks:
    - name: Remove existing WireGuard peer
      ansible_wrieguard:
        interface: wg0
        peer_public_key: <PEER_PUBLIC_KEY>
        state: absent
```

## License
This module is released under the MIT License. See the LICENSE file for details.

## Acknowledgments
This module was generated using ChatGPT, with minor modifications.