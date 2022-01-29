#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput

from imports.aws import AwsProvider
from imports.aws.vpc import Vpc, RouteTable, Subnet, InternetGateway, RouteTableAssociation, Route, SecurityGroup, \
    SecurityGroupIngress, NatGateway, SecurityGroupEgress
from imports.aws.ec2 import Instance, Eip


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        # AWS Provider on North Virginia (us-east-1)
        AwsProvider(self, "Aws", region="us-east-1")

        # MyVPC on 10.0.0.0/16
        vpc = Vpc(self, "MyVPC", cidr_block="10.0.0.0/16", tags={'Name': 'MyVPC'})

        # Public Subnet on 10.0.1.0/24
        public_subnet = Subnet(self, 'public_subnet', cidr_block='10.0.1.0/24', vpc_id=vpc.id, tags={'Name': 'public_subnet'})

        # Private Subnet on 10.0.2.0/24
        private_subnet = Subnet(self, 'private_subnet', cidr_block='10.0.2.0/24', vpc_id=vpc.id, tags={'Name': 'private_subnet'})

        # Internet Gateway
        igw = InternetGateway(self, 'igw', vpc_id=vpc.id, tags={'Name': 'igw'})

        public_route_table = RouteTable(self, id='public_route_table', vpc_id=vpc.id, tags={"Name": "public_route_table"})
        public_rta2 = RouteTableAssociation(self, 'public_subnet_rta', subnet_id=public_subnet.id, route_table_id=public_route_table.id)
        public_route = Route(self, 'public_route', route_table_id=public_route_table.id, gateway_id=igw.id,
                             destination_cidr_block='0.0.0.0/0')

        # NAT Gateway - needed for private network internet access
        # We also need an Elastic IP
        eip = Eip(self, "eip", tags={"Name": "eip"})
        nat_gateway = NatGateway(self, 'nat_gateway', subnet_id=public_subnet.id, tags={"Name": "nat_gateway"})
        nat_gateway.allocation_id = eip.allocation_id

        # Private Route Table / nat_gateway association
        private_route_table = RouteTable(self, id='private_route_table', vpc_id=vpc.id, tags={"Name": "private_route_table"})
        RouteTableAssociation(self, 'private_subnet_rta', subnet_id=private_subnet.id, route_table_id=private_route_table.id)
        Route(self, 'private_route', route_table_id=private_route_table.id, nat_gateway_id=nat_gateway.id,
              destination_cidr_block='0.0.0.0/0')

        # Public Security Group
        pub_sec_gr = SecurityGroup(self, "pub_sec_gr", description="Public Security Group", name="pub_sec_gr", vpc_id=vpc.id,
                                   tags={"Name": "pub_sec_gr"})
        # We need to open inbound ports 22 and 80
        pub_sec_gr_ing1 = SecurityGroupIngress(cidr_blocks=["0.0.0.0/0"], description="SSH", from_port=22, to_port=22, protocol="TCP")
        pub_sec_gr_ing2 = SecurityGroupIngress(cidr_blocks=["0.0.0.0/0"], description="HTTP", from_port=80, to_port=80, protocol="TCP")
        # We need to open outbound ports to internet, so that we can yum update/install
        pub_sec_gr_eg1 = SecurityGroupEgress(cidr_blocks=["0.0.0.0/0"], description="All", from_port=0, to_port=0, protocol="-1")
        pub_sec_gr.ingress = [pub_sec_gr_ing1, pub_sec_gr_ing2]
        pub_sec_gr.egress = [pub_sec_gr_eg1]

        # Private Security Group
        priv_sec_gr = SecurityGroup(self, "priv_sec_gr", description="Private Security Group", name="priv_sec_gr", vpc_id=vpc.id,
                                    tags={"Name": "priv_sec_gr"})
        # We need to open inbound ports 22 and 3306
        priv_sec_gr_ing1 = SecurityGroupIngress(cidr_blocks=["10.0.1.0/24"], description="SSH", from_port=22, to_port=22, protocol="TCP")
        priv_sec_gr_ing2 = SecurityGroupIngress(cidr_blocks=["10.0.1.0/24"], description="MySQL", from_port=3306, to_port=3306,
                                                protocol="TCP")
        priv_sec_gr_ing3 = SecurityGroupIngress(cidr_blocks=["10.0.1.0/24"], description="ICMP", from_port=-1, to_port=-1,
                                                protocol="ICMP")
        # We need to open outbound ports to internet, so that we can yum update/install
        priv_sec_gr_eg1 = SecurityGroupEgress(cidr_blocks=["0.0.0.0/0"], description="All", from_port=0, to_port=0, protocol="-1")
        priv_sec_gr.ingress = [priv_sec_gr_ing1, priv_sec_gr_ing2, priv_sec_gr_ing3]
        priv_sec_gr.egress = [priv_sec_gr_eg1]

        # Public Instance on Public Subnet
        # Amazon Linux 2 AMI (HVM) - Kernel 5.10, SSD Volume Type - ami-08e4e35cccc6189f4 (64-bit x86)
        pub_instance = Instance(self, "pub_instance", ami="ami-08e4e35cccc6189f4", instance_type="t2.micro", subnet_id=public_subnet.id,
                                key_name="celeghin.mac13", depends_on=[pub_sec_gr], associate_public_ip_address=True,
                                tags={"Name": "pub_instance"})
        pub_instance.security_groups = [pub_sec_gr.id]
        TerraformOutput(self, "public_ip", value=pub_instance.public_ip)

        # Private Instance on Private Subnet
        # Amazon Linux 2 AMI (HVM) - Kernel 5.10, SSD Volume Type - ami-08e4e35cccc6189f4 (64-bit x86)
        priv_instance = Instance(self, "priv_instance", ami="ami-08e4e35cccc6189f4", instance_type="t2.micro", subnet_id=private_subnet.id,
                                 key_name="celeghin.mac13", associate_public_ip_address=False, tags={"Name": "priv_instance"})
        priv_instance.security_groups = [priv_sec_gr.id]
        TerraformOutput(self, "private_ip", value=priv_instance.private_ip)


app = App()
MyStack(app, "cdktf-aws-python")

app.synth()
