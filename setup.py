
from setuptools import setup

setup(
    name='ixf',
    version=open('config/VERSION').read().rstrip(),
    description='IX-F db access and tools',
    long_description=open('README.rst').read(),
    license='LICENSE',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=['ixf'],
    url='http://ix-f.net/',
    maintainer='Matt Griswold',
    maintainer_email='grizz@dipd.com',
    zip_safe=False
    )
