# Copyright (c) 2010 Advanced Micro Devices, Inc.
#               2016 Georgia Institute of Technology
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Brad Beckmann
#          Tushar Krishna

from __future__ import print_function
from __future__ import absolute_import

from m5.params import *
from m5.objects import *

from common import FileSystemConfig

from .BaseTopology import SimpleTopology

# Creates a generic 3D Mesh assuming an equal number of cache
# and directory controllers.
# XYZ routing is enforced (using link weights)
# to guarantee deadlock freedom.

class Mesh_XYZ(SimpleTopology):
    description='Mesh_XYZ'

    def __init__(self, controllers):
        self.nodes = controllers

    # Makes a generic 3D mesh
    # assuming an equal number of cache and directory cntrls

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        print("File: Mesh_XYZ.py")
        nodes = self.nodes

        num_routers = options.num_cpus
        x_depth = options.mesh_cols

        # default values for link latency and router latency.
        # Can be over-ridden on a per link/router basis
        link_latency = options.link_latency # used by simple and garnet
        router_latency = options.router_latency # only used by garnet


        # There must be an evenly divisible number of cntrls to routers
        # Also, obviously the number or rows must be <= the number of routers
        cntrls_per_router, remainder = divmod(len(nodes), num_routers)
        assert(x_depth > 0 and x_depth <= num_routers)

        if (options.z_depth>0):
            z_depth=options.z_depth
        else:
            z_depth = int(num_routers/x_depth/x_depth)

        if (options.mesh_rows>0):
            y_depth=options.mesh_rows
        else:
            y_depth = int(num_routers / x_depth /z_depth)

        assert(z_depth * y_depth * x_depth == num_routers)
        print("Total Number Routers: ", num_routers)
        print("x_depth: ", x_depth)
        print("y_depth: ", y_depth)
        print("z_depth: ", z_depth)

        # Create the routers in the mesh
        routers = [Router(router_id=i, latency = router_latency) \
            for i in range(num_routers)]
        network.routers = routers

        # link counter to set unique link ids
        link_count = 0

        # Add all but the remainder nodes to the list of nodes to be uniformly
        # distributed across the network.
        network_nodes = []
        remainder_nodes = []
        for node_index in range(len(nodes)):
            if node_index < (len(nodes) - remainder):
                network_nodes.append(nodes[node_index])
            else:
                remainder_nodes.append(nodes[node_index])

        # Connect each node to the appropriate router
        ext_links = []
        for (i, n) in enumerate(network_nodes):
            cntrl_level, router_id = divmod(i, num_routers)
            assert(cntrl_level < cntrls_per_router)
            ext_links.append(ExtLink(link_id=link_count, ext_node=n,
                                    int_node=routers[router_id],
                                    latency = link_latency))
            link_count += 1

        # Connect the remaining nodes to router 0.  These should only be
        # DMA nodes.
        for (i, node) in enumerate(remainder_nodes):
            assert(node.type == 'DMA_Controller')
            assert(i < remainder)
            ext_links.append(ExtLink(link_id=link_count, ext_node=node,
                                    int_node=routers[0],
                                    latency = link_latency))
            link_count += 1

        network.ext_links = ext_links

        # Create the mesh links.
        int_links = []
        total=link_count
        # East output to West input links (weight = 1)
        for z in range(z_depth):
            for x in range(x_depth):
                for y in range(y_depth):
                    if (y + 1 < y_depth):
                        east_out = y + (x * y_depth) + (z * y_depth * x_depth)
                        west_in=(y+1)+(x*y_depth)+(z*y_depth*x_depth)
                        int_links.append(IntLink(link_id=link_count,
                                                src_node=routers[east_out],
                                                dst_node=routers[west_in],
                                                src_outport="East",
                                                dst_inport="West",
                                                latency = link_latency,
                                                weight=1))
                        link_count += 1
        print("\nNUM EAST-WEST LINKS = ", link_count-total)
        total=link_count
        # West output to East input links (weight = 1)
        for z in range(z_depth):
            for x in range(x_depth):
                for y in range(y_depth):
                    if (y + 1 < y_depth):
                        east_in = y + (x * y_depth) + (z * y_depth * x_depth)
                        west_out = (y + 1) + (x * y_depth) + (z * y_depth * x_depth)
                        int_links.append(IntLink(link_id=link_count,
                                                src_node=routers[west_out],
                                                dst_node=routers[east_in],
                                                src_outport="West",
                                                dst_inport="East",
                                                latency = link_latency,
                                                weight=1))
                        link_count += 1
        print("NUM WEST-EAST LINKS = ", link_count-total)
        total=link_count
        # North output to South input links (weight = 2)
        for z in range(z_depth):
            for x in range(x_depth):
                for y in range(y_depth):
                    if (x + 1 < x_depth):
                        north_out = y + (x * y_depth) + (z * y_depth * x_depth)
                        south_in = y + ((x + 1) * y_depth) + (z * y_depth * x_depth)
                        int_links.append(IntLink(link_id=link_count,
                                                src_node=routers[north_out],
                                                dst_node=routers[south_in],
                                                src_outport="North",
                                                dst_inport="South",
                                                latency = link_latency,
                                                weight=2))
                        link_count += 1
        print("NUM NORTH-SOUTH LINKS = ", link_count-total)
        total=link_count
        # South output to North input links (weight = 2)
        for z in range(z_depth):
            for x in range(x_depth):
                for y in range(y_depth):
                    if (x + 1 < x_depth):
                        north_in = y + (x * y_depth) + (z * y_depth * x_depth)
                        south_out = y + ((x + 1) * y_depth) + (z * y_depth * x_depth)
                        int_links.append(IntLink(link_id=link_count,
                                                src_node=routers[south_out],
                                                dst_node=routers[north_in],
                                                src_outport="South",
                                                dst_inport="North",
                                                latency = link_latency,
                                                weight=2))
                        link_count += 1
        print("NUM SOUTH-NORTH LINKS = ", link_count-total)
        total=link_count
        # Up output to Down input links (weight = 3)
        for z in range(z_depth):
            for y in range(y_depth):
                for x in range(x_depth):
                    if (z + 1 < z_depth):
                        up_out = x + (y * x_depth) + (z * y_depth * x_depth)
                        down_in = x + (y * x_depth) + ((z + 1) * y_depth * x_depth)
                        int_links.append(IntLink(link_id=link_count,
                                                src_node=routers[up_out],
                                                dst_node=routers[down_in],
                                                src_outport="Up",
                                                dst_inport="Down",
                                                latency = link_latency,
                                                weight=3))
                        link_count += 1
        print("NUM UP-DOWN LINKS = ", link_count-total)
        total=link_count
        # Down output to Up input links (weight = 3)
        for z in range(z_depth):
            for y in range(y_depth):
                for x in range(x_depth):
                    if (z + 1 < z_depth):
                        up_in = x + (y * x_depth) + (z * y_depth * x_depth)
                        down_out = x + (y * x_depth) + ((z + 1) * y_depth * x_depth)
                        int_links.append(IntLink(link_id=link_count,
                                                src_node=routers[down_out],
                                                dst_node=routers[up_in],
                                                src_outport="Down",
                                                dst_inport="Up",
                                                latency = link_latency,
                                                weight=3))
                        link_count += 1
        print("NUM DOWN-UP LINKS = ", link_count-total)
        total=link_count
        print("TOTAL NUM LINKS = ", len(int_links), "\n")
        network.int_links = int_links

    # Register nodes with filesystem
    def registerTopology(self, options):
        for i in range(options.num_cpus):
            FileSystemConfig.register_node([i],
                    MemorySize(options.mem_size) // options.num_cpus, i)
