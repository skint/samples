# coding: utf8
# created: 2014-05-18 13:58:03
# Copyright @ 2014 breaker <breaker@broken.su>

from setuptools import setup

setup(
    name='Flashlight',
    version='0.0.1',
    packages=['flashlight'],
    license='LICENSE',
    description='Sample network flashlight',
    author='Maxim Kamyshev',
    author_email='breaker@broken.su',
    install_requires=['tornado'],
    package_data={'': ['tmpl/index.html']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'flashlight = flashlight.flashlight:run',
        ]
    }
)
