# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown] editable=true deletable=true frozen=false
# # Happy path test

# %% tags=["parameters"] editable=true deletable=true frozen=false
x = 1
y = None

# %% editable=true deletable=true frozen=false
from anre.utils.jupyterNotebook.jupyterNotebook import JupyterNotebook  # noqa: E402

JupyterNotebook.setup_screen(interactive=False)

# %% editable=true deletable=true frozen=false
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

# %% [markdown] editable=true deletable=true frozen=false
# ## Run report

# %% editable=true deletable=true frozen=false
y = y if y is not None else 5
ans = x + y
ans

# %% editable=true deletable=true frozen=false
sr = pd.Series([0, 1, 0, 2, 0, 3, 0, 4])

fig, ax = plt.subplots()
sr.plot(title='Test graph')
None

# %% editable=true deletable=true frozen=false
df = pd.DataFrame({'x1': sr, 'x2': np.log(1 + sr), 'x3': np.exp(sr)})
df.corr().style.background_gradient(cmap='coolwarm')
