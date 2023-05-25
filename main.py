import sys
import logging
import pathlib
import json
import boto3
import typer

from typer import Typer
from configs import *
from commands import vpc_command

app = Typer()
local_dir = pathlib.Path("./params").resolve()
local_dir.mkdir(exist_ok=True, parents=True)
formatter = logging.Formatter(
    fmt="%(asctime)s (%(funcName)s) : %(msg)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


@app.command(
    name="configure-vpc",
    help="executes series of operations to create VPC within configured region"
)
def configure_vpc(
    profile_name: str = typer.Option(..., help="name of AWS administrator profile"),
    region: str = typer.Option(..., help="name of AWS region to create VPC"),
    vpc_cidr: str = typer.Option(..., help="range of IP host addresses to define within VPC"),
    vpc_name: str = typer.Option(..., help="name of VPC"),
    sg_name: str = typer.Option(..., help="name of security group to attach to VPC"),
    igw_name: str = typer.Option(..., help="name of internet gateway to associate with VPC"),
    vpc_config_name: str = typer.Option("vpc_config.json", help="file name of generated VPC configuration"),
):
    vpc_config = VpcConfig(
        region=region,
        vpc_cidr=vpc_cidr,
        vpc_name=vpc_name,
        sg_name=sg_name,
        igw_name=igw_name,
    )
    session = boto3.Session(
        profile_name=profile_name, 
        region_name=vpc_config.region
    )
    ec2_client = session.client("ec2")

    logger.info("Create VPC")
    vpc_id = vpc_command.create_vpc(ec2_client, vpc_config)
    vpc_config.vpc_id = vpc_id

    logger.info("Create security group and open configured ports")
    sg_id = vpc_command.create_vpc_security_group(ec2_client, vpc_config)
    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=vpc_config.parse_ip_permissions()
    )
    vpc_config.sg_id = sg_id

    logger.info("Create internet gateway and attach it to VPC")
    igw_id = vpc_command.create_internet_gateway(ec2_client, vpc_config)
    ec2_client.attach_internet_gateway(
        InternetGatewayId=igw_id, VpcId=vpc_id
    )
    vpc_config.igw_id = igw_id

    vpc_config_path = local_dir.joinpath(vpc_config_name)
    logger.info(f"Save VPC configuration file as {vpc_config_path}")
    with open(vpc_config_path, "w") as file:
        json.dump(vpc_config.__dict__, file)


@app.command(
    name="configure-subnet",
    help="executes series of operations to create subnet within predefined VPC"
)
def configure_subnet(
    profile_name: str = typer.Option(..., help="name of AWS administrator profile"),
    subnet_name: str = typer.Option(..., help="name of subnet to create within VPC"),
    cidr_substitute: str = typer.Option(..., help="value to use as third octet(integer between 1-254)"),
    availability_zone_postfix: str = typer.Option(..., help="postfix to attach to region name"),
    route_table_name: str = typer.Option(..., help="name of route table to associate with subnet"),
    is_public: bool = typer.Option(..., help="whether created subnet is routed to internet gateway"),
    vpc_config_name: str = typer.Option("vpc_config.json", help="file name of generated VPC configuration"),
):
    with open(local_dir.joinpath(vpc_config_name), "r") as file:
        vpc_config = json.load(file)
        vpc_config = VpcConfig(**vpc_config)
    session = boto3.Session(
        profile_name=profile_name, 
        region_name=vpc_config.region
    )
    ec2_client = session.client("ec2")
    subnet_config = SubnetConfig(
        vpc_config=vpc_config,
        subnet_name=subnet_name,
        cidr_substitute=cidr_substitute,
        az_postfix=availability_zone_postfix,
        rt_name=route_table_name,
    )

    logger.info("Create subnet")
    subnet_id = vpc_command.create_subnet(ec2_client, subnet_config)
    subnet_config.subnet_id = subnet_id

    logger.info("Create subnet route table")
    rt_id = vpc_command.create_subnet_route_table(ec2_client, subnet_config, is_public)
    subnet_config.rt_id = rt_id

    subnet_config_file_name = f"subnet_{subnet_name.replace('-', '_')}_config.json"
    subnet_config_path = local_dir.joinpath(subnet_config_file_name)
    logger.info(f"Save VPC configuration file as {subnet_config_path}")
    with open(subnet_config_path, "w") as file:
        json.dump(subnet_config.__dict__, file)


if __name__ == "__main__":
    app()
