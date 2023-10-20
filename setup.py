"""setup.py file for the androidtv package."""

from setuptools import setup

with open("README.rst") as f:
    readme = f.read()

setup(
    name="androidtv",
    version="0.0.73",
    description="Communicate with an Android TV or Fire TV device via ADB over a network.",
    long_description=readme,
    keywords=["adb", "android", "androidtv", "firetv"],
    url="https://github.com/JeffLIrion/python-androidtv/",
    license="MIT",
    author="Jeff Irion",
    author_email="jefflirion@users.noreply.github.com",
    packages=["androidtv", "androidtv.adb_manager", "androidtv.basetv", "androidtv.androidtv", "androidtv.firetv"],
    install_requires=["adb-shell>=0.4.0", "pure-python-adb>=0.3.0.dev0"],
    extras_require={"async": ["aiofiles>=0.4.0", "async_timeout>=3.0.0"], "usb": ["adb-shell[usb]>=0.4.0"]},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
    ],
    test_suite="tests",
)
