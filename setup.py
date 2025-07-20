# setup.py

from setuptools import setup

setup(
    name="Kaos-Tunes",
    version="2.0.0",
    description="Kaos Tunes v2.0 - A telemetry-free, DRM-free, privacy-respecting media player.",
    author="Kaotick Jay",
    author_email="kaotickj@gmail.com",
    url="https://github.com/kaotickj/Python-Music-Player",
    license="GPL-3.0-or-later",
    py_modules=["K-Tunes"],
    install_requires=[
        "Pillow",
        "pygame",
        "mutagen",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Players",
    ],
    python_requires=">=3.6",
)
