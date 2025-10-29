# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='ckanext-mahulu',
    version='0.0.1',
    description='Mahulu extension for CKAN',
    author='Ricko Caesar Aprilla Tiaka',
    author_email='you@example.com',
    license='AGPL',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points='''
        [ckan.plugins]
        mahulu=ckanext.mahulu.plugin:MahuluPlugin

        [babel.extractors]
        ckan = ckan.lib.extract:extract_ckan
    ''',
    message_extractors={
        'ckanext': [
            ('**.py', 'python', None),
            ('**.js', 'javascript', None),
            ('**/templates/**.html', 'ckan', None),
        ],
    }
)
