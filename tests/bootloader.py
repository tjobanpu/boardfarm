# Copyright (c) 2017
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.

import rootfs_boot
from devices import board, prompt

class UBootVars(rootfs_boot.RootFSBootTest):
    '''UBootVars prints U-boot environment variables.'''
    def runTest(self):
        variables=['loadaddr=0x0E000000', 'stdin=uart@18101500', 'boot_partition=(\d)']
        board.sendline('fw_printenv | tee uboot_vars && echo \"U-boot environment variables\"')
        board.expect('U-boot environment variables')
        board.expect(prompt)
        for v in variables:
            board.sendline('egrep -o "{}" uboot_vars'.format(v))
            board.expect(v)
            board.expect(prompt)
        board.sendline('\nrm -f uboot_vars')
        board.expect(prompt)

    def recover(self):
        board.sendline('\nrm -f uboot_vars')
        board.expect(prompt)

