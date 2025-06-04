# This file contains commands for one-time setup of linux computer dedicated for ML

### install pipx
sudo apt update
sudo apt install pipx
pipx ensurepath
exit     # need restart the terminal


### install poetry
pipx install poetry
poetry self add poetry-dotenv-plugin

### install conda. (Butu gerai cia konkrecia versija naudoti, kad nebutu netiketu neatitikimu)
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh
# make auto-init then asked
exit     # need restart the terminal


### install rsync
sudo apt-get install rsync

### pg
apt-get install git libpq-dev -y

### compiles
sudo apt install build-essential

### else
sudo apt install tmux mc


