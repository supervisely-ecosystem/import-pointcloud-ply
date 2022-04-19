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
    datasets_names, datasets_images_map = f.get_datasets_images_map(dir_info)

    project = api.project.create(
        workspace_id=g.WORKSPACE_ID,
        name=project_name,
        type=sly.ProjectType.POINT_CLOUDS,
        change_name_if_conflict=True
    )
    for dataset_name in datasets_names:
        dataset_info = api.dataset.create(
            project_id=project.id,
            name=dataset_name,
            change_name_if_conflict=True
        )

        images_names = datasets_images_map[dataset_name]["ply_names"]
        images_paths = datasets_images_map[dataset_name]["ply_paths"]
        images_hashes = datasets_images_map[dataset_name]["ply_hashes"]
        for batch_names, batch_paths, batch_hashes in progress_bar(
                zip(
                    sly.batched(seq=images_names, batch_size=10),
                    sly.batched(seq=images_paths, batch_size=10),
                    sly.batched(seq=images_hashes, batch_size=10),
                ),
                total=len(images_hashes) // 10,
                message="Dataset: {!r}".format(dataset_name),
        ):

            res_batch_names, res_batch_paths, local_save_dir = f.download_and_convert_dataset(
                api=api,
                names=batch_names,
                paths=batch_paths,
                hashes=batch_hashes,
            )
            api.pointcloud.upload_paths(
                dataset_id=dataset_info.id,
                names=res_batch_names,
                paths=res_batch_paths,
            )
            sly.fs.remove_dir(dir_=local_save_dir)

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
