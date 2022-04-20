
<div align="center" markdown>
<img src="https://i.imgur.com/bgCPgfa.png"/>  

# Import Images

<p align="center">
  <a href="#Overview">Overview</a> •
  <a href="#How-To-Run">How To Run</a> •
  <a href="#Demo">Demo</a>
</p>

[![](https://img.shields.io/badge/supervisely-ecosystem-brightgreen)](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/import-images)
[![](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://supervise.ly/slack)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/supervisely-ecosystem/import-images)
[![views](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-images&counter=views&label=views)](https://supervise.ly)
[![used by teams](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-images&counter=downloads&label=used%20by%20teams)](https://supervise.ly)
[![runs](https://app.supervise.ly/public/api/v3/ecosystem.counters?repo=supervisely-ecosystem/import-images&counter=runs&label=runs&123)](https://supervise.ly)

</div>

# Overview

This app allows you to upload pointcloud PLY files with (or without) related images.
These files will be automatically converted to PCD format and uploaded to Supervisely.
The new pointloud project will be created. 

Be aware that "remove files after successful import" flag is enabled by default, it will automatically remove source directory after import.

#### Input files structure

Directory name defines project name, subdirectories define dataset names. Files in root directory will be moved to dataset with name "`ds0`".

**Example 1. Import structure:**

```
.
├── xxx.ply
├── ds_ny
│   └── frame.ply
└── ds_sf
    └── kitti_0000000001.ply
```

In this case the following datasets will be created

- `ds_0` with a single file `xxx.ply`
- `ds_ny` with a single file `frame.ply`
- `ds_sf` with a single file `kitti_0000000001.ply`


**Example 2. Import structure:**

```
abcd_folder/
├── xxx.ply
├── ds_ny
│   └── frame.ply
└── ds_sf
    └── kitti_0000000001.ply
```

In this case only the one dataset `abcd_folder` will be created with all pointcloud files.


**Example 3. PLY files with photo context:**


```
abcd_folder/
└── dir_01
    └── dir_02
        ├── frame.ply
        ├── kitti_0000000001.ply
        └── related_images
            └── kitti_0000000001_ply
                ├── 0000000000.png
                └── 0000000000.png.json
```

if you want to attach photo context to ply file just create a directory related_images near the file. 
Then create directory <filename_with_ext> (in this example we name directory kitti_0000000001_ply - it's a filename + extension + all symbols . are replaced to _) 
and put there images and corresponding json files with projection matrix. See example for more info.

As a result we will get project `my_images_project` with 3 datasets with the names: `ds0`, `my_folder1`, `my_folder3`. Dataset `my_folder1` will also contain images from `my_folder2` directory.

# How to Run

**Step 1.** Add [Import Pointclouds PLY](https://ecosystem.supervise.ly/apps/supervisely-ecosystem/import-images) app to your team from Ecosystem

<img data-key="sly-module-link" data-module-slug="supervisely-ecosystem/import-images" src="https://i.imgur.com/7dfX1s2.png" width="350px" style='padding-bottom: 10px'/>

**Step 2.** Run the application from the context menu of the directory with images on Team Files page

<img src="https://i.imgur.com/0DF8igu.png" width="80%" style='padding-top: 10px'>  

**Step 3.** Select options and press the Run button

<img src="https://i.imgur.com/G6UjpD2.png" width="80%" style='padding-top: 10px'>  

### Demo
Example of uploading pointclouds:
![](https://i.imgur.com/EkLt9ii.gif)
