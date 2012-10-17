
import sys

try:
    import requests
except ImpoerError:
    print >>sys.stderr, 'The tentapp library requires that you have the "requests" library installed.  Run "pip install requests".'

__version__ = '0.1.0'

from tentapp import (
    TentApp,
    KeyStore,
    DiscoveryFailure,
    RegistrationFailure,
    AuthRequestFailure,
    ConnectionFailure,
)

