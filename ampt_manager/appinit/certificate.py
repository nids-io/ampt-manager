'''
Create self-signed SSL certificate for new AMPT instances

'''

import os
import stat
import uuid
from socket import gethostname
from time import gmtime, mktime
from os.path import exists, join
from OpenSSL import crypto, SSL

from .. import settings


CERT_FILE = 'ampt_manager.crt'
KEY_FILE = 'ampt_manager.key'
KEY_SIZE = settings.default_ssl_key_size

def create_self_signed_cert(cert_dir):
    '''
    If datacard.crt and datacard.key don't exist in cert_dir, create a new
    self-signed cert and keypair and write them into that directory.
    '''

    if (not exists(join(cert_dir, CERT_FILE))
        or not exists(join(cert_dir, KEY_FILE))):

        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, KEY_SIZE)

        # create a self-signed cert
        host_name = gethostname()
        serial_num = uuid.uuid4().int
        cert = crypto.X509()
        cert.get_subject().C = 'AU'
        cert.get_subject().ST = 'Some-State'
        cert.get_subject().L = 'Some-City'
        cert.get_subject().O = 'Internet Widgits Pty Ltd'
        cert.get_subject().OU = 'World Wide Web Pty Ltd'
        cert.get_subject().CN = host_name
        cert.set_serial_number(serial_num)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10*365*24*60*60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha256')

        with open(join(cert_dir, CERT_FILE), 'wb') as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        with open(join(cert_dir, KEY_FILE), 'wb') as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
            os.chmod(f.name, stat.S_IRUSR|stat.S_IWUSR)

