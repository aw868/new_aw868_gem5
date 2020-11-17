# ./build/ARM/gem5.opt configs/example/garnet_synth_traffic.py  \
# --num-cpus=8 \
# --num-dirs=4 \
# --network=garnet2.0 \
# --topology=Homo_Chiplets \
# --mesh-rows=2  \
# --y-depth=2 \
# --z-depth=2 \
# --sim-cycles=200000 \
# --synthetic=uniform_random \
# --injectionrate=0.3 \
# --routing-algorithm=5 \
# --vcs-per-vnet=2 >./sim_results/SmallMeshXYZChiplet;

# ./build/ARM/gem5.opt configs/example/garnet_synth_traffic.py  \
# --num-cpus=256 \
# --num-dirs=4 \
# --network=garnet2.0 \
# --topology=Homo_Chiplets \
# --mesh-rows=8  \
# --y-depth=8 \
# --z-depth=4 \
# --sim-cycles=100 \
# --synthetic=uniform_random \
# --injectionrate=0.01 \
# --routing-algorithm=5 \
# --vcs-per-vnet=4 >./sim_results/LargeMeshXYZChiplet;

./build/ARM/gem5.opt configs/example/garnet_synth_traffic.py  \
--num-cpus=16 \
--num-dirs=16 \
--topology=Mesh_XYZ \
--network=garnet \
--mesh-rows=4  \
--sim-cycles=50000 \
--synthetic=uniform_random \
--injectionrate=0.3 \
--routing-algorithm=1 \
--vcs-per-vnet=4;

#--vcs-per-vnet=4 >/home/DREXEL/aw868/research/hetero_results/heChiplets_8x8x4_ir0.3_4vcpvnet_bash;
# ./build/ARM/gem5.opt configs/example/garnet_synth_traffic.py  \
# --num-cpus=256 \
# --num-dirs=4 \
# --network=garnet2.0 \
# --topology=VasilSucks \
# --mesh-rows=16  \
# --mem-size=16GB \
# --sim-cycles=100 \
# --synthetic=uniform_random \
# --injectionrate=0.01 \
# --routing-algorithm=0 \
# --vcs-per-vnet=4 >./sim_results/XYMesh_XYRouting;
