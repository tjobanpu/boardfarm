# Copyright (c) 2017
#
# All rights reserved.
#
# This file is distributed under the Clear BSD license.
# The full text can be found in LICENSE in the root directory.
import os
import rootfs_boot
from devices import board

class BoardPing6ClickerDev(rootfs_boot.RootFSBootTest):
	'''Board lowpan interface can ping6 the clicker.'''
	def runTest(self):
		CLICKER_IP=os.getenv('CLICKER1_IP')
		board.sendline('\nping6 -I lowpan0 -c 20 -s 80 {}\n'.format(CLICKER_IP))
		board.expect('PING ')
		board.expect(' ([0-9]+) packets received')
		board.expect(' ([0-1]+)% packet loss')
		n = int(board.match.group(1))
		board.expect(prompt)
		assert n > 0
