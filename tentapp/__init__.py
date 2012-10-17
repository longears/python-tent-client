
import sys

try:
    import requests
except ImportError:
    print >>sys.stderr, 'The tentapp library requires that you have the "requests" library installed.  Run "pip install requests".'

__version__ = '0.1.0dev2'

from tentapp import (
    TentApp,
    KeyStore,
    DiscoveryFailure,
    RegistrationFailure,
    AuthRequestFailure,
    ConnectionFailure,
)

