import rootfs_boot
from devices import board, wan, lan, wlan, prompt

class CurlSSLGood(rootfs_boot.RootFSBootTest):
    '''Curl can access https and verify signature.'''
    def runTest(self):
        board.sendline('\n')
        board.expect(prompt)
        board.sendline('opkg install ca-certificates')
        board.expect(prompt)
        checks = [ 
                   'https://sha256.badssl.com/',
                   'https://dh2048.badssl.com/',
                   'https://hsts.badssl.com/',
                   'https://upgrade.badssl.com/',
                   'https://preloaded-hsts.badssl.com/',
                 ]
        for check in checks:
            board.sendline('curl ' + check)
            board.expect('<!DOCTYPE html>')
            board.expect(prompt)
            print '\n\nCurl downloaded ' + check + ' as expected\n'

class CurlSSLBad(rootfs_boot.RootFSBootTest):
    '''Curl can't access https with bad signature.'''
    def runTest(self):
        board.sendline('\n')
        board.expect(prompt)
        board.sendline('opkg install ca-certificates')
        board.expect(prompt)
        checks = [
                   ('https://expired.badssl.com/', 'BADCERT_EXPIRED'),
                   ('https://wrong.host.badssl.com/', 'BADCERT_CN_MISMATCH'),
                   ('https://subdomain.preloaded-hsts.badssl.com/', 'BADCERT_CN_MISMATCH'),
                   ('https://self-signed.badssl.com/', 'BADCERT_NOT_TRUSTED'),
                   ('https://superfish.badssl.com/', 'Connection was reset by peer'),
                   ('https://edellroot.badssl.com/', 'BADCERT_NOT_TRUSTED'),
                   ('https://dsdtestprovider.badssl.com/', 'BADCERT_NOT_TRUSTED'),
                   ('https://incomplete-chain.badssl.com/', 'BADCERT_NOT_TRUSTED'),
                 ]
        for check in checks:
            board.sendline('curl ' + check[0])
            board.expect(check[1])
            board.expect(prompt)
            print '\n\nCurl refused to download ' + check[0] + ' as expected\n'
 
