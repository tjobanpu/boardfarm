# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import re
import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class Logread(rootfs_boot.RootFSBootTest):
    '''Recorded syslog.'''
    def runTest(self):
        board.sendline('\nlogread')
        board.expect('logread')
        board.expect('OpenWrt', timeout=5)
        board.expect(prompt)

class DiskUse(rootfs_boot.RootFSBootTest):
    '''Checked disk use.'''
    def runTest(self):
        board.sendline('\ndf -k')
        board.expect('Filesystem', timeout=5)
        board.expect(prompt)
        board.sendline('du -k | grep -v ^0 | sort -n | tail -20')
        board.expect(prompt)

class TopCheck(rootfs_boot.RootFSBootTest):
    '''Ran "top" to see current processes.'''
    def runTest(self):
        board.sendline('\ntop -b -n 1')
        board.expect('Mem:', timeout=5)
        try:
            board.expect(prompt, timeout=2)
        except:
            # some versions of top do not support '-n'
            # must CTRL-C to kill top
            board.sendcontrol('c')

class UciShow(rootfs_boot.RootFSBootTest):
    '''Dumped all current uci settings.'''
    def runTest(self):
        board.sendline('\nls -l /etc/config/')
        board.expect('/etc/config/', timeout=5)
        board.expect(prompt)
        board.sendline('ls -l /etc/config/ | wc -l')
        #board.expect('(\d+)\r\n')
        board.expect('(\d+)')
        num_files = int(board.match.group(1))
        board.expect(prompt)
        board.sendline('uci show')
        board.expect(prompt, searchwindowsize=50)
        self.result_message = 'Dumped all current uci settings from %s files in /etc/config/.' % num_files

class DhcpLeaseCheck(rootfs_boot.RootFSBootTest):
    '''Checked dhcp.leases file.'''
    def runTest(self):
        board.sendline('\ncat /tmp/dhcp.leases')
        board.expect('leases')
        board.expect(prompt)

class IfconfigCheck(rootfs_boot.RootFSBootTest):
    '''Ran 'ifconfig' to check interfaces.'''
    def runTest(self):
        board.sendline('\nifconfig')
        board.expect('ifconfig')
        board.expect(prompt)
        results = re.findall('([A-Za-z0-9-\.]+)\s+Link.*\n.*addr:([^ ]+)', board.before)
        tmp = ', '.join(["%s %s" % (x, y) for x, y in results])
        board.sendline('route -n')
        board.expect(prompt)
        self.result_message = 'ifconfig shows ip addresses: %s' % tmp

class MacAddressCheck(rootfs_boot.RootFSBootTest):
    '''Checked MAC addresses for all interfaces.'''
    def __checkMac(self, mac_address, base_mac, mac_sequence):
        result = int(base_mac, base=16) + mac_sequence
        if mac_address:
            mac_address = re.sub('[:]', '', mac_address.upper())[-6:]
            if result == int(mac_address, base=16):
                self.result_message = 'MAC addresses are sequential'
            else:
                raise ValueError('MAC addresses are not sequential')
        else:
            raise ValueError('Could not find appropriate MAC address')

    def runTest(self):
        board.sendline('\nhexdump -n 6 -v -e \'8/1 "%02X" "\n"\' /proc/device-tree/uccp@18480000/mac-address0')
        board.expect('mac-address0')
        board.expect(prompt)
        mac0 = re.search(r'0019F5([A-F0-9]{2}){3}', board.before).group()
        mac0 = mac0[-6:]
        board.sendline('\nhexdump -n 6 -v -e \'8/1 "%02X" "\n"\' /proc/device-tree/uccp@18480000/mac-address1')
        board.expect('mac-address1')
        board.expect(prompt)
        mac1 = re.search(r'0019F5([A-F0-9]{2}){3}', board.before).group()
        self.__checkMac(mac1, mac0, 1)
        board.sendline('\nhcitool dev')
        board.expect('hci0')
        board.expect(prompt)
        mac2 = re.search(r'00:19:F5(:[A-F0-9]{2}){3}', board.before).group()
        self.__checkMac(mac2, mac0, 2)
        board.sendline('\ncat /sys/class/net/eth0/address')
        board.expect('eth0/address')
        board.expect(prompt)
        mac3 = re.search(r'00:19:f5(:[a-f0-9]{2}){3}', board.before).group()
        self.__checkMac(mac3, mac0, 3)
        board.sendline('\ncat /sys/class/net/lowpan0/address')
        board.expect('lowpan0/address')
        board.expect(prompt)
        # skipping mac4, it's a placeholder to represent MAC address for Mesh interface
        mac5 = re.search(r'02:19:f5:ff:fe(:[a-f0-9]{2}){3}', board.before).group()
        self.__checkMac(mac5, mac0, 5)
        board.sendline('\ncat /sys/class/net/wpan0/address')
        board.expect('wpan0/address')
        board.expect(prompt)
        mac5 = re.search(r'02:19:f5:ff:fe(:[a-f0-9]{2}){3}', board.before).group()
        self.__checkMac(mac5, mac0, 5)

class MemoryUse(rootfs_boot.RootFSBootTest):
    '''Checked memory use.'''
    def runTest(self):
        board.sendline('\nsync; echo 3 > /proc/sys/vm/drop_caches')
        board.expect('echo 3')
        board.expect(prompt, timeout=5)
        # There appears to be a tiny, tiny chance that
        # /proc/meminfo won't exist, so try one more time.
        for i in range(2):
            try:
                board.sendline('cat /proc/meminfo')
                board.expect('MemTotal:\s+(\d+) kB', timeout=5)
                break
            except:
                pass
        mem_total = int(board.match.group(1))
        board.expect('MemFree:\s+(\d+) kB')
        mem_free = int(board.match.group(1))
        board.expect(prompt)
        mem_used = mem_total - mem_free
        self.result_message = 'Used memory: %s MB. Free memory: %s MB.' % (mem_used/1000, mem_free/1000)
        self.logged['mem_used'] = mem_used/1000

class Sleep2Minutes(rootfs_boot.RootFSBootTest):
    '''Slept 2 minutes.'''
    def recover(self):
        board.sendcontrol('c')
    def runTest(self):
        # Connections time out after 2 minutes, so this is useful to have.
        board.sendline('\n date')
        board.expect('date')
        board.expect(prompt)
        board.sendline('sleep 120')
        board.expect('sleep ')
        board.expect(prompt, timeout=130)
        board.sendline('date')
        board.expect('date')
        board.expect(prompt)

class Sleep5Minutes(rootfs_boot.RootFSBootTest):
    '''Slept 5 minutes.'''
    def recover(self):
        board.sendcontrol('c')
    def runTest(self):
        board.sendline('\n date')
        board.expect('date')
        board.expect(prompt)
        board.sendline('sleep 300')
        board.expect('sleep ')
        board.expect(prompt, timeout=310)
        board.sendline('date')
        board.expect('date')
        board.expect(prompt)
