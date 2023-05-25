from dataclasses import dataclass
from typing import List, Dict, Tuple, Union, Optional


@dataclass
class VpcConfig:
    region: str
    vpc_cidr: str
    vpc_name: str
    sg_name: str
    igw_name: str
    vpc_id: Optional[str] = None
    sg_id: Optional[str] = None
    igw_id: Optional[str] = None
    ingress_port_ranges: Tuple[Tuple[int, int]] = (
        (22, 22),      # SSH
        (80, 80),      # HTTP
        (5000, 5002),  # Docker
        (8888, 8890),  # Jupyter
    )

    def parse_ip_permissions(self) -> List[Dict[str, Union[str, int]]]:
        ip_permissions = []
        for port_range in self.ingress_port_ranges:
            from_port, to_port = port_range
            parsed_permission = {
                "FromPort": from_port,
                "ToPort": to_port,
                "IpProtocol": "tcp",
                "IpRanges": [
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "better to allow connection by predefined VPN, but skip for simplicity"
                    }
                ]
            }
            ip_permissions.append(parsed_permission)
        return ip_permissions


class SubnetConfig(VpcConfig):

    def __init__(
        self,
        vpc_config: VpcConfig,
        az_postfix: str,
        cidr_substitute: str,
        subnet_name: str,
        rt_name: str,
    ):
        super(SubnetConfig, self).__init__(**vpc_config.__dict__)
        if az_postfix not in "abcd":
            raise ValueError("availability zone prefix must be one of ('a', 'b', 'c', 'd').")
        self.availability_zone = f"{vpc_config.region}{az_postfix}"
        self.subnet_name = subnet_name
        self.subnet_id = None
        self.rt_name = rt_name
        self.rt_id = None
        cidr_chunks = self.vpc_cidr.split(".")
        cidr_chunks[2] = cidr_substitute
        cidr_chunks[3] = f"0/24"
        self.subnet_cidr = ".".join(cidr_chunks)
