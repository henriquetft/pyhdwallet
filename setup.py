import setuptools
import re

with open("README.md", "r") as fh:
    long_description = fh.read()

# retrieves version from __init__.py
with open("pyhdwallet/__init__.py", encoding="utf8") as f:
    version = re.search(r'__version__\s*=\s*"(.*?)"', f.read()).group(1)

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="pyhdwallet",
    version=version,
    author="henriquetft",
    author_email="henrique@teofilo.me",
    description="A Python lib for working with BIP32 (Hierarchical Deterministic Wallets)",
    long_description=long_description,
    license='BSD',
    long_description_content_type="text/markdown",
    url="https://github.com/henriquetft/pyhdwallet",
    packages=setuptools.find_packages(),
    keywords=["cryptocurrency", "bitcoin", "bip32", "python", "crypto",
              "wallet", "hierarchical-deterministic-wallets", "hdwallet",
              "bitcoincash"],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers"
    ],
    python_requires='>=3.6',
)