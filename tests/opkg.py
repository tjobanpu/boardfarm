# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import time

import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class OpkgList(rootfs_boot.RootFSBootTest):
    '''Opkg list shows installed packages.'''
    def runTest(self):
        board.sendline('\nopkg list-installed | wc -l')
        board.expect('opkg list')
        board.expect('(\d+)\r\n')
        num_pkgs = int(board.match.group(1))
        board.expect(prompt)
        board.sendline('opkg list-installed')
        board.expect(prompt)
        self.result_message = '%s OpenWrt packages are installed.' % num_pkgs
        self.logged['num_installed'] = num_pkgs

class CheckQosScripts(rootfs_boot.RootFSBootTest):
    '''Package "qos-scripts" is not installed.'''
    def runTest(self):
        board.sendline('\nopkg list-installed | grep qos-scripts')
        try:
            board.expect('qos-scripts - ', timeout=4)
        except:
            return   # pass if not installed
        assert False # fail if installed

class OpkgUpdate(rootfs_boot.RootFSBootTest):
    '''Opkg is able to update list of packages.'''
    def runTest(self):
        board.sendline("\nopkg update | tee opkg.txt && ! grep 'Signature check failed' opkg.txt"
                        "&& echo 'All package lists updated' && rm opkg.txt")
        board.expect('Updated list of available packages')
        board.expect('All package lists updated')
        board.expect(prompt)

    def recover(self):
        board.sendline('\nrm opkg.txt')
        board.expect(prompt)

class OpkgInstall(rootfs_boot.RootFSBootTest):
    '''Opkg is able to install selected packages'''
    def runTest(self):
        # One package per feed: packages, openwrt-routing, openwrt-managements,
        # ci40-platform-feed, telephony, luci
        packages = [ "nano", "mrd6", "libssh", "glog", "miax", "luci-mod-rpc" ]
        for pkg in packages:
            board.sendline("\nopkg install {}".format(pkg))
            board.expect("Configuring {}".format(pkg))
            board.expect(prompt)
