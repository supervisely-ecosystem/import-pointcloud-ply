import os
import pathlib

import open3d as o3d

import supervisely as sly
from supervisely.io.fs import get_file_ext, get_file_name, get_file_name_with_ext
from supervisely.video.import_utils import get_dataset_name

import globals as g


def get_project_name_from_input_path(input_path: str) -> str:
    """Returns project name from target sly folder name."""
    full_path_dir = os.path.dirname(input_path)
    return os.path.basename(full_path_dir)


def convert_ply_to_pcd(name, path: str) -> tuple:
    """Convert .ply format to .pcd."""
    points = o3d.io.read_point_cloud(path)
    name = f"{get_file_name(name)}.pcd"
    path = f"{os.path.dirname(path)}/{name}"
    o3d.io.write_point_cloud(path, points, write_ascii=True)

    return name, path


def download_and_convert_dataset(
    api: sly.Api, names: list, paths: list, hashes: list
) -> tuple:
    """
    Download dataset and convert pointclouds from .pcd to .ply format.
    """
    res_batch_names = []
    res_batch_paths = []
    app_batch_paths = [f"{g.STORAGE_DIR}{batch_path}" for batch_path in paths]
    remote_ds_dir = f"{os.path.dirname(paths[0])}/"
    local_save_dir = f"{g.STORAGE_DIR}{remote_ds_dir}/"

    api.file.download_directory(
        g.TEAM_ID, remote_path=remote_ds_dir, local_save_path=local_save_dir
    )

    for name, path in zip(names, app_batch_paths):
        try:
            file_ext = get_file_ext(path).lower()
            if file_ext == ".ply":
                name, path = convert_ply_to_pcd(name, path)
                res_batch_names.append(name)
                res_batch_paths.append(path)
        except Exception as e:
            sly.logger.warning(
                "Skip image {!r}: {}".format(name, str(e)), extra={"file_path": path}
            )
    return res_batch_names, res_batch_paths, local_save_dir


def get_datasets_images_map(dir_info: list) -> tuple:
    """Creates a dictionary map based on api response from the target sly folder data."""
    datasets_images_map = {}
    for file_info in dir_info:
        full_path_file = file_info["path"]
        file_ext = get_file_ext(full_path_file)
        if file_ext not in g.ALLOWED_POINTCLOUD_EXTENSIONS:
            sly.logger.warn(f"File skipped '{full_path_file}': {file_ext} is not supported. Supported extenstions: {g.ALLOWED_POINTCLOUD_EXTENSIONS}")
            continue

        file_name = get_file_name_with_ext(full_path_file)
        file_hash = file_info["hash"]
        ds_name = get_dataset_name(full_path_file.lstrip("/"))
        if ds_name not in datasets_images_map.keys():
            datasets_images_map[ds_name] = {
                "ply_names": [],
                "ply_paths": [],
                "ply_hashes": [],
            }

        if file_name in datasets_images_map[ds_name]["ply_names"]:
            temp_name = sly.fs.get_file_name(full_path_file)
            temp_ext = sly.fs.get_file_ext(full_path_file)
            new_file_name = f"{temp_name}_{sly.rand_str(5)}{temp_ext}"
            sly.logger.warning(
                "Name {!r} already exists in dataset {!r}: renamed to {!r}".format(
                    file_name, ds_name, new_file_name
                )
            )
            file_name = new_file_name

        datasets_images_map[ds_name]["ply_names"].append(file_name)
        datasets_images_map[ds_name]["ply_paths"].append(full_path_file)
        datasets_images_map[ds_name]["ply_hashes"].append(file_hash)

    datasets_names = list(datasets_images_map.keys())
    return datasets_names, datasets_images_map
