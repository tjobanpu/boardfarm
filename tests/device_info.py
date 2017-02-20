# Copyright (c) 2015
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import rootfs_boot
from devices import board, prompt

class DeviceInfo(rootfs_boot.RootFSBootTest):
    '''Check device information of Ci40 board.'''
    def runTest(self):
        board.sendline('\ncat /etc/device_info')
        board.expect('cat /etc/device_info', timeout=6)
        board.expect('DEVICE_MANUFACTURER=\'Imagination Technologies\'')
        board.expect('DEVICE_MANUFACTURER_URL=\'www.imgtec.com\'')
        board.expect('DEVICE_PRODUCT=\'Creator Ci40\\(marduk\\)\'')
        board.expect('DEVICE_REVISION=\'v0\'') # Until CreatorDev/openwrt#293 is fixed
        board.expect(prompt)
