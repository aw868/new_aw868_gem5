# to run: python3 generateNonUniformLayout.py
import random
import sys

print("Enter num rows (y-length): ")
y_length = int(input())
print("Enter num cols (x-length): ")
x_length = int(input())
print("Enter number of layers (z-length): ")
z_length = int(input())
print("Enter number of directories: ")
num_dir = int(input())
# print("Enter injection rate: ")
# injection_rate = float(input())
# print("Enter if wireless (0=wired only, 1=wireless): ")
# wireless = float(input())

injection_rate = 0.06
traffic_patterns = [
	"uniform_random", "tornado", "bit_reverse", "bit_rotation", "neighbor", "shuffle", "transpose"
]
chiplet_layout_string = '0,0,7,7,8,0,15,7,0,8,7,15,8,8,15,15'
ratio = y_length*x_length*z_length/num_dir

if (ratio == 1):
	topology = 'NonUniform_Chiplets'
elif (ratio == 2):
	topology = 'Sparse_NonUniform_Chiplets'
elif (ratio > 2):
	topology = 'SuperSparse_NonUniform_Chiplets'

file_name = 'T4_Z'+str(z_length)

with open('condor_'+file_name, 'w') as f:
    sys.stdout = f 
    print("""Universe = vanilla
Executable = /home/aw868/new_aw868_gem5/build/ARM/gem5.opt
Error = condortest.err
Output = condortest.out
Log = condortest.log

SYNCHRO_DIR = /home/aw868/new_aw868_gem5/results/%s
SYNTHTRAFFIC_RUN_SCRIPT =  /home/aw868/new_aw868_gem5/configs/example/garnet_synth_traffic.py\n""" %(file_name))

    for count,pattern in enumerate(traffic_patterns):
		for ir in range(-30,25,5):
			print("ARGS_%s_%s = --num-cpus=%s --num-dirs=%s --network=garnet --topology=%s --mesh-rows=%s --mesh-cols=%s --z-depth=%s --nu-chiplets-input=%s --sim-cycles=10000000 --synthetic=%s --routing-algorithm=4 --vcs-per-vnet=4 --injectionrate=%s" %(count, (ir+30)/5, y_length*x_length*z_length, num_dir, topology, y_length, x_length, z_length, chiplet_layout_string, pattern, injection_rate+float(ir/1000.0)))
			print("Initialdir = $(SYNCHRO_DIR)/ARGS_%s_%s" %(count, (ir+30)/5))
			print("arguments = \"$(SYNTHTRAFFIC_RUN_SCRIPT) $(ARGS_%s_%s)\"" %(count, (ir+30)/5))
			print("Queue\n")
   