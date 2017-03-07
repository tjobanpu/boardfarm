# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import re
import rootfs_boot
from devices import board, prompt

class InterfacesShow(rootfs_boot.RootFSBootTest):
    '''Used "ip" or "ifconfig" to list interfaces.'''
    def runTest(self):
        board.sendline('\nip link show')
        board.expect('ip link show')
        board.expect(prompt)
        if "ip: not found" not in board.before:
            up_interfaces = re.findall('\d: ([A-Za-z0-9-\.]+)[:@].*state UP ', board.before)
            ether_interfaces = re.findall('\d: ([A-Za-z0-9-\.]+)[:@].*\n.*link/ether ', board.before)
            assert up_interfaces == ether_interfaces
        else:
            board.sendline('ifconfig')
            board.expect(prompt)
            up_interfaces = re.findall('([A-Za-z0-9-\.]+)\s+Link', board.before)
        num_up = len(up_interfaces)
        if num_up:
            self.result_message = "%s interfaces are UP: %s" % (num_up, ", ".join(sorted(up_interfaces)))
        else:
            self.result_message = "0 interfaces are UP"
        assert num_up >= 1
