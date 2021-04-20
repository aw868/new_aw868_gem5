# to run: python3 generateNonUniformLayout.py
import random
import sys

print("Enter num rows (y-length): ")
y_length = int(input())
print("Enter num cols (x-length): ")
x_length = int(input())
print("Enter number of layers (z-length): ")
z_length = int(input())
print("Enter number of layouts to generate: ")
num_layouts = int(input())
print("Enter injection rate: ")
injection_rate = float(input())
# print("Enter if wireless (0=wired only, 1=wireless): ")
# wireless = float(input())

with open('condor_MC2', 'w') as f:
    sys.stdout = f 
    print("""Universe = vanilla
Executable = /home/aw868/new_aw868_gem5/build/ARM/gem5.opt
Error = condortest.err
Output = condortest.out
Log = condortest.log

SYNCHRO_DIR = /home/aw868/new_aw868_gem5/results/MC2
SYNTHTRAFFIC_RUN_SCRIPT =  /home/aw868/new_aw868_gem5/configs/example/garnet_synth_traffic.py\n""")

    for i in range(num_layouts):
        chiplet_count = 0
        chiplet_array = [-1 for j in range(y_length*x_length)]
        chiplet_coords = []
        for router,chiplet in enumerate(chiplet_array):
            if chiplet == -1:
                x_min = int(router%x_length)
                y_min = int(router/x_length)
                x_max = x_min
                y_max = y_min

                for x in range(0, x_length-x_min):
                    if chiplet_array[router+x] == -1:
                        x_max = x+x_min
                    else:
                        break

                for y in range(0, y_length-y_min):
                    if chiplet_array[router+y*y_length] == -1:
                        y_max = y+y_min
                    else:
                        break

                rand_x = random.randint(x_min, x_max)
                rand_y = random.randint(y_min, y_max)
                # generate random coordinates for dimensions of chiplet
                for fill_y in range(y_min, rand_y+1):
                    for fill_x in range(x_min, rand_x+1):
                        # print("fill_x: " , fill_x , " | fill_y: " , fill_y)
                        # print("router,fill_x,fill_y*y_length: " , router+fill_x+fill_y*y_length)
                        assert chiplet_array[fill_x+fill_y*y_length] == -1
                        chiplet_array[fill_x+fill_y*y_length] = chiplet_count

                chiplet_count+=1
                chiplet_coords.extend([x_min, y_min, rand_x, rand_y])
        
        chiplet_coords_string = ','.join([str(elem) for elem in chiplet_coords])
        if (injection_rate == -1):
            for ir in range(1,10):
                print("ARGS_%s_%s = --num-cpus=%s --num-dirs=%s --network=garnet --topology=Sparse_NonUniform_Chiplets --mesh-rows=%s --mesh-cols=%s --z-depth=%s --nu-chiplets-input=%s --sim-cycles=10000000 --synthetic=uniform_random --routing-algorithm=4 --vcs-per-vnet=4 --injectionrate=%s" %(i, ir, y_length*x_length*z_length, y_length*x_length*z_length/2, y_length, x_length, z_length, chiplet_coords_string, float(ir/10.0)))
                print("Initialdir = $(SYNCHRO_DIR)/ARGS_%s_%s" %(i, ir))
                print("arguments = \"$(SYNTHTRAFFIC_RUN_SCRIPT) $(ARGS_%s_%s)\"" %(i, ir))
                print("Queue\n")
        else:
            for ir in range(-30,25,5):
                print("ARGS_%s_%s = --num-cpus=%s --num-dirs=%s --network=garnet --topology=Sparse_NonUniform_Chiplets --mesh-rows=%s --mesh-cols=%s --z-depth=%s --nu-chiplets-input=%s --sim-cycles=10000000 --synthetic=uniform_random --routing-algorithm=4 --vcs-per-vnet=4 --injectionrate=%s" %(i, (ir+30)/5, y_length*x_length*z_length, y_length*x_length*z_length/2, y_length, x_length, z_length, chiplet_coords_string, injection_rate+float(ir/1000.0)))
                print("Initialdir = $(SYNCHRO_DIR)/ARGS_%s_%s" %(i, (ir+30)/5))
                print("arguments = \"$(SYNTHTRAFFIC_RUN_SCRIPT) $(ARGS_%s_%s)\"" %(i, (ir+30)/5))
                print("Queue\n")
        # print(chiplet_coords)
        # for o in range(y_length-1, -1, -1):
        #     # print out current values in chiplet_array
        #     print(chiplet_array[o*x_length:(o+1)*x_length])

        assert not -1 in chiplet_array


    
