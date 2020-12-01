/*
 * Copyright (c) 2020 Advanced Micro Devices, Inc.
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
 */


#ifndef __MEM_RUBY_NETWORK_GARNET_0_GARNETNETWORK_HH__
#define __MEM_RUBY_NETWORK_GARNET_0_GARNETNETWORK_HH__

#include <iostream>
#include <vector>
using namespace std;

#include "mem/ruby/network/Network.hh"
#include "mem/ruby/network/fault_model/FaultModel.hh"
#include "mem/ruby/network/garnet/CommonTypes.hh"
#include "params/GarnetNetwork.hh"

class FaultModel;
class NetworkInterface;
class Router;
class NetDest;
class NetworkLink;
class CreditLink;

class GarnetNetwork : public Network
{
  public:
    typedef GarnetNetworkParams Params;
    GarnetNetwork(const Params *p);
    ~GarnetNetwork() = default;

    void init();

    const char *garnetVersion = "3.0";

    // Configuration (set externally)

    // for 2D topology
    int getNumRows() const { return m_num_rows; }
    int getNumCols() { return m_num_cols; }
    int getZDepth() { return m_z_depth; }
    int getNumChipletsX() { return m_num_chiplets_x;}
    int getNumChipletsY() { return m_num_chiplets_y;}
    string getHeteroInput() { return m_hetero_chiplets_input;}
    int* getCoords(int router_id, int coords[]) {
        int z_coord = router_id/(m_num_rows*m_num_cols); //calculating z coordinate
        int x_coord = -1;
        int y_coord = -1;

        if(m_num_cols == 1){
            x_coord = (router_id-(z_coord*m_num_rows*m_num_cols)) / m_num_cols; //calculating x coordinate
            y_coord = (router_id-(z_coord*m_num_rows*m_num_cols)) % m_num_cols; //calculating y coordinate
        } else {
            x_coord = (router_id-(z_coord*m_num_rows*m_num_cols)) % m_num_cols; //calculating x coordinate
            y_coord = (router_id-(z_coord*m_num_rows*m_num_cols)) / m_num_cols; //calculating y coordinate
        }
        assert(x_coord>-1 && y_coord>-1 && z_coord>-1);
        coords[0] = z_coord;
        coords[1] = y_coord;
        coords[2] = x_coord;
        // cout<<"getCoords: ("<<coords[0]<<", "<<coords[1]<<", "<<coords[2]<<")"<<endl;
        return coords;
    }
    
    int getSectorHo(int router_id, int z_coord, int num_chiplets_x, int num_chiplets_y) { 
        // location = id - (GlobalParams::mesh_dim_x * GlobalParams::mesh_dim_y)*(layer_num-1);
        // subnet_x = (location % GlobalParams::mesh_dim_x) / GlobalParams::subnet_dim_x;
        // subnet_y = ((location / GlobalParams::mesh_dim_x) % GlobalParams::mesh_dim_y) / GlobalParams::subnet_dim_y;
        // subnet_id = subnet_x + subnet_y*(GlobalParams::mesh_dim_x/GlobalParams::subnet_dim_x);

        int subnet_dim_x = m_num_rows/num_chiplets_x;
        int subnet_dim_y = m_num_cols/num_chiplets_y;

        int base_id = router_id-(m_num_rows*m_num_cols)*(z_coord);
        int sector_x = (base_id%m_num_rows)/subnet_dim_x;
        int sector_y = ((base_id/m_num_rows)%m_num_cols)/subnet_dim_y;
        int sector = sector_x+sector_y*(m_num_rows/subnet_dim_x);

        // cout<<"getSectorHo: base_id: "<<base_id<<" | sector_x: "<<sector_x<<" | sector_y: "<<sector_y<<" | sector: "<<sector<<endl;
        
        assert(sector<num_chiplets_x*num_chiplets_y && sector>=0);
        return sector;
    }

    struct not_digit {
        bool operator()(const char c) {
            return c != ' ' && !std::isdigit(c);
        }
    };

    vector<int> stringToVector(string stringInput) {
        cout<<"stringToVector(string stringInput)"<<endl;
        vector<int> base_router_list;
        not_digit not_a_digit;
        string::iterator end = std::remove_if(stringInput.begin(), stringInput.end(), not_a_digit);
        string all_numbers(stringInput.begin(), end);
        stringstream ss(all_numbers);
        cout <<"here"<<endl;;
        for(int i = 0; ss >> i; ) {
            base_router_list.push_back(i);
            cout << i << " ";
        }
        // assert that input is multiple of 4
        return base_router_list;
    }

    vector<int> calculateBaseRouters(string heteroChipletString) {
        cout<<"calculateBaseRouters(string heteroChipletInputs)"<<endl;
        // vector<int> base_router_list(m_num_rows*m_num_cols, -1);
        // initialize to -1, errors if value=-1 at the end
        cout<<heteroChipletString<<endl;
        vector<int> base_router_list = stringToVector(heteroChipletString);

        // for (int i = 0; i < heteroChipletInputs.size(); i++) { 
        //     // for each hetero chiplet, set value at index to sector number
        //     for (int row=heteroChipletInputs[i][2];row<heteroChipletInputs[i][3];row++){
        //         for (int col=heteroChipletInputs[i][0];col<heteroChipletInputs[i][1];col++) {
        //             int router_id = row*m_num_cols+col;
        //             heteroChipletInputs[router_id] = i;
        //         }
        //     }
        // }

        if(count(base_router_list.begin(), base_router_list.end(), -1)){
            fatal("Hetero Chiplet input does not include all routers");
            exit(0);
        }
        return base_router_list;
    }

    int getSectorHe(int router_id, int z_coord, int num_sectors) { 
        cout<<"File: GarnetNetwork.hh"<<endl;
        cout<<"getSectorHe(int router_id, int z_coord, int num_sectors)"<<endl;

        int sector = -1;
        int base_id = router_id-(m_num_rows*m_num_cols)*(z_coord);

        for (int i=0;i<m_sector_list.size();i++) {
            cout<<m_sector_list[i]<<endl;
        }
        // // start row/x, end row/x, start col/y, end col/y
        // vector<vector<int>> sector_list_input = {{0,1,0,1}, 
        //                                         {2,5,0,3},
        //                                         {6,7,0,1},
        //                                         {0,1,2,3},
        //                                         {6,7,2,3}};
        // vector<int> sector_list = calculateBaseRouters(sector_list_input);
        sector = m_sector_list[base_id];

        assert(sector>=0);
        return sector;
    }

    // for network
    uint32_t getNiFlitSize() const { return m_ni_flit_size; }
    uint32_t getBuffersPerDataVC() { return m_buffers_per_data_vc; }
    uint32_t getBuffersPerCtrlVC() { return m_buffers_per_ctrl_vc; }
    int getRoutingAlgorithm() const { return m_routing_algorithm; }
    

    bool isFaultModelEnabled() const { return m_enable_fault_model; }
    FaultModel* fault_model;


    // Internal configuration
    bool isVNetOrdered(int vnet) const { return m_ordered[vnet]; }
    VNET_type
    get_vnet_type(int vnet)
    {
        return m_vnet_type[vnet];
    }
    int getNumRouters();
    int get_router_id(int ni, int vnet);


    // Methods used by Topology to setup the network
    void makeExtOutLink(SwitchID src, NodeID dest, BasicLink* link,
                     std::vector<NetDest>& routing_table_entry);
    void makeExtInLink(NodeID src, SwitchID dest, BasicLink* link,
                    std::vector<NetDest>& routing_table_entry);
    void makeInternalLink(SwitchID src, SwitchID dest, BasicLink* link,
                          std::vector<NetDest>& routing_table_entry,
                          PortDirection src_outport_dirn,
                          PortDirection dest_inport_dirn);

    //! Function for performing a functional write. The return value
    //! indicates the number of messages that were written.
    uint32_t functionalWrite(Packet *pkt);

    // Stats
    void collateStats();
    void regStats();
    void resetStats();
    void print(std::ostream& out) const;

    // increment counters
    void increment_injected_packets(int vnet) { m_packets_injected[vnet]++; }
    void increment_received_packets(int vnet) { m_packets_received[vnet]++; }

    void
    increment_packet_network_latency(Tick latency, int vnet)
    {
        m_packet_network_latency[vnet] += latency;
    }

    void
    increment_packet_queueing_latency(Tick latency, int vnet)
    {
        m_packet_queueing_latency[vnet] += latency;
    }

    void increment_injected_flits(int vnet) { m_flits_injected[vnet]++; }
    void increment_received_flits(int vnet) { m_flits_received[vnet]++; }

    void
    increment_flit_network_latency(Tick latency, int vnet)
    {
        m_flit_network_latency[vnet] += latency;
    }

    void
    increment_flit_queueing_latency(Tick latency, int vnet)
    {
        m_flit_queueing_latency[vnet] += latency;
    }

    void
    increment_total_hops(int hops)
    {
        m_total_hops += hops;
    }

  protected:
    // Configuration
    int m_num_rows;
    int m_num_cols;
    int m_z_depth;
    int m_num_chiplets_x;
    int m_num_chiplets_y;
    string m_hetero_chiplets_input;
    uint32_t m_ni_flit_size;
    uint32_t m_max_vcs_per_vnet;
    uint32_t m_buffers_per_ctrl_vc;
    uint32_t m_buffers_per_data_vc;
    int m_routing_algorithm;
    bool m_enable_fault_model;
    vector<int> m_sector_list; 

    // Statistical variables
    Stats::Vector m_packets_received;
    Stats::Vector m_packets_injected;
    Stats::Vector m_packet_network_latency;
    Stats::Vector m_packet_queueing_latency;

    Stats::Formula m_avg_packet_vnet_latency;
    Stats::Formula m_avg_packet_vqueue_latency;
    Stats::Formula m_avg_packet_network_latency;
    Stats::Formula m_avg_packet_queueing_latency;
    Stats::Formula m_avg_packet_latency;

    Stats::Vector m_flits_received;
    Stats::Vector m_flits_injected;
    Stats::Vector m_flit_network_latency;
    Stats::Vector m_flit_queueing_latency;

    Stats::Formula m_avg_flit_vnet_latency;
    Stats::Formula m_avg_flit_vqueue_latency;
    Stats::Formula m_avg_flit_network_latency;
    Stats::Formula m_avg_flit_queueing_latency;
    Stats::Formula m_avg_flit_latency;

    Stats::Scalar m_total_ext_in_link_utilization;
    Stats::Scalar m_total_ext_out_link_utilization;
    Stats::Scalar m_total_int_link_utilization;
    Stats::Scalar m_average_link_utilization;
    Stats::Vector m_average_vc_load;

    Stats::Scalar  m_total_hops;
    Stats::Formula m_avg_hops;

  private:
    GarnetNetwork(const GarnetNetwork& obj);
    GarnetNetwork& operator=(const GarnetNetwork& obj);

    std::vector<VNET_type > m_vnet_type;
    std::vector<Router *> m_routers;   // All Routers in Network
    std::vector<NetworkLink *> m_networklinks; // All flit links in the network
    std::vector<CreditLink *> m_creditlinks; // All credit links in the network
    std::vector<NetworkInterface *> m_nis;   // All NI's in Network
};

inline std::ostream&
operator<<(std::ostream& out, const GarnetNetwork& obj)
{
    obj.print(out);
    out << std::flush;
    return out;
}

#endif //__MEM_RUBY_NETWORK_GARNET_0_GARNETNETWORK_HH__