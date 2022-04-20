import supervisely as sly
from supervisely.app.widgets import SlyTqdm

import functions as f
import globals as g

progress_bar = SlyTqdm()


@sly.timeit
def import_pointcloud_ply(api: sly.Api, task_id: int):
    dir_info = api.file.list(g.TEAM_ID, g.INPUT_PATH)
    if len(dir_info) == 0:
        raise Exception(f"There are no files in selected directory: '{g.INPUT_PATH}'")

    project_name = f.get_project_name_from_input_path(g.INPUT_PATH)
    f.download_project(api, g.INPUT_PATH)

    datasets_names, datasets_images_map = f.get_datasets_items_map(
        dir_info, g.STORAGE_DIR
    )
    project = api.project.create(
        workspace_id=g.WORKSPACE_ID,
        name=project_name,
        type=sly.ProjectType.POINT_CLOUDS,
        change_name_if_conflict=True,
    )
    for dataset_name in datasets_names:
        dataset_info = api.dataset.create(
            project_id=project.id, name=dataset_name, change_name_if_conflict=True
        )

        ply_names = datasets_images_map[dataset_name]["ply_names"]
        ply_paths = datasets_images_map[dataset_name]["ply_paths"]
        ply_hashes = datasets_images_map[dataset_name]["ply_hashes"]
        ply_rel_images_paths = datasets_images_map[dataset_name]["ply_related_images"][
            "images_paths"
        ]
        ply_rel_images_meta_paths = datasets_images_map[dataset_name][
            "ply_related_images"
        ]["images_metas_paths"]

        try:
            pointclouds_infos = f.upload_pointclouds(
                api=api,
                dataset_id=dataset_info.id,
                dataset_name=dataset_info.name,
                progress_bar=progress_bar,
                ply_names=ply_names,
                ply_paths=ply_paths,
                ply_hashes=ply_hashes,
            )

            if ply_rel_images_paths.count(None) != len(ply_rel_images_paths):
                f.upload_related_images(
                    api=api,
                    dataset_name=dataset_info.name,
                    progress_bar=progress_bar,
                    pointclouds_infos=pointclouds_infos,
                    ply_rel_images_paths=ply_rel_images_paths,
                    ply_rel_images_meta_paths=ply_rel_images_meta_paths,
                )
        except:
            sly.logger.error(msg=f"Couldn't upload files from '{dataset_name}' dataset. Please check directory's file "
                                 f"structure, for subdirectories and duplicated file names")
            continue

    sly.fs.remove_dir(dir_=g.STORAGE_DIR)
    if g.REMOVE_SOURCE:
        api.file.remove(team_id=g.TEAM_ID, path=g.INPUT_PATH)
        source_dir_name = g.INPUT_PATH.lstrip("/").rstrip("/")
        sly.logger.info(
            msg=f"Source directory: '{source_dir_name}' was successfully removed."
        )

    api.task.set_output_project(
        task_id=task_id, project_id=project.id, project_name=project.name
    )


if __name__ == "__main__":
    sly.logger.info(
        "Script arguments",
        extra={
            "context.teamId": g.TEAM_ID,
            "context.workspaceId": g.WORKSPACE_ID,
            "modal.state.slyFolder": g.INPUT_PATH,
        },
    )

    import_pointcloud_ply(g.api, g.TASK_ID)
    try:
        sly.app.fastapi.shutdown()
    except KeyboardInterrupt:
        sly.logger.info("Application shutdown successfully")
