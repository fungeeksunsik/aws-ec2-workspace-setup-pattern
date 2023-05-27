from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ElasticFileSystemConfig:
    region: str
    efs_name: str
    efs_id: Optional[str] = None

    @classmethod
    def from_config(cls, config: Dict[str, str]):
        return cls(**config)


@dataclass
class MountTargetConfig:
    region: str
    subnet_id: str
    sg_id: str
    efs_name: str
    efs_id: str
    mt_id: Optional[str] = None

    @classmethod
    def from_config(cls, config: Dict[str, str]):
        return cls(**config)

    @property
    def mt_dns(self):
        return f"{self.efs_id}.{self.region}.amazonaws.com"
