/* Src: \(4,7,4\) \| Current: \(.,.,.\) \| Dest: \(1,0,7\)
 * Copyright (c) 2008 Princeton University
 * Copyright (c) 2016 Georgia Institute of Technology
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * Authors: Niket Agarwal
 *          Tushar Krishna
 */


#include "base/cast.hh"
#include "base/logging.hh"
#include "mem/ruby/network/garnet2.0/InputUnit.hh"
#include "mem/ruby/network/garnet2.0/Router.hh"
#include "mem/ruby/network/garnet2.0/RoutingUnit.hh"
#include "mem/ruby/slicc_interface/Message.hh"

using namespace std;

RoutingUnit::RoutingUnit(Router *router)
{
    m_router = router;
    m_routing_table.clear();
    m_weight_table.clear();
}

void
RoutingUnit::addRoute(const NetDest& routing_table_entry)
{
    m_routing_table.push_back(routing_table_entry);
}

void
RoutingUnit::addWeight(int link_weight)
{
    m_weight_table.push_back(link_weight);
}

/*
 * This is the default routing algorithm in garnet.
 * The routing table is populated during topology creation.
 * Routes can be biased via weight assignments in the topology file.
 * Correct weight assignments are critical to provide deadlock avoidance.
 */

int
RoutingUnit::lookupRoutingTable(int vnet, NetDest msg_destination)
{
    // First find all possible output link candidates
    // For ordered vnet, just choose the first
    // (to make sure different packets don't choose different routes)
    // For unordered vnet, randomly choose any of the links
    // To have a strict ordering between links, they should be given
    // different weights in the topology file
    // cout<<"File: RoutingUnit.cc"<<endl;
    // cout<<"####################################################################"<<endl;
    // cout<<"Starting lookupRoutingTable"<<endl;
    // cout<<"vnet: "<<vnet<<endl;

    int output_link = -1;
    int min_weight = INFINITE_;
    std::vector<int> output_link_candidates;
    int num_candidates = 0;

    // cout<<"Identify the minimum weight among the candidate output links"<<endl;
    // Identify the minimum weight among the candidate output links
    for (int link = 0; link < m_routing_table.size(); link++) {
        // cout<<"link: "<<link<<" | m_weight_table: "<<m_weight_table[link]<<endl;
        if (msg_destination.intersectionIsNotEmpty(m_routing_table[link])) {

        if (m_weight_table[link] <= min_weight)
            min_weight = m_weight_table[link];
        }
    };

    // cout<<"Collect all candidate output links with this minimum weight"<<endl;
    // Collect all candidate output links with this minimum weight
    for (int link = 0; link < m_routing_table.size(); link++) {
        if (msg_destination.intersectionIsNotEmpty(m_routing_table[link])) {
            if (m_weight_table[link] == min_weight) {
                // cout<<"link: "<<link<<" | m_routing_table[link]: "<<m_routing_table[link]<<" | m_weight_table[link]: "<<m_weight_table[link]<<endl;
                num_candidates++;
                output_link_candidates.push_back(link);
            }
        }
    }

    for (int candidate_link = 0; candidate_link < output_link_candidates.size(); candidate_link++){
        // cout<<"output_link_candidates[candidate_link]: "<<output_link_candidates[candidate_link]<<endl;
    }

    if (output_link_candidates.size() == 0) {
        fatal("Fatal Error:: No Route exists from this Router.");
        exit(0);
    }

    // Randomly select any candidate output link
    int candidate = 0;
    if (!(m_router->get_net_ptr())->isVNetOrdered(vnet))
        candidate = rand() % num_candidates;

    output_link = output_link_candidates.at(candidate);
    // cout<<"RoutingUnit::lookupRoutingTable: vnet: "<<vnet<<" | output_link: "<<output_link<<endl;
    // cout<<"Finished lookupRoutingTable"<<endl;
    return output_link;
}


void
RoutingUnit::addInDirection(PortDirection inport_dirn, int inport_idx)
{
    m_inports_dirn2idx[inport_dirn] = inport_idx;
    m_inports_idx2dirn[inport_idx]  = inport_dirn;
}

void
RoutingUnit::addOutDirection(PortDirection outport_dirn, int outport_idx)
{
    m_outports_dirn2idx[outport_dirn] = outport_idx;
    m_outports_idx2dirn[outport_idx]  = outport_dirn;
}

// outportCompute() is called by the InputUnit
// It calls the routing table by default.
// A template for adaptive topology-specific routing algorithm
// implementations using port directions rather than a static routing
// table is provided here.

int
RoutingUnit::outportCompute(RouteInfo route, int inport,
                            PortDirection inport_dirn)
{
    int outport = -1;
    // cout<<"current router: "<<m_router->get_id()<<" | route.dest_router: "<<route.dest_router<<endl;
    int src_id = route.src_router;
    int src_coords[3];
    m_router->get_net_ptr()->getCoords(src_id,src_coords);
    int my_id = m_router->get_id();
    int my_coords[3];
    m_router->get_net_ptr()->getCoords(my_id,my_coords);
    int dest_id = route.dest_router;
    int dest_coords[3];
    m_router->get_net_ptr()->getCoords(dest_id,dest_coords);

    // cout<<"Src: ("<<src_coords[0]<<","<<src_coords[1]<<","<<src_coords[2]<<") | Current: ("<<my_coords[0]<<","<<my_coords[1]<<","<<my_coords[2]<<") | Dest: ("<<dest_coords[0]<<","<<dest_coords[1]<<","<<dest_coords[2]<<") cycle "<<m_router->curCycle();


    if (route.dest_router == m_router->get_id()) {
        // cout<<"choose lookupRoutingTable"<<endl;
        // Multiple NIs may be connected to this router,
        // all with output port direction = "Local"
        // Get exact outport id from table
        outport = lookupRoutingTable(route.vnet, route.net_dest);
        // cout<<endl;
        return outport;
    }

    // Routing Algorithm set in GarnetNetwork.py
    // Can be over-ridden from command line using --routing-algorithm = 1
    RoutingAlgorithm routing_algorithm =
        (RoutingAlgorithm) m_router->get_net_ptr()->getRoutingAlgorithm();
    switch (routing_algorithm) {
        case TABLE_:  outport =
            lookupRoutingTable(route.vnet, route.net_dest);
            // cout<<"choose lookupRoutingTable"<<endl; break;
        case XY_:     outport =
            outportComputeXY(route, inport, inport_dirn); break;
        case XYZ_:     outport =
            outportComputeXYZ(route, inport, inport_dirn); break;
        case XYZ_CHIPLETS: outport =
            outportComputeXYZChiplets(route, inport, inport_dirn); break;
            // cout<<"choose outportComputeXYZChiplets"<<endl;
        case XYZ_CHIPLETS2: outport =
            outportComputeXYZChiplets2(route, inport, inport_dirn); break;
        default: outport =
            lookupRoutingTable(route.vnet, route.net_dest); break;
    }

    assert(outport != -1);
    return outport;
}

// XY routing implemented using port directions
// Only for reference purpose in a Mesh
// By default Garnet uses the routing table
int
RoutingUnit::outportComputeXY(RouteInfo route,
                              int inport,
                              PortDirection inport_dirn)
{
    PortDirection outport_dirn = "Unknown";
    // cout<<"##########################################################################"<<endl;
    // cout<<"Starting ComputeXY\n"<<endl;
    // cout<<"Came from: "<<inport_dirn<<endl;

    int M5_VAR_USED num_rows = m_router->get_net_ptr()->getNumRows();
    int num_cols = m_router->get_net_ptr()->getNumCols();
    assert(num_rows > 0 && num_cols > 0);

    int my_id = m_router->get_id();
    int my_x = my_id % num_cols;
    int my_y = my_id / num_cols;
    // cout<<"current coordinates: ("<<my_x<<","<<my_y<<")"<<endl;

    int dest_id = route.dest_router;
    int dest_x = dest_id % num_cols;
    int dest_y = dest_id / num_cols;
    // cout<<"destination coordinates: ("<<dest_x<<","<<dest_y<<")"<<endl;

    int x_hops = abs(dest_x - my_x);
    int y_hops = abs(dest_y - my_y);
    // cout<<"NEEDS: "<< x_hops<<" x_hops, "<<y_hops<<" y_hops\n"<<endl;

    bool x_dirn = (dest_x >= my_x);
    bool y_dirn = (dest_y >= my_y);

    // already checked that in outportCompute() function
    assert(!(x_hops == 0 && y_hops == 0));

    if (x_hops > 0) {
        if (x_dirn) {
            assert(inport_dirn == "Local" || inport_dirn == "West");
            outport_dirn = "East";
        } else {
            assert(inport_dirn == "Local" || inport_dirn == "East");
            outport_dirn = "West";
        }
    } else if (y_hops > 0) {
        if (y_dirn) {
            // "Local" or "South" or "West" or "East"
            assert(inport_dirn != "North");
            outport_dirn = "North";
        } else {
            // "Local" or "North" or "West" or "East"
            assert(inport_dirn != "South");
            outport_dirn = "South";
        }
    } else {
        // x_hops == 0 and y_hops == 0
        // this is not possible
        // already checked that in outportCompute() function
        panic("x_hops == y_hops == 0");
    }

    // cout<<"Going: "<<outport_dirn<<endl;
    // cout<<"Finished ComputeXY"<<endl;
    // cout<<"##########################################################################"<<endl;
    return m_outports_dirn2idx[outport_dirn];
}

int
RoutingUnit::outportComputeXYZ(RouteInfo route,
                              int inport,
                              PortDirection inport_dirn)
{
    PortDirection outport_dirn = "Unknown";
    // cout<<"##########################################################################"<<endl;
    // cout<<"File: RoutingUnit.cc"<<endl;
    // cout<<"Starting ComputeZYX"<<endl;
    // cout<<"Came from: "<<inport_dirn<<"\n"<<endl;

    int M5_VAR_USED num_rows = m_router->get_net_ptr()->getNumRows();
    int num_cols = m_router->get_net_ptr()->getNumCols();
    int z_depth = m_router->get_net_ptr()->getZDepth();
    assert(num_rows > 0 && num_cols > 0 && z_depth > 0);

    int my_id = m_router->get_id();
    int my_z = (my_id/(num_rows*num_cols));
    int my_x = (my_id-(my_z*num_rows*num_cols)) % num_cols;
    int my_y = (my_id-(my_z*num_rows*num_cols)) / num_cols;
    // cout<<"Current Coordinates: ("<<my_z<<","<<my_y<<","<<my_x<<")"<<endl;

    int dest_id = route.dest_router;
    int dest_z = (dest_id/(num_rows*num_cols));
    int dest_x = (dest_id-(dest_z*num_rows*num_cols)) % num_cols;
    int dest_y = (dest_id-(dest_z*num_rows*num_cols)) / num_cols;
    // cout<<"Destination Coordinates: ("<<dest_z<<","<<dest_y<<","<<dest_x<<")"<<endl;

    int x_hops = abs(dest_x - my_x);
    int y_hops = abs(dest_y - my_y);
    int z_hops = abs(dest_z - my_z);
    // cout<<"NEEDS: "<< z_hops<<" z_hops, "<< y_hops<<" y_hops, "<<x_hops<<" x_hops\n"<<endl;

    bool x_dirn = (dest_x >= my_x); //true if destination is east of current
    bool y_dirn = (dest_y >= my_y); //true if destination is north of current
    bool z_dirn = (dest_z >= my_z); //true if destination is above current

    // already checked that in outportCompute() function
    assert(!(x_hops == 0 && y_hops == 0 && z_hops == 0));

    if (x_hops > 0) {
        if (x_dirn) {
            assert(inport_dirn == "Local" || inport_dirn == "West");
            outport_dirn = "East";
        } else {
            assert(inport_dirn == "Local" || inport_dirn == "East");
            outport_dirn = "West";
        }
    } else if (y_hops > 0) {
        if (y_dirn) {
            assert(inport_dirn != "North");
            outport_dirn = "North";
        } else {
            assert(inport_dirn != "South");
            outport_dirn = "South";
        }
    } else if (z_hops > 0) {
        if (z_dirn) {
            assert(inport_dirn != "Up");
            outport_dirn = "Up";
        } else {
            assert(inport_dirn != "Down");
            outport_dirn = "Down";
        }
    } else {
        // x_hops == 0 and y_hops == 0 and z_hops == 0
        // this is not possible
        // already checked that in outportCompute() function
        panic("x_hops == y_hops == z_hops == 0");
    }
    // cout<<"Going: "<<outport_dirn<<endl;
    // cout<<"Finished ComputeZYX"<<endl;
    // cout<<"##########################################################################"<<endl;

/*     cout<<"TESTING NORTH: "<<m_outports_dirn2idx["North"]<<endl;
    cout<<"TESTING SOUTH: "<<m_outports_dirn2idx["South"]<<endl;
    cout<<"TESTING EAST: "<<m_outports_dirn2idx["East"]<<endl;
    cout<<"TESTING WEST: "<<m_outports_dirn2idx["West"]<<endl;
    cout<<"TESTING UP: "<<m_outports_dirn2idx["Up"]<<endl;
    cout<<"TESTING DOWN: "<<m_outports_dirn2idx["Down"]<<endl;
    cout<<"TESTING LOCAL: "<<m_outports_dirn2idx["Local"]<<endl; */

    return m_outports_dirn2idx[outport_dirn];
}

int
RoutingUnit::outportComputeXYZChiplets(RouteInfo route,
                              int inport,
                              PortDirection inport_dirn)
{
    PortDirection outport_dirn = "Unknown";
    // cout<<"##########################################################################"<<endl;
    // cout<<"File: RoutingUnit.cc"<<endl;
    // cout<<"Starting ComputeZYXChiplet"<<endl;
    // cout<<"Came from: "<<inport_dirn<<"\n"<<endl;
    int num_chiplets_x = m_router->get_net_ptr()->getNumChipletsX();
    int num_chiplets_y = m_router->get_net_ptr()->getNumChipletsY();


    int M5_VAR_USED num_rows = m_router->get_net_ptr()->getNumRows();
    int num_cols = m_router->get_net_ptr()->getNumCols();
    int z_depth = m_router->get_net_ptr()->getZDepth();
    assert(num_rows > 0 && num_cols > 0 && z_depth > 0);

    int my_id = m_router->get_id();
    int my_coords[3];
    m_router->get_net_ptr()->getCoords(my_id,my_coords); //(z,y,x) = a[0],a[1],a[2]
    // cout<<"Current Coordinates: ("<<my_coords[0]<<","<<my_coords[1]<<","<<my_coords[2]<<")"<<endl;
    // cout<<"my_id: "<<my_id<<" | z_coord: "<<my_coords[0]<<endl;
    int my_quad = m_router->get_net_ptr()->getQuad(my_id, my_coords[0], num_chiplets_x, num_chiplets_y);

    // cout<<"Current Quadrant: "<<my_quad<<endl;

    int dest_id = route.dest_router;
    int dest_coords[3];
    m_router->get_net_ptr()->getCoords(dest_id,dest_coords); //(z,y,x) = a[0],a[1],a[2]
    // cout<<"Dest Coordinates: ("<<dest_coords[0]<<","<<dest_coords[1]<<","<<dest_coords[2]<<")"<<endl;
    // cout<<"dest_id: "<<dest_id<<" | z_coord: "<<dest_coords[0]<<endl;
    int dest_quad = m_router->get_net_ptr()->getQuad(dest_id, dest_coords[0], num_chiplets_x, num_chiplets_y);

    // cout<<"Destination Quadrant: "<<dest_quad<<endl;

    int x_hops = abs(dest_coords[2] - my_coords[2]);
    int y_hops = abs(dest_coords[1] - my_coords[1]);
    int z_hops = abs(dest_coords[0] - my_coords[0]);

    bool x_dirn = (dest_coords[2] >= my_coords[2]); //true if destination is east of current
    bool y_dirn = (dest_coords[1] >= my_coords[1]); //true if destination is north of current
    bool z_dirn = (dest_coords[0] >= my_coords[0]); //true if destination is above current
    bool same_quad = (my_quad == dest_quad); // true if destination and current router are in the same quadrant

    // cout<<" myquad: "<<my_quad<<" destquad: "<<dest_quad<<" same_quad: "<<same_quad;

    // Quadrant Numbering:
    // _______________
    // |      |      |
    // |  2   |   3  |
    // |______|______|
    // |      |      |
    // |  0   |   1  |
    // |______|______|

    // already checked that in outportCompute() function
    assert(!(x_hops == 0 && y_hops == 0 && z_hops == 0));

    if (same_quad){ // if current node and destination router are in the same quadrant, move normally
        if (x_hops > 0) {
            if (x_dirn) {
                // assert(inport_dirn == "Local" || inport_dirn == "West");
                outport_dirn = "East";
            } else {
                // assert(inport_dirn == "Local" || inport_dirn == "East");
                outport_dirn = "West";
            }
        } else if (y_hops > 0) {
            if (y_dirn) {
                // assert(inport_dirn != "North");
                outport_dirn = "North";
            } else {
                // assert(inport_dirn != "South");
                outport_dirn = "South";
            }
        } else if (z_hops > 0) {
            if (z_dirn) {
                // assert(inport_dirn != "Up");
                outport_dirn = "Up";
            } else {
                // assert(inport_dirn != "Down");
                outport_dirn = "Down";
            }
        } else {
            // x_hops == 0 and y_hops == 0 and z_hops == 0
            // this is not possible
            // already checked that in outportCompute() function
            panic("x_hops == y_hops == z_hops == 0");
        }
    } else { // if current router and destination router are not in the same quadrant
        if (my_coords[0] == 0) { //if router in layer 0, move in xy direction to same quadrant as router
            if (x_hops > 0) {
                if (x_dirn) {
                    outport_dirn = "East";
                } else {
                    outport_dirn = "West";
                }
            } else if (y_hops > 0) {
                if (y_dirn) {
                    assert(inport_dirn != "North");
                    outport_dirn = "North";
                } else {
                    assert(inport_dirn != "South");
                    outport_dirn = "South";
                }
            }
        } else { // if router not in layer 0, move to layer 0
            // assert(inport_dirn != "Down");
            outport_dirn = "Down";
        }
    }

    // cout<<" "<<outport_dirn<<endl;
    // for (int i=0; i<sizeof(m_outports_idx2dirn)/sizeof(m_outports_idx2dirn[0]); i = i + 1) {
    // for (int i=0; i<8; i = i + 1) {
    //     cout<<"m_outports_idx2dirn["<<i<<"]: "<<m_outports_idx2dirn[i]<<" | ";
    // }
    // cout<<endl<<"m_outports_dirn2idx["<<outport_dirn<<"]: "<<m_outports_dirn2idx[outport_dirn]<<endl;
    return m_outports_dirn2idx[outport_dirn];
    // cout<<"Finished ComputeZYXChiplet"<<endl;
    // cout<<"##########################################################################"<<endl;
}

int
RoutingUnit::outportComputeXYZChiplets2(RouteInfo route,
                              int inport,
                              PortDirection inport_dirn)
{
    PortDirection outport_dirn = "Unknown";
    int num_chiplets_x = 2;
    int num_chiplets_y = 2;

    int M5_VAR_USED num_rows = m_router->get_net_ptr()->getNumRows();
    int num_cols = m_router->get_net_ptr()->getNumCols();
    int z_depth = m_router->get_net_ptr()->getZDepth();
    assert(num_rows > 0 && num_cols > 0 && z_depth > 0);


    // cout<<"num_rows: "<<num_rows<<" | num_cols: "<<num_cols<<" | z_depth: "<<z_depth<<endl;

    int my_id = m_router->get_id();
    int my_coords[3];
    m_router->get_net_ptr()->getCoords(my_id,my_coords); //(z,y,x) = a[0],a[1],a[2]
    int my_quad = m_router->get_net_ptr()->getQuad(my_id, my_coords[0], num_chiplets_x, num_chiplets_y);


    int dest_id = route.dest_router;
    int dest_coords[3];
    m_router->get_net_ptr()->getCoords(dest_id,dest_coords); //(z,y,x) = a[0],a[1],a[2]
    int dest_quad = m_router->get_net_ptr()->getQuad(dest_id, dest_coords[0], num_chiplets_x, num_chiplets_y);

    int x_hops = abs(dest_coords[2] - my_coords[2]);
    int y_hops = abs(dest_coords[1] - my_coords[1]);
    int z_hops = abs(dest_coords[0] - my_coords[0]);
    // cout<<"NEEDS: "<< z_hops<<" z_hops, "<< y_hops<<" y_hops, "<<x_hops<<" x_hops\n"<<endl;

    bool x_dirn = (dest_coords[2] >= my_coords[2]); //true if destination is east of current
    bool y_dirn = (dest_coords[1] >= my_coords[1]); //true if destination is north of current
    bool z_dirn = (dest_coords[0] >= my_coords[0]); //true if destination is above current
    bool same_quad = (my_quad == dest_quad); // true if destination and current router are in the same quadrant

    // Quadrant Numbering:
    // _______________
    // |      |      |
    // |  2   |   3  |
    // |______|______|
    // |      |      |
    // |  0   |   1  |
    // |______|______|

    // already checked that in outportCompute() function
    assert(!(x_hops == 0 && y_hops == 0 && z_hops == 0));
    if (same_quad){ // if current node and destination router are in the same quadrant, move normally
        if (x_hops > 0) {
            if (x_dirn) {
                // assert(inport_dirn == "Local" || inport_dirn == "West");
                outport_dirn = "East";
            } else {
                // assert(inport_dirn == "Local" || inport_dirn == "East");
                outport_dirn = "West";
            }
        } else if (y_hops > 0) {
            if (y_dirn) {
                // assert(inport_dirn != "North");
                outport_dirn = "North";
            } else {
                // assert(inport_dirn != "South");
                outport_dirn = "South";
            }
        } else if (z_hops > 0) {
            if (z_dirn) {
                // assert(inport_dirn != "Up");
                outport_dirn = "Up";
            } else {
                // assert(inport_dirn != "Down");
                outport_dirn = "Down";
            }
        } else {
            panic("x_hops == y_hops == z_hops == 0");
        }
    } else { // if current router and destination router are not in the same quadrant
        if (my_coords[0] == 0) { //if router in layer 0, move in xy direction to same quadrant as router
            if (x_hops > 0) {
                if (x_dirn) {
                    outport_dirn = "East";
                } else {
                    outport_dirn = "West";
                }
            } else if (y_hops > 0) {
                if (y_dirn) {
                    assert(inport_dirn != "North");
                    outport_dirn = "North";
                } else {
                    assert(inport_dirn != "South");
                    outport_dirn = "South";
                }
            }
        } else { // if router not in layer 0, move to layer 0
            assert(inport_dirn != "Down");
            outport_dirn = "Down";
        }
    }

    // cout<<"Finished ComputeZYXChiplet"<<endl;
    // cout<<"##########################################################################"<<endl;

    return m_outports_dirn2idx[outport_dirn];
}


// parameters:
// - num-chiplets
// - cuts-x
// - cuts-y
//
// given number of chiplets to create and the x/y axises for the 'cuts',
// calculate the number of and location of each intersection. The number of
// intersections is equal to the number of line segments you must erase
// ex:  num-chiplets=5
//      cuts-x = [1,4]
//      cuts-y = [0,2]
//
//        o     o  |  o     o     o  |  o
//    2 -----------X-----------------X-----
//        o     o  |  o     o     o  |  o
//    1            |                 |
//        o     o  |  o     o     o  |  o
//    0 -----------X-----------------X-----
//        o     o  |  o     o     o  |  o
//                 |                 |
//           0     1     2     3     4
//
// **intersections marked with 'X' (4 total = cuts-x.length * cuts-y.length)**
// for each intersection:
//      if the intersection is surrounded by other intersections in all 4 cardinal directions:
//          segments = [all the line segments stemming from this intersection that do not lead to other intersections]
//      else if the intersection is surrounded by other intersections:
//          segments = [all the line segments stemming from this intersection]
//
//      randomly 'delete' a line segment from 'segments'
//
//
//
//
//
//
//
//
//
//



int
RoutingUnit::outportComputeChipletHetero(RouteInfo route,
                              int inport,
                              PortDirection inport_dirn)
{
    PortDirection outport_dirn = "Unknown";
    // cout<<"##########################################################################"<<endl;
    // cout<<"File: RoutingUnit.cc"<<endl;
    // cout<<"Starting ComputeChipletHetero"<<endl;
    // cout<<"Came from: "<<inport_dirn<<"\n"<<endl;
    int num_chiplets_x = 2;
    int num_chiplets_y = 2;

    int M5_VAR_USED num_rows = m_router->get_net_ptr()->getNumRows();
    int num_cols = m_router->get_net_ptr()->getNumCols();
    int z_depth = m_router->get_net_ptr()->getZDepth();
    assert(num_rows > 0 && num_cols > 0 && z_depth > 0);

    int my_id = m_router->get_id();
    int my_coords[3];
    m_router->get_net_ptr()->getCoords(my_id,my_coords); //(z,y,x) = a[0],a[1],a[2]
    // cout<<"Current Coordinates: ("<<my_coords[0]<<","<<my_coords[1]<<","<<my_coords[2]<<")"<<endl;
    // cout<<"my_id: "<<my_id<<" | z_coord: "<<my_coords[0]<<endl;
    int my_quad = m_router->get_net_ptr()->getQuad(my_id, my_coords[0], num_chiplets_x, num_chiplets_y);

    // cout<<"Current Quadrant: "<<my_quad<<endl;

    int dest_id = route.dest_router;
    int dest_coords[3];
    m_router->get_net_ptr()->getCoords(dest_id,dest_coords); //(z,y,x) = a[0],a[1],a[2]
    // cout<<"Dest Coordinates: ("<<dest_coords[0]<<","<<dest_coords[1]<<","<<dest_coords[2]<<")"<<endl;
    // cout<<"dest_id: "<<dest_id<<" | z_coord: "<<dest_coords[0]<<endl;
    int dest_quad = m_router->get_net_ptr()->getQuad(dest_id, dest_coords[0], num_chiplets_x, num_chiplets_y);

    // cout<<"Destination Quadrant: "<<dest_quad<<endl;

    int x_hops = abs(dest_coords[2] - my_coords[2]);
    int y_hops = abs(dest_coords[1] - my_coords[1]);
    int z_hops = abs(dest_coords[0] - my_coords[0]);

    bool x_dirn = (dest_coords[2] >= my_coords[2]); //true if destination is east of current
    bool y_dirn = (dest_coords[1] >= my_coords[1]); //true if destination is north of current
    bool z_dirn = (dest_coords[0] >= my_coords[0]); //true if destination is above current
    bool same_quad = (my_quad == dest_quad); // true if destination and current router are in the same quadrant

    // cout<<" myquad: "<<my_quad<<" destquad: "<<dest_quad<<" same_quad: "<<same_quad;

    // Quadrant Numbering:
    // _______________
    // |      |      |
    // |  2   |   3  |
    // |______|______|
    // |      |      |
    // |  0   |   1  |
    // |______|______|

    // already checked that in outportCompute() function
    assert(!(x_hops == 0 && y_hops == 0 && z_hops == 0));

    if (same_quad){ // if current node and destination router are in the same quadrant, move normally
        if (x_hops > 0) {
            if (x_dirn) {
                // assert(inport_dirn == "Local" || inport_dirn == "West");
                outport_dirn = "East";
            } else {
                // assert(inport_dirn == "Local" || inport_dirn == "East");
                outport_dirn = "West";
            }
        } else if (y_hops > 0) {
            if (y_dirn) {
                // assert(inport_dirn != "North");
                outport_dirn = "North";
            } else {
                // assert(inport_dirn != "South");
                outport_dirn = "South";
            }
        } else if (z_hops > 0) {
            if (z_dirn) {
                // assert(inport_dirn != "Up");
                outport_dirn = "Up";
            } else {
                // assert(inport_dirn != "Down");
                outport_dirn = "Down";
            }
        } else {
            // x_hops == 0 and y_hops == 0 and z_hops == 0
            // this is not possible
            // already checked that in outportCompute() function
            panic("x_hops == y_hops == z_hops == 0");
        }
    } else { // if current router and destination router are not in the same quadrant
        if (my_coords[0] == 0) { //if router in layer 0, move in xy direction to same quadrant as router
            if (x_hops > 0) {
                if (x_dirn) {
                    outport_dirn = "East";
                } else {
                    outport_dirn = "West";
                }
            } else if (y_hops > 0) {
                if (y_dirn) {
                    assert(inport_dirn != "North");
                    outport_dirn = "North";
                } else {
                    assert(inport_dirn != "South");
                    outport_dirn = "South";
                }
            }
        } else { // if router not in layer 0, move to layer 0
            // assert(inport_dirn != "Down");
            outport_dirn = "Down";
        }
    }

    return m_outports_dirn2idx[outport_dirn];
}
