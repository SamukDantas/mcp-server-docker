from typing import Any

from docker.models.containers import Container
from docker.models.images import Image
from docker.models.networks import Network
from docker.models.volumes import Volume


def docker_to_dict(
    obj: Image | Container | Volume | Network, overrides: dict[str, Any] | None = None
) -> dict[str, Any]:
    result = None

    if isinstance(obj, Image):
        img_config: dict[str, Any] = obj.attrs.get("Config") or {}

        result = {
            "id": obj.id,
            "tags": obj.tags,
            "short_id": obj.short_id,
            "labels": img_config.get("Labels", {}),
            "repo_tags": obj.attrs.get("RepoTags"),
            "repo_digests": obj.attrs.get("RepoDigests"),
            "created": obj.attrs.get("Created"),
            "size": obj.attrs.get("Size"),
        }

    if isinstance(obj, Container):
        config: dict[str, Any] = obj.attrs.get("Config") or {}

        # Get image info from container attrs only - avoid accessing obj.image
        # as it tries to resolve the image and can fail for incomplete SHA256 IDs
        image_data = obj.attrs.get("Image", "")
        if image_data:
            image_info = {
                "id": image_data,
                "tags": [],
                "short_id": image_data[:12] if len(image_data) >= 12 else image_data,
            }
        else:
            image_info = None

        # Get status from State attribute for accurate status
        state = obj.attrs.get("State", {})
        status = state.get("Status", obj.status)

        result = {
            "id": obj.id,
            "name": obj.name,
            "short_id": obj.short_id,
            "image": image_info,
            "status": status,
            "labels": config.get("Labels", {}),
            "ports": obj.ports,
            "created": obj.attrs.get("Created"),
            "state": obj.attrs.get("State"),
            "restart_count": obj.attrs.get("RestartCount"),
            "networks": list(
                obj.attrs.get("NetworkSettings", {}).get("Networks", {}).keys()
            ),
            "mounts": obj.attrs.get("Mounts"),
            "config": {
                "hostname": config.get("Hostname"),
                "user": config.get("User"),
                "image": config.get("Image"),
            },
        }

    if isinstance(obj, Network):
        result = {
            "id": obj.id,
            "name": obj.name,
            "short_id": obj.short_id,
            "driver": obj.attrs.get("Driver"),
            "scope": obj.attrs.get("Scope"),
            "created": obj.attrs.get("CreatedAt"),
            "labels": obj.attrs.get("Labels"),
        }

    if isinstance(obj, Volume):
        result = {
            "id": obj.id,
            "name": obj.name,
            "short_id": obj.short_id,
            "labels": obj.attrs.get("Labels", {}),
            "mountpoint": obj.attrs.get("Mountpoint"),
            "created": obj.attrs.get("CreatedAt"),
            "driver": obj.attrs.get("Driver"),
            "scope": obj.attrs.get("Scope"),
        }

    if result is None:
        raise ValueError(f"Unsupported object type: {type(obj)}")

    return result if overrides is None else {**result, **overrides}
