'''
AMPT-manager setup
'''

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ampt-manager',
    version='0.4.2',
    description=('AMPT-manager, a web application that manages passive '
                 'network device monitoring'),
    long_description=long_description,
    url='https://github.com/nids-io/ampt-manager',
    author='AMPT Project',
    author_email='ampt@nids.io',
    license='BSD',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Security',
        'Topic :: System :: Networking :: Monitoring',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5',
        'Operating System :: POSIX',
        'Framework :: Flask',
    ],
    keywords='ampt, ampt-manager, a passive network health monitoring tool',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask-Bcrypt',
        'Flask-Classy',
        'Flask-DebugToolbar',
        'Flask-Login',
        'Flask-Mail',
        'Flask-Misaka',
        'Flask-Moment',
        'Flask-WTF',
        'Gunicorn',
        'peewee',
        'pyOpenSSL',
        'requests',
        'setproctitle',
        'WTForms',
    ],
    entry_points={
        'console_scripts': [
            'ampt-manager=ampt_manager.cli:main',
        ],
    },
)
