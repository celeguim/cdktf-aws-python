#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput

from imports.aws import AwsProvider
from imports.aws.vpc import Vpc, RouteTable, Subnet, InternetGateway, RouteTableAssociation, RouteTableRoute, Route


class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        AwsProvider(self, "Aws", region="us-east-1")
        vpc = Vpc(self, "MyVPC", cidr_block="10.0.0.0/16", tags={'Name': 'private_vpc'})
        TerraformOutput(self, "main_route_table_id", value=vpc.main_route_table_id)

        # subnets
        public_subnet = Subnet(self, 'public_subnet', cidr_block='10.0.1.0/24', vpc_id=vpc.id, tags={'Name': 'public_subnet'})
        private_subnet = Subnet(self, 'private_subnet', cidr_block='10.0.2.0/24', vpc_id=vpc.id, tags={'Name': 'private_subnet'})

        # internet gateway
        igw = InternetGateway(self, 'igw', vpc_id=vpc.id, tags={'Name': 'igw'})

        public_route_table = RouteTable(self, id='public_route_table', vpc_id=vpc.id, tags={"Name": "public_route_table"})
        # public_rta1 = RouteTableAssociation(self, 'igw_rta', route_table_id=public_route_table.id, gateway_id=igw.id)
        public_rta2 = RouteTableAssociation(self, 'public_subnet_rta', subnet_id=public_subnet.id, route_table_id=public_route_table.id)
        # public_rtr = RouteTableRoute(cidr_block='10.0.1.0/24', gateway_id=igw.id)
        # public_route = Route(self, 'public_route', destination_cidr_block='10.0.1.0/24')
        public_route = Route(self, 'public_route', route_table_id=public_route_table.id, gateway_id=igw.id,
                             destination_cidr_block='0.0.0.0/0')
        # public_route_table.route = [public_route]


app = App()
MyStack(app, "cdktf-aws-python")

app.synth()
