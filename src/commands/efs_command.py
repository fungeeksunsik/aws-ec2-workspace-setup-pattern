import time
from configs import ElasticFileSystemConfig, MountTargetConfig, SubnetConfig


def create_file_system(efs_client, efs_config: ElasticFileSystemConfig) -> str:
    response = efs_client.create_file_system(
        PerformanceMode="generalPurpose",          # other option: 'maxIO'
        Encrypted=True,
        # KmsKeyId="kms_key_id",                   # optionally required if using custom KMS
        ThroughputMode="elastic",
        # ProvisionedThroughputInMbps=128.0,       # required if ThroughputMode="provisioned"
        # AvailabilityZoneName="ap-northeast-2a",  # required if using this EFS in single AZ
        Backup=False,
        Tags=[{"Key": "Name", "Value": efs_config.efs_name}],
    )
    efs_id = response["FileSystemId"]
    available = False
    while not available:
        time.sleep(1)
        response = efs_client.describe_file_systems(FileSystemId=efs_id)
        current_state = response["FileSystems"][0]
        available = current_state["LifeCycleState"] == "available"
    return efs_id


def delete_file_system(efs_client, efs_config: ElasticFileSystemConfig):
    efs_client.delete_file_system(FileSystemId=efs_config.efs_id)


def create_mount_target(efs_client, subnet_config: SubnetConfig, efs_config: ElasticFileSystemConfig) -> str:
    response = efs_client.create_mount_target(
        FileSystemId=efs_config.efs_id,
        SubnetId=subnet_config.subnet_id,
        SecurityGroups=[subnet_config.sg_id],
    )
    mt_id = response["MountTargetId"]
    available = False
    while not available:
        time.sleep(1)
        response = efs_client.describe_mount_targets(MountTargetId=mt_id)
        current_state = response["MountTargets"][0]
        available = current_state["LifeCycleState"] == "available"
    return mt_id


def delete_mount_target(efs_client, mt_config: MountTargetConfig):
    efs_client.delete_mount_target(MountTargetId=mt_config.mt_id)
