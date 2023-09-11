# Visualizing Text2Shape
Visualization tool for [Text2Shape dataset](http://text2shape.stanford.edu/).

## Overview
This repository provides some visualization tools for [Text2Shape dataset](http://text2shape.stanford.edu/). This dataset has been introduced in 2018 and provides paired data samples of 3D shapes and text descriptions.

## Download
The 3D shapes of Text2Shape belong to the categories "chair" and "table" of [ShapeNet](https://shapenet.org/).
Text2Shape provides the voxelgrids of such objects and multiple textual descriptions for each of them.
Since in our visualization, we make use of the mesh representation for the shapes, it is preferable to download directly the meshes from ShapeNet.
Thus, data can be downloaded in the following way:
* 3D shapes can be downloaded from [ShapeNet website](https://shapenet.org/) (download section)
* textual descriptions can be found in a csv file, which can be downloaded from [Text2Shape website](http://text2shape.stanford.edu/) (ShapeNet Downloads => Text Descriptions).

## Installation
Python 3.8 is required.

Create and activate a virtual environment
```console
python -m venv env
source env/bin/activate
```

Install the required libraries: BLENDER Python API [bpy](https://docs.blender.org/api/current/index.html), [Open3D](http://www.open3d.org/) and [Matplolib](https://matplotlib.org/)
```console
pip install bpy
pip install open3d
pip install 
```

## First visualization: renderings of 3D shapes with corresponding text
### Generation of the rendered views
### Plot of the rendered views, with text prompts


## Second visualization: word clouds