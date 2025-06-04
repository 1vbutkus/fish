#!/bin/bash
# . setup.sh

ENVIRONMENT_NAME="fish"
if test -f _local/environment_name.txt; then
  ENVIRONMENT_NAME=$(cat _local/environment_name.txt)
fi
echo environment: $ENVIRONMENT_NAME


### one time setup of the project
# poetry init
# chmod +rwx setup.sh

# conda deactivate
# conda remove -n fish --all -y
conda create -y -n $ENVIRONMENT_NAME -c conda-forge python=3.11 --no-default-packages
conda init
conda activate $ENVIRONMENT_NAME
poetry install

# conda env config vars list
conda env config vars set JUPYTER_PLATFORM_DIRS=1 -n $ENVIRONMENT_NAME
conda deactivate
conda activate $ENVIRONMENT_NAME


jupyter labextension enable
# poetry add jupyterlab_freeze
# poetry add jupyterlab_execute_time
# poetry run jupyter lab

## cd libs
## git submodule add https://github.com/1vbutkus/py-clob-client.git
## poetry add --editable ./libs/py-clob-client


echo --------------------- The last line of the script. Have a good day ------------------------
