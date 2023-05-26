from configs import VpcConfig, SubnetConfig


def create_vpc(ec2_client, vpc_config: VpcConfig) -> str:
    response = ec2_client.create_vpc(
        CidrBlock=vpc_config.vpc_cidr,
        TagSpecifications=[
            {
                "ResourceType": "vpc",
                "Tags": [{"Key": "Name", "Value": vpc_config.vpc_name}]
            }
        ]
    )
    return response["Vpc"]["VpcId"]


def delete_vpc(ec2_client, vpc_config: VpcConfig):
    ec2_client.delete_vpc(VpcId=vpc_config.vpc_id)


def create_vpc_security_group(ec2_client, vpc_config: VpcConfig) -> str:
    response = ec2_client.create_security_group(
        GroupName=vpc_config.sg_name,
        Description="traffic rules over EC2 workspace",
        VpcId=vpc_config.vpc_id,
    )
    sg_id = response["GroupId"]
    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=vpc_config.parse_ip_permissions()
    )
    return sg_id


def delete_security_group(ec2_client, vpc_config: VpcConfig):
    ec2_client.delete_security_group(GroupId=vpc_config.sg_id)


def create_internet_gateway(ec2_client, vpc_config: VpcConfig) -> str:
    response = ec2_client.create_internet_gateway(
        TagSpecifications=[
            {
                "ResourceType": "internet-gateway",
                "Tags": [{"Key": "Name", "Value": vpc_config.igw_name}]
            }
        ]
    )
    igw_id = response["InternetGateway"]["InternetGatewayId"]
    ec2_client.attach_internet_gateway(
        InternetGatewayId=igw_id, VpcId=vpc_config.vpc_id
    )
    return igw_id


def delete_internet_gateway(ec2_client, vpc_config: VpcConfig):
    ec2_client.detach_internet_gateway(
        InternetGatewayId=vpc_config.igw_id,
        VpcId=vpc_config.vpc_id
    )
    ec2_client.delete_internet_gateway(
        InternetGatewayId=vpc_config.igw_id
    )


def create_subnet(ec2_client, subnet_config: SubnetConfig) -> str:
    response = ec2_client.create_subnet(
        CidrBlock=subnet_config.subnet_cidr,
        VpcId=subnet_config.vpc_id,
        AvailabilityZone=subnet_config.availability_zone,
        TagSpecifications=[
            {
                "ResourceType": "subnet",
                "Tags": [{"Key": "Name", "Value": subnet_config.subnet_name}]
            }
        ]
    )
    return response["Subnet"]["SubnetId"]


def delete_subnet(ec2_client, subnet_config: SubnetConfig):
    ec2_client.delete_subnet(SubnetId=subnet_config.subnet_id)


def create_route_table(ec2_client, subnet_config: SubnetConfig, is_public: bool) -> str:
    response = ec2_client.create_route_table(
        VpcId=subnet_config.vpc_id,
        TagSpecifications=[
            {
                "ResourceType": "route-table",
                "Tags": [{"Key": "Name", "Value": subnet_config.rt_name}]
            }
        ]
    )
    route_table_id = response["RouteTable"]["RouteTableId"]
    if is_public:
        ec2_client.create_route(
            DestinationCidrBlock="0.0.0.0/0",
            GatewayId=subnet_config.igw_id,
            RouteTableId=route_table_id,
        )
    return route_table_id


def delete_route_table(ec2_client, subnet_config: SubnetConfig):
    ec2_client.delete_route_table(RouteTableId=subnet_config.rt_id)


def create_subnet_route_table_association(ec2_client, subnet_config: SubnetConfig) -> str:
    response = ec2_client.associate_route_table(
        RouteTableId=subnet_config.rt_id,
        SubnetId=subnet_config.subnet_id
    )
    return response["AssociationId"]


def delete_subnet_route_table_association(ec2_client, subnet_config: SubnetConfig):
    ec2_client.disassociate_route_table(
        AssociationId=subnet_config.subnet_rt_association_id
    )
