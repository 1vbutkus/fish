#!/bin/bash
# bash server/start_jupyter_on_tmux.sh

ENVIRONMENT_NAME="fish"
if test -f _local/environment_name.txt; then
  ENVIRONMENT_NAME=$(cat _local/environment_name.txt)
fi
echo environment: $ENVIRONMENT_NAME

JUPYTER_PORT="5000"

/usr/bin/tmux new-session -d -s jupyter_fish
/usr/bin/tmux send-keys "export JUPYTER_CONFIG_DIR=~/F/Vygantas/projektai/fish/_local/.jupyter" 'C-m'
/usr/bin/tmux send-keys "cd ~/F/Vygantas/projektai/fish" 'C-m'
/usr/bin/tmux send-keys "conda activate $ENVIRONMENT_NAME" 'C-m'
/usr/bin/tmux send-keys "poetry run jupyter lab --no-browser --port=$JUPYTER_PORT --ip 0.0.0.0" 'C-m'

echo "Started jupyter server: http://127.0.0.1:$ENVIRONMENT_NAME/lab"


### set password
# jupyter lab --generate-config
# jupyter lab password

