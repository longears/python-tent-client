try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from tentapp import __version__ as version

setup(
    name='tentapp',
    version=version,
    packages=['tentapp'],
    install_requires=['requests'],

    author='David Wallace',
    author_email='david.wallace+tentapp@gmail.com',
    url='https://github.com/longears/python-tent-client/',

    license='MIT License',
    description='Python client/app library for the Tent protocol (https://tent.io)',
    long_description=open('README.md','r').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
        'Topic :: Communications',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)



