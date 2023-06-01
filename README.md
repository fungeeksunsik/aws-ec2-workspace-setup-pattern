# aws-vpc-hello-world-setup

This repository contains commands for creating basic network structure which contains private, public subnet within single VPC. Before executing commands in execute section, IAM user with Administrator authority(ex. admin.kim) has to be prepared after following instructions explained in [this page](https://docs.aws.amazon.com/IAM/latest/UserGuide/getting-set-up.html#create-an-admin). Then, corresponding access key and password has to be configured into local configuration file using `aws configure` command. 
   
## Environment

Execution environment setup

```shell
python3 --version  # Python 3.10.10
python3 -m venv venv
source venv/bin/activate
pip3 install typer==0.9.0 boto3==1.26.140
export PYTHONPATH=$PWD/src
```

## Execute

If administrator user profile is configured, use name of the profile as parameter of `--profile-name` argument. For example, every command below uses configured credential that corresponds to `admin.kim`.    

### 1. create VPC

1. create a VPC
2. create configured security group and attach it to created VPC
3. create internet gateway and attach it to created VPC

```shell
python main.py configure-vpc \
    --profile-name=admin.kim \
    --region=ap-northeast-2 \
    --vpc-name=prod \
    --vpc-cidr=172.20.0.0/16 \
    --sg-name=prod-sg \
    --igw-name=prod-igw
```

### 2. create subnet

To create public subnet within VPC, use `--is-public` option.

1. create a subnet
2. create route table and add route to internet gateway
3. associate created subnet with created route table 

```shell
python main.py configure-subnet \
    --profile-name=admin.kim \
    --vpc-name=prod \
    --subnet-name=pub-a \
    --cidr-substitute=100 \
    --availability-zone-postfix=a \
    --route-table-name=rt-pub-a \
    --is-public
```

To create private subnet within VPC, use `--no-is-public` option.

1. create a subnet
2. create a route table
3. associate created subnet with created route table

```shell
python main.py configure-subnet \
    --profile-name=admin.kim \
    --vpc-name=prod \
    --subnet-name=prv-c \
    --cidr-substitute=101 \
    --availability-zone-postfix=c \
    --route-table-name=rt-prv-c \
    --no-is-public
```

### 3. delete subnet

Delete objects in reverse order of their creation.

1. delete association between subnet and route table
2. delete the route table
3. delete the subnet 

```shell
python main.py remove-subnet \
    --profile-name=admin.kim \
    --subnet-name=pub-a
```

### 4. delete VPC

Delete objects in reverse order of their creation.

1. detach internet gateway from VPC and delete it
2. delete security group
2. delete VPC

```shell
python main.py remove-vpc \
    --profile-name=admin.kim \
    --vpc-name=prod
```
