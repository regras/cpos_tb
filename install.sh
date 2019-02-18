#!/bin/bash

# dependencies install
sudo apt-get install -y libzmq3-dev
if ! [ -x "$(command -v pip)" ]; then
  sudo apt-get install -y pip
fi
python -m pip install pyzmq

# create executable files
touch blockchain-cli < #!/bin/bash\npython rpc/rpcclient.py $*
chmod +x blockchain-cli 
