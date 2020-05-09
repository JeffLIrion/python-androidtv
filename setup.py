from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='aio_androidtv',
    version='0.0.1',
    description='Communicate with an Android TV or Fire TV device via ADB over a network.',
    long_description=readme,
    keywords=['adb', 'android', 'aio_androidtv', 'firetv'],
    url='https://github.com/JeffLIrion/python-aio_androidtv/',
    license='MIT',
    author='Jeff Irion',
    author_email='jefflirion@users.noreply.github.com',
    packages=['aio_androidtv'],
    install_requires=['adb-shell>=0.1.3', 'pure-python-adb>=0.2.2.dev0', 'aio-adb-shell'],
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    test_suite='tests'
)
