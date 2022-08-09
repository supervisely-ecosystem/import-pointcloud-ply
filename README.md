<div align="center" markdown>

<img src="https://user-images.githubusercontent.com/106374579/183657811-118e7a0a-29b0-4dfe-874f-3f70c3cf1352.png"/>  

# Import Pointclouds PLY

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#Demo">Demo</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/import-pointcloud-ply)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-pointcloud-ply)
[![views](https://app.supervise.ly/img/badges/views/supervisely-ecosystem/import-pointcloud-ply.png)](https://supervise.ly)
[![runs](https://app.supervise.ly/img/badges/runs/supervisely-ecosystem/import-pointcloud-ply.png)](https://supervise.ly)

</div>

# Overview

This app allows you to upload pointcloud PLY files with (or without) related images.
These files will be automatically converted to `.PCD` format and uploaded to Supervisely.
The new pointloud project will be created. 

Be aware that "remove files after successful import" flag is enabled by default, it will automatically remove source directory after import.

**Input files structure**

Directory name defines project name, subdirectories define dataset names. Files in root directory will be moved to dataset with name "`ds0`".

**Example 1. Import structure:**

```
my_project
├── xxx.ply
├── ds_ny
│   └── frame.ply
└── ds_sf
    └── kitti_0000000001.ply
```

In this case the following datasets will be created:

- `ds_0` with a single file `xxx.ply`
- `ds_ny` with a single file `frame.ply`
- `ds_sf` with a single file `kitti_0000000001.ply`


**Example 2. Import structure:**

```
my_project
└── dataset_01
    ├── xxx.ply
    ├── ds_ny
    │   └── frame.ply
    └── ds_sf
        └── kitti_0000000001.ply
```

In this case only the one dataset `dataset_01` will be created with all pointcloud files.


**Example 3. PLY files with photo context:**


```
my_project
└── dataset_01
    ├── frame.ply
    ├── kitti_0000000001.ply
    └── related_images
        └── kitti_0000000001_ply
            ├── 0000000000.png
            └── 0000000000.png.json
```

if you want to attach photo context to ply file just create a directory `related_images` near the file. 
Then create directory <filename_with_ext> (in this example we name directory kitti_0000000001_ply - it's a filename + extension + all symbols . are replaced to _) 
and put there images and corresponding json files with projection matrix. See example for more info.

As a result we will get project `my_project` with 1 dataset `dataset_01`. Dataset will contain 2 pointcloud files, `kitti_0000000001.ply` with related image, and `frame.ply` without related image.

# How to Run

**Step 1.** Add [Import Pointclouds PLY](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/import-pointcloud-ply) app to your team from Ecosystem

<img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/import-pointcloud-ply" src="https://i.imgur.com/7AHFXQ3.png" width="500px" style='padding-bottom: 10px'/>

**Step 2.** Run the application from the context menu of the directory with pointclouds on Team Files page

<img src="https://i.imgur.com/NepdSfq.png" width="100%" style='padding-top: 10px'>  

**Step 3.** Select options and press the Run button

<img src="https://i.imgur.com/ezaUHE9.png" width="80%" style='padding-top: 10px'>  

### Demo
Example of uploading pointclouds:
![](https://i.imgur.com/CPQTrm1.gif)
