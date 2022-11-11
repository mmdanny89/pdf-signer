from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in pdf_signer/__init__.py
from pdf_signer import __version__ as version

setup(
	name="pdf_signer",
	version=version,
	description="Application for signing PDF files",
	author="Danny Molina Morales",
	author_email="mmdanny89@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
