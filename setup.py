#!/usr/bin/python

from setuptools import setup 

setup(
    name='hammock',
    version='0.1.3',
    license='MIT',
    author='avengineers',
    author_email='avengineers@gmail.com',
    url='http://github.com/avengineers/hammock',
    description='Create mocks for c-code automatically',
    packages=['hammock'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'libclang',
        'Jinja2'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python'
        ])
