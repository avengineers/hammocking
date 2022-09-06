#!/usr/bin/python

from setuptools import setup 

setup(
    name='hammocking',
    license='MIT',
    author='avengineers',
    author_email='avengineers@gmail.com',
    url='https://avengineers.github.io/hammocking',
    description='Create mocks for c-code automatically',
    long_description = 'Create mocks for c-code automatically',
    long_description_content_type = 'text/x-rst',   
    packages=['hammocking'],
    include_package_data=True,
    zip_safe=False,
    use_scm_version=True,
    setup_requires=[
        'setuptools_scm'
    ],
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
