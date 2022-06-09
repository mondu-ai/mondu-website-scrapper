import setuptools
from setuptools import setup

setup(
    name="mondu-website-scrapper",
    version="0.1.0",
    description="Web Scrapper",
    author="Mondu GmbH",
    package_data={"": ["client_secret.json", ".env"]},
    include_package_data=True,
)
