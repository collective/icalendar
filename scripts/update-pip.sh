#!/usr/bin/env bash
# upgrade pip
# see https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576

set -ev

apt update

# upgrade certificates
# see https://discuss.python.org/t/information-for-python-users-regarding-emudhra-emsign-ca-certificate-security-incident/109576/10
apt install --upgrade ca-certificates

python -m pip --version

echo Install the safe version of pip
python -m pip install "pip @ https://files.pythonhosted.org/packages/3f/06/3e4420302363fbb71be3c7f35ce042f54bfca330e3e66b3a2e3c4cca579f/pip-26.2.2-py3-none-any.whl#sha256=fd7f4dfa8190e014013b9f08f3e973f4e4c26ffd179a204895533a7254813a70"

echo Update certifi
python -m pip install --upgrade certifi

echo "Update pip"
python -m pip install --upgrade pip

python -m pip --version

echo "Update successful. Pip can now be used to install packages."
