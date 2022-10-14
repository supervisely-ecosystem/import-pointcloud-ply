import os
import open3d as o3d
from pathlib import Path
import supervisely as sly

from supervisely.api.module_api import ApiField
from supervisely.app.widgets import SlyTqdm
from supervisely.imaging.image import SUPPORTED_IMG_EXTS
from supervisely.io.fs import get_file_ext, get_file_name, get_file_name_with_ext
from supervisely.io.json import load_json_file

import globals as g
import download_progress


def get_project_name_from_input_path(input_path: str) -> str:
    """Returns project name from target sly folder name."""
    full_path_dir = os.path.dirname(input_path)
    return os.path.basename(full_path_dir)


def convert_ply_to_pcd(name: str, path: str) -> tuple:
    """Convert .ply format to .pcd."""
    points = o3d.io.read_point_cloud(path)
    name = f"{get_file_name(name)}.pcd"
    path = f"{os.path.dirname(path)}/{name}"
    o3d.io.write_point_cloud(path, points, write_ascii=True)

    return name, path


def convert_items_in_dataset(names: list, paths: list) -> tuple:
    """
    Download dataset and convert pointclouds from .pcd to .ply format.
    """
    res_batch_names = []
    res_batch_paths = []
    for name, path in zip(names, paths):
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
    return res_batch_names, res_batch_paths


def download_project(api: sly.Api, input_path: str) -> str:
    """Download target directory with ply files."""
    if g.IS_ON_AGENT:
        agent_id, cur_files_path = api.file.parse_agent_id_and_path(input_path)
    else:
        cur_files_path = input_path

    sizeb = api.file.get_directory_size(g.TEAM_ID, input_path)
    extract_dir = os.path.join(g.STORAGE_DIR, cur_files_path.strip("/"))
    progress_cb = download_progress.get_progress_cb(api, g.TASK_ID, f"Downloading {input_path.strip('/')}", sizeb,
                                                    is_size=True)
    api.file.download_directory(g.TEAM_ID, input_path, extract_dir, progress_cb)
    return extract_dir


def get_related_image_and_meta_paths(
    local_path_to_ply_file: str, ply_file_name: str
) -> tuple:
    """Get related image and image meta paths from dataset directory if they exist."""
    ds_root_dir = os.path.dirname(local_path_to_ply_file)
    if not sly.fs.dir_exists(ds_root_dir):
        return None, None
    rel_images_dir_name = (
        f"{get_file_name(ply_file_name)}{get_file_ext(ply_file_name).replace('.', '_')}"
    )
    rel_images_dir = os.path.join(ds_root_dir, "related_images", rel_images_dir_name)
    rel_image_path = None
    rel_image_meta_path = None
    if not os.path.exists(rel_images_dir):
        return None, None
    files_in_dir = os.listdir(rel_images_dir)
    for file in files_in_dir:
        if file.startswith(f"{get_file_name(ply_file_name)}."):
            file_ext = get_file_ext(file).lower()
            if file_ext in SUPPORTED_IMG_EXTS:
                rel_image_path = os.path.join(rel_images_dir, file)
                rel_image_meta_path = os.path.join(rel_images_dir, f"{file}.json")
                if sly.fs.file_exists(rel_image_path) and sly.fs.file_exists(
                    rel_image_meta_path
                ):
                    break
                else:
                    return None, None
    return rel_image_path, rel_image_meta_path


def get_datasets_items_map(dir_info: list, storage_dir) -> tuple:
    """Creates a dictionary map based on api response from the target sly folder data."""
    datasets_images_map = {}
    for file_info in dir_info:
        remote_file_path = file_info["path"]
        if g.IS_ON_AGENT:
            agent_id, remote_file_path = g.api.file.parse_agent_id_and_path(remote_file_path)
        full_path_file = f"{storage_dir}{remote_file_path}"
        file_ext = get_file_ext(full_path_file)
        if file_ext not in g.ALLOWED_POINTCLOUD_EXTENSIONS:
            if file_ext not in SUPPORTED_IMG_EXTS and file_ext != ".json":
                sly.logger.warn(
                    f"File skipped '{full_path_file}': {file_ext} is not supported. Supported extensions: {g.ALLOWED_POINTCLOUD_EXTENSIONS}"
                )
            continue

        file_name = get_file_name_with_ext(full_path_file)
        file_hash = file_info["hash"]
        file_related_image_path, file_related_image_meta_path = get_related_image_and_meta_paths(
            full_path_file, file_name
        )
        ds_name = get_dataset_name(remote_file_path.lstrip("/"))
        if ds_name not in datasets_images_map.keys():
            datasets_images_map[ds_name] = {
                "ply_names": [],
                "ply_paths": [],
                "ply_hashes": [],
                "ply_related_images": {"images_paths": [], "images_metas_paths": []},
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
        datasets_images_map[ds_name]["ply_related_images"]["images_paths"].append(
            file_related_image_path
        )
        datasets_images_map[ds_name]["ply_related_images"]["images_metas_paths"].append(
            file_related_image_meta_path
        )

    datasets_names = list(datasets_images_map.keys())
    return datasets_names, datasets_images_map


def upload_pointclouds(
    api: sly.Api,
    dataset_id: int,
    dataset_name: str,
    progress_bar: SlyTqdm,
    ply_names: list,
    ply_paths: list,
    ply_hashes: list,
) -> list:
    """Convert ply to pcd and upload to project."""
    pointclouds_infos = None
    batch_size = min(len(ply_names), 10)
    for batch_names, batch_paths, batch_hashes in progress_bar(
        zip(
            sly.batched(seq=ply_names, batch_size=batch_size),
            sly.batched(seq=ply_paths, batch_size=batch_size),
            sly.batched(seq=ply_hashes, batch_size=batch_size),
        ),
        total=len(ply_paths),
        message="Dataset: {!r} pointclouds".format(dataset_name),
    ):
        res_batch_names, res_batch_paths = convert_items_in_dataset(
            names=batch_names, paths=batch_paths
        )
        pointclouds_infos = api.pointcloud.upload_paths(
            dataset_id=dataset_id, names=res_batch_names, paths=res_batch_paths
        )
    return pointclouds_infos


def upload_related_images(
    api: sly.Api,
    dataset_name: str,
    progress_bar: SlyTqdm,
    pointclouds_infos: list,
    ply_rel_images_paths: list,
    ply_rel_images_meta_paths: list,
) -> None:
    """Upload related images to corresponding pointclouds in project."""
    pointclouds_ids = [pointcloud_info.id for pointcloud_info in pointclouds_infos]
    pointclouds_names = [pointcloud_info.name for pointcloud_info in pointclouds_infos]
    for (
        batch_rel_images_paths,
        batch_pointclouds_ids,
        pointclouds_names,
        batch_rel_images_meta_paths,
    ) in progress_bar(
        zip(
            sly.batched(seq=ply_rel_images_paths, batch_size=10),
            sly.batched(seq=pointclouds_ids, batch_size=10),
            sly.batched(seq=pointclouds_names, batch_size=10),
            sly.batched(seq=ply_rel_images_meta_paths, batch_size=10),
        ),
        total=len(ply_rel_images_paths) // 10,
        message="Dataset: {!r} related images".format(dataset_name),
    ):
        images_infos = []
        for rimg_path, pcd_id, pcd_name, meta_path in zip(
            batch_rel_images_paths,
            batch_pointclouds_ids,
            pointclouds_names,
            batch_rel_images_meta_paths,
        ):
            if rimg_path is not None or meta_path is not None:
                img_hash = api.pointcloud.upload_related_image(rimg_path)
                img_meta = load_json_file(meta_path)

                image_info = {
                    ApiField.ENTITY_ID: pcd_id,
                    ApiField.NAME: pcd_name,
                    ApiField.HASH: img_hash[0],
                    ApiField.META: img_meta,
                }
                images_infos.append(image_info)

        api.pointcloud.add_related_images(images_infos)

def get_dataset_name(file_path, default="ds0"):
    dir_path = os.path.split(file_path)[0]
    ds_name = default
    path_parts = Path(dir_path).parts
    if len(path_parts) != 1:
        if g.IS_ON_AGENT:
            return path_parts[-1]
        ds_name = path_parts[1]
    return ds_name
