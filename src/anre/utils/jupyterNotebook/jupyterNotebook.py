import os
import subprocess
import warnings
from pathlib import Path

import IPython
import jupytext
import matplotlib.pyplot as plt
import papermill as pm

from anre.utils.functions import get_randomStr


class JupyterNotebook:
    @classmethod
    def setup_screen(cls, interactive: bool = True):
        iPython = IPython.get_ipython()
        gui = 'widget' if interactive else 'inline'
        iPython.enable_matplotlib(gui=gui)

        import seaborn as sns

        sns.set_style(style="darkgrid")

        # from IPython.display import display, HTML
        # display(HTML("<style>:root { --jp-notebook-max-width: 100% !important; }</style>"))
        # display(HTML("<style>.container { width:100% !important; }</style>"))
        # display(HTML("<style>.CodeMirror {background-color: #EEEEEE;} </style>"))

        import pandas as pd

        pd.set_option('display.max_rows', 100)
        pd.set_option('display.min_rows', 100)
        pd.set_option('display.max_columns', 100)
        pd.set_option('display.width', 260)
        pd.set_option('display.max_colwidth', 260)
        if interactive:
            plt.rcParams['figure.figsize'] = (18, 7)
        else:
            plt.rcParams['figure.figsize'] = (23, 9)

        import numpy as np

        np.set_printoptions(
            edgeitems=30, linewidth=100000, formatter=dict(float=lambda x: "%.3g" % x)
        )

    @staticmethod
    def convert_jupyter2html(
        jupyterFilePath: str, override: bool = False, execute: bool = False, asReport: bool = False
    ) -> str:
        assert os.path.exists(jupyterFilePath), f'jupyterFilePath does not found: {jupyterFilePath}'
        inputPathObj = Path(jupyterFilePath)
        assert inputPathObj.suffix == '.ipynb', 'Input file is not Jupyter Notebook (.ipynb)'

        outputPathObj = Path(jupyterFilePath).with_suffix('.html')
        assert override or not os.path.exists(outputPathObj), (
            f'Output file exists. Use override if needed. File: {outputPathObj}'
        )

        call_args = ['jupyter', 'nbconvert', jupyterFilePath, '--to', 'html']
        if execute:
            call_args.append('--execute')
        if asReport:
            call_args.extend(['--no-input', '--no-prompt'])

        process = subprocess.Popen(call_args, shell=False)
        process.wait()

        assert os.path.exists(outputPathObj), f'Output file not found: {outputPathObj}'
        return str(outputPathObj.absolute())

    @classmethod
    def run_jupyterTemplate(
        cls,
        templateFilePath: str,
        outputFilePath: str,
        parameters: dict | None = None,
        override: bool = False,
        convertToHtml: bool = False,
        asReport: bool = False,
        progress_bar: bool = False,
    ):
        try:
            res = cls._run_jupyterTemplate(
                templateFilePath=templateFilePath,
                outputFilePath=outputFilePath,
                parameters=parameters,
                override=override,
                convertToHtml=convertToHtml,
                asReport=asReport,
                progress_bar=progress_bar,
            )
            return res
        except BaseException:
            msg = f'Error running report: {templateFilePath}]\nparameters:{parameters}'
            print(msg)
            raise

    @classmethod
    def _run_jupyterTemplate(
        cls,
        templateFilePath: str,
        outputFilePath: str,
        parameters: dict | None,
        override: bool,
        convertToHtml: bool,
        asReport: bool,
        progress_bar: bool,
    ) -> list[str]:
        parameters = parameters if parameters is not None else dict()
        assert os.path.exists(templateFilePath), (
            f'templateFilePath does not found: {templateFilePath}'
        )

        inputPathObj = Path(templateFilePath)
        assert inputPathObj.suffix in ['.ipynb', '.py'], (
            'Input file is not Jupyter Notebook (.ipynb or .py)'
        )

        outputPathObj = Path(outputFilePath)
        assert outputPathObj.suffix == '.ipynb', 'Output file is not Jupyter Notebook (.ipynb)'

        if os.path.exists(outputPathObj) and not override:
            msg = f'Output file exists. Use override if needed. File: {outputPathObj}'
            raise FileExistsError(msg)

        outputPathObj.parent.mkdir(mode=0o777, parents=True, exist_ok=True)
        assert outputPathObj.parent.exists(), (
            f'Output directory does not exists: {outputPathObj.parent}'
        )

        templateFilePath_temp = None
        if inputPathObj.suffix == '.py':
            ntbk = jupytext.read(templateFilePath)
            templateFilePath_temp = os.path.join(
                outputPathObj.parent, f'_temp_{get_randomStr(32)}_{outputPathObj.name}'
            )
            jupytext.write(ntbk, templateFilePath_temp)
            templateFilePath = templateFilePath_temp

        output_file_path_temp = os.path.join(
            outputPathObj.parent, f'_in_proc_{get_randomStr(32)}_{outputPathObj.name}'
        )

        with warnings.catch_warnings():
            warnings.filterwarnings(
                action='ignore',
                message="Passing unrecognized arguments to super",
                category=DeprecationWarning,
                module='traitlets',
            )
            warnings.filterwarnings(
                action='ignore',
                message="Jupyter is migrating its paths to use standard platformdirs",
                category=DeprecationWarning,
                module='jupyterNotebook',
            )
            warnings.filterwarnings(
                action='ignore',
                message="zmq.eventloop.ioloop is deprecated in pyzmq",
                category=DeprecationWarning,
                module='jupyterNotebook',
            )
            warnings.filterwarnings(
                action='ignore',
                message="the imp module is deprecated in favour of importlib and slated for removal",
                category=DeprecationWarning,
                module='ansiwrap',
            )
            _ = pm.execute_notebook(
                input_path=templateFilePath,
                output_path=output_file_path_temp,
                parameters=parameters,
                progress_bar=progress_bar,
            )

        assert os.path.exists(output_file_path_temp), (
            f'Output file not  found: {output_file_path_temp}'
        )
        os.replace(output_file_path_temp, outputFilePath)
        assert os.path.exists(outputFilePath), f'Output file not  found: {outputPathObj}'
        resList = [outputFilePath]

        # clean temp file:
        if templateFilePath_temp is not None:
            if os.path.exists(templateFilePath_temp):
                os.remove(templateFilePath_temp)

        if convertToHtml:
            htmlFilePath = cls.convert_jupyter2html(
                jupyterFilePath=outputFilePath, override=True, execute=False, asReport=asReport
            )
            resList.append(htmlFilePath)

        return resList
