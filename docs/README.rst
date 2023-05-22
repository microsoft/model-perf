=============================
Model Performance Toolkit
=============================

Installation
============================


**Build and Install from Source**

Firstly, build and install [MLPerf LoadGen](https://github.com/mlcommons/inference/blob/master/loadgen/README_BUILD.md).

.. code:: bash

    git clone https://github.com/microsoft/model-perf
    cd python
    python -m pip install -e .

Example
============================

.. code:: python

    # pass

Build the Docs
=============================

Run the following commands and open ``docs/_build/html/index.html`` in browser.

.. code:: bash

    pip install sphinx myst-parser sphinx-rtd-theme sphinxemoji
    cd docs/

    make html         # for linux
    .\make.bat html   # for windows
