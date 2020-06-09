# QGIS_python_fmask
QGIS interface to python-fmask

We want to make Python FMask available in QGIS.

Making the QGIS interface is easy. But FMask has to be built for the particular system.

The plan is to take the ready-built versions of [`python-fmask`](https://anaconda.org/conda-forge/python-fmask) and [`rios`](https://anaconda.org/conda-forge/rios) from `conda-forge` and just dump them somewhere in QGIS's PYTHONPATH.

Too bad QGIS is not using `conda`.


## Installation

You need make `python-fmask` and its dependency`rios` available to your QGIS Python.

You can download the packages that suit your system from the `conda-forge` channel builds for [`python-fmask`](https://anaconda.org/conda-forge/python-fmask) and [`rios`](https://anaconda.org/conda-forge/rios).

For your convenience, this repo includes the builds for 
* Windows 64 with Python 2.7 and Numpy 1.12 (`python-fmask-0.4.4-np112py27_0` and `rios-1.4.3-py27_1`)
* More to follow

So an easy way to install for users with this configuration is to pick the right bundle from the `dependencies` folder and unpack it to your QGIS Python `site=packages` directory, e.g. `C:\OSGeo4W64\apps\Python27\Lib\site-packages`.

All others, just do the same the files from `conda-forge`. You need only the contents of the `Lib/site-packages` folder.

Then place this repo somewhere in your `~/.qgis2/processing/scripts` folder and you are ready to go.
