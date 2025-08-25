"""
Setup script for devtools package.
"""

from setuptools import setup, find_packages

setup(
    name="devtools-utils",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "requests>=2.25.0",
        "pyyaml>=5.0.0",
    ],
    entry_points={
        "console_scripts": [
            "devtools=devtools.cli:cli",
        ],
    },
    author="Sankalp Tharu",
    author_email="sankalptharu50028@gmail.com",
    description="A collection of developer tools",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/S4NKALP/DevTools",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)
