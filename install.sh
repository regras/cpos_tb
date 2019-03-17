#!/bin/bash

# dependencies install
sudo apt-get install -y libzmq3-dev
if ! [ -x "$(command -v pip)" ]; then
  sudo apt-get install -y python-pip
fi
python -m pip install pyzmq
python -m pip install configparser
