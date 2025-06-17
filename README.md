# Fish project

## Setup

Start jupyter server:
```
./server/start_jupyter_on_tmux.sh
```




## Contribution guidance

In order to contribute the code must be typed, formated and tested.
Merge to master should be done via pull requests. It is configured to run some jobs with CI.

Commands to maintain code quality:

```
mypy .
ruff format
ruff check --fix
pytest -n auto
pytest -n auto -m "not slow" # avoids slower integration tests
```


## Tips


### Git

Example on some selective git command that is good to know.

Contribute:
```
git commit -m "YOUR_COMMIT_MESSAGE"          # very normal git commit
git commit --amend                           # update commit
git log --show-signature                     # see logs with signatures
git push                                     # push active branch
gh pr create --base master --head develop    # create PR
```

Get latest code
```
git fetch origin master:master
git pull origin master
git merge master
git rebase master
```

Add keys if needed
```
ssh -T git@github.com
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
ssh-add ~/.ssh/id_rsa
ssh-add ~/.ssh/id_ed25519_personal
echo "$SSH_AUTH_SOCK"
```


### Useful commands that good to know

Port forwarding (if needed)
```
ssh -L 5000:localhost:5000 ubuntu@cofc2.analytics.strudel.lt
```

Make file executable
```
chmod +x server/start_jupyter_on_tmux.sh
```

Read premisions:
```
chmod -R go+rX mydir
```

Kill all python jobs (in worst case)
```
ps -ef | grep python
pkill -9 python
ps -ef | grep cml-vygantas
sudo systemctl restart docker
```



### Useful pycharm settings

```python
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
plt.ion()

import pandas as pd
# pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 1000)
pd.set_option('display.min_rows', 200)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 400)

import seaborn as sns
sns.set(style="darkgrid")

import numpy as np
np.set_printoptions(edgeitems=30, linewidth=100000,
    formatter=dict(float=lambda x: "%.3g" % x))

import numpy as np
np.set_printoptions(edgeitems=30, linewidth=100000,
    formatter=dict(float=lambda x: "%.3g" % x))
```
