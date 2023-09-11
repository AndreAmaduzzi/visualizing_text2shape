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
pip install wordcloud
```

## First visualization: renderings of 3D shapes with corresponding text
### Generation of the rendered views
The rendered views are captured from a virtual camera which is rotating around the 3D shape. We can specify the number of views to capture. The rendering pipeline will make sure to cover the whole range of 360 degress around the object.

To generate the rendered views for all the shapes of the dataset:
```console
python render_shapenet_obj.py --category all --views <views_per_shape>
```


To generate the rendered views for the shapes belonging to a single category (e.g. chairs or tables):
```console
python render_shapenet_obj.py --category Chair --views <views_per_shape>
```


To generate the rendered views for the shape provided as example in this repository:
```console
python render_shapenet_obj.py 
--obj_path input_examples/a682c4bf731e3af2ca6a405498436716.obj 
--views <views_per_shape>
```

The resulting renderings will be saved in the folder specified by the argument *output_folder*, being by default ***output_renders/***.

### Plot of the rendered views, with text prompts
Once obtained all renderings, we can plot the views for a specific shape and the corresponding textual descriptions.
```console
python plot_renderings.py 
--obj_path <path to .obj file of the 3D shape>
```

The output figure will we saved in the folder specified by the argument *output_folder*, being by default ***output_plots/***.
The code is able to automatically adjust the positioning and size of the views, according to their number (if 20, 10, 5...).
Below, we report the figure with 20 views and with 10 views.
![alt text](https://raw.githubusercontent.com/AndreAmaduzzi/visualizing_text2shape/main/output_examples/output_renderings_20.png)
![alt text](https://raw.githubusercontent.com/AndreAmaduzzi/visualizing_text2shape/main/output_examples/output_renderings_10.png)


## Second visualization: word clouds
This visualization provides an understanding of the frequency with which different words appear in the textual descriptions of Text2Shape. 
To plot a wordcloud for the whole dataset:
```console
python plot_text.py
```

To plot a wordclous for a specific category of the dataset, such as chairs:
```console
python plot_text.py --category Chair
```

The resulting figure will be saved in the folder specified by the argument *output_folder*, being by default ***output_plots/***.
![alt text](https://raw.githubusercontent.com/AndreAmaduzzi/visualizing_text2shape/main/output_examples/worcloud_all.png)
