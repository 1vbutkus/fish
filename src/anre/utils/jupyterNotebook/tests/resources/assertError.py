# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown] editable=true deletable=true frozen=false
# # With error

# %% tags=["parameters"] editable=true deletable=true frozen=false
x = 1
y = None

# %% editable=true deletable=true frozen=false
from anre.utils.jupyterNotebook.jupyterNotebook import JupyterNotebook  # noqa: E402

JupyterNotebook.setup_screen(interactive=False)

# %% editable=true deletable=true frozen=false

# %% editable=true deletable=true frozen=false
assert x < 0

# %% editable=true deletable=true frozen=false
