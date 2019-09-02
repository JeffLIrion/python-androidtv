from setuptools import setup

setup(
    name='androidtv',
    version='0.0.26',
    description='Communicate with an Android TV or Fire TV device via ADB over a network.',
    url='https://github.com/JeffLIrion/python-androidtv/',
    license='MIT',
    author='Jeff Irion',
    author_email='jefflirion@users.noreply.github.com',
    packages=['androidtv'],
    install_requires=['rsa', 'adb-homeassistant>=1.3.2', 'pure-python-adb-homeassistant>=0.1.7.dev0'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    test_suite='tests'
)
