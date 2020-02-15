from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='androidtv',
    version='0.0.39',
    description='Communicate with an Android TV or Fire TV device via ADB over a network.',
    long_description=readme,
    keywords=['adb', 'android', 'androidtv', 'firetv'],
    url='https://github.com/JeffLIrion/python-androidtv/',
    license='MIT',
    author='Jeff Irion',
    author_email='jefflirion@users.noreply.github.com',
    packages=['androidtv'],
    install_requires=['adb-shell>=0.1.0', 'pure-python-adb>=0.2.2.dev0'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
    ],
    test_suite='tests'
)
