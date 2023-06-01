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
        (22, 22),  # SSH
        (80, 80),  # HTTP
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

    @classmethod
    def from_config(cls, vpc_config: Dict[str, Union[str, List[List[int]]]]):
        return cls(**vpc_config)


class SubnetConfig(VpcConfig):

    def __init__(
            self,
            vpc_config: VpcConfig,
            subnet_name: str,
            rt_name: str,
            az_postfix: Optional[str] = None,
            availability_zone: Optional[str] = None,
            cidr_substitute: Optional[str] = None,
            subnet_cidr: Optional[str] = None,
            subnet_id: Optional[str] = None,
            rt_id: Optional[str] = None,
            subnet_rt_association_id: Optional[str] = None,
    ):
        super(SubnetConfig, self).__init__(**vpc_config.__dict__)
        self.subnet_name = subnet_name
        self.rt_name = rt_name
        self.subnet_cidr = self._parse_subnet_cidr(cidr_substitute, subnet_cidr)
        self.availability_zone = self._parse_availability_zone(az_postfix, availability_zone)
        self.subnet_id = subnet_id
        self.rt_id = rt_id
        self.subnet_rt_association_id = subnet_rt_association_id

    def _parse_subnet_cidr(
            self,
            cidr_substitute: Optional[str] = None,
            subnet_cidr: Optional[str] = None,
    ) -> str:
        if subnet_cidr:
            return subnet_cidr
        elif cidr_substitute:
            cidr_chunks = self.vpc_cidr.split(".")
            cidr_chunks[2] = cidr_substitute
            cidr_chunks[3] = f"0/24"
            return ".".join(cidr_chunks)
        else:
            raise ValueError("One of subnet_cidr and cidr_substitute must be specified")

    def _parse_availability_zone(
            self,
            az_postfix: Optional[str] = None,
            availability_zone: Optional[str] = None,
    ):
        if availability_zone:
            return availability_zone
        elif az_postfix in "abcd":
            return f"{self.region}{az_postfix}"
        else:
            raise ValueError("One of az_postfix and availability_zone must be specified")

    @classmethod
    def from_config(
            cls, subnet_config: Dict[str, Union[str, List[List[int]]]]
    ):
        vpc_config = VpcConfig(
            region=subnet_config["region"],
            vpc_cidr=subnet_config["vpc_cidr"],
            vpc_name=subnet_config["vpc_name"],
            sg_name=subnet_config["sg_name"],
            igw_name=subnet_config["igw_name"],
            vpc_id=subnet_config["vpc_id"],
            sg_id=subnet_config["sg_id"],
            igw_id=subnet_config["igw_id"],
        )
        return cls(
            vpc_config=vpc_config,
            subnet_name=subnet_config["subnet_name"],
            rt_name=subnet_config["rt_name"],
            availability_zone=subnet_config["availability_zone"],
            subnet_cidr=subnet_config["subnet_cidr"],
            subnet_id=subnet_config["subnet_id"],
            rt_id=subnet_config["rt_id"],
            subnet_rt_association_id=subnet_config["subnet_rt_association_id"],
        )
