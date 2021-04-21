# to run: python3 generateNonUniformLayout.py
import random
import sys

# print("Enter num rows (y-length): ")
# y_length = int(input())
# print("Enter num cols (x-length): ")
# x_length = int(input())
# print("Enter number of layers (z-length): ")
# z_length = int(input())
print("Enter number of chiplets: ")
num_chiplets = input()
print("Enter number of antennas: ")
num_antennas = int(input())
# print("Enter injection rate: ")
# injection_rate = float(input())
# print("Enter if wireless (0=wired only, 1=wireless): ")
# wireless = float(input())

y_length = 16
x_length = 16
z_length = 2

injection_rate = 0.06
traffic_patterns = [
	"uniform_random", "tornado", "bit_complement", "bit_reverse", "bit_rotation", "neighbor", "shuffle", "transpose"
]

if (num_chiplets == 1):
	chiplet_layout_string = "0,0,15,15"
elif (num_chiplets == 2):
	chiplet_layout_string = "0,0,15,7,0,8,15,15"
elif (num_chiplets == 4):
	chiplet_layout_string = "0,0,7,7,8,0,15,7,0,8,7,15,8,8,15,15"
elif (num_chiplets == 8):
	chiplet_layout_string = "0,0,7,3,8,0,15,3,0,4,7,7,8,4,15,7,0,8,7,11,8,8,15,11,0,12,7,15,8,12,15,15"
elif (num_chiplets == 16):
	chiplet_layout_string = "0,0,3,3,4,0,7,3,8,0,11,3,12,0,15,3,0,4,3,7,4,4,7,7,8,4,11,7,12,4,15,7,0,8,3,11,4,8,7,11,8,8,11,11,12,8,15,11,0,12,3,15,4,12,7,15,8,12,11,15,12,12,15,15"

if (num_antennas == 8):
	wireless_layout_string = "1,1,1,14,1,1,4,5,1,11,5,1,4,10,1,11,10,1,1,14,1,14,14,1"
elif (num_antennas == 16):
	wireless_layout_string = "1,1,1,14,1,1,6,3,1,9,3,1,2,4,1,13,4,1,4,5,1,11,5,1,4,10,1,11,10,1,2,11,1,13,11,1,6,12,1,9,12,1,1,14,1,14,14,1"
elif (num_antennas == 32):
	wireless_layout_string = "1,1,1,4,1,1,7,1,1,9,1,1,11,1,1,14,1,1,6,3,1,9,3,1,2,4,1,13,4,1,4,5,1,11,5,1,1,6,1,6,6,1,9,6,1,14,6,1,1,9,1,6,9,1,9,9,1,14,9,1,4,10,1,11,10,1,2,11,1,13,11,1,6,12,1,9,12,1,1,14,1,4,14,1,7,14,1,9,14,1,11,14,1,14,14,1"
elif (num_antennas == 64):
	wireless_layout_string = "1,1,1,4,1,1,6,1,1,9,1,1,11,1,1,14,1,1,3,2,1,5,2,1,8,2,1,10,2,1,12,2,1,1,3,1,6,3,1,9,3,1,14,3,1,2,4,1,5,4,1,7,4,1,10,4,1,13,4,1,4,5,1,8,5,1,11,5,1,1,6,1,3,6,1,6,6,1,9,6,1,12,6,1,14,6,1,5,7,1,7,7,1,10,7,1,4,8,1,8,8,1,11,8,1,1,9,1,3,9,1,6,9,1,9,9,1,12,9,1,14,9,1,4,10,1,8,10,1,11,10,1,2,11,1,5,11,1,7,11,1,10,11,1,13,11,1,1,12,1,4,12,1,6,12,1,9,12,1,11,12,1,14,12,1,3,13,1,7,13,1,12,13,1,1,14,1,4,14,1,6,14,1,9,14,1,11,14,1,14,14,1"

file_name = 'WT'+str(num_chiplets)+'_A'+str(num_antennas)

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
			print("ARGS_%s_%s = --num-cpus=%s --num-dirs=%s --network=garnet --topology=Sparse_Wireless_NUChiplets --mesh-rows=%s --mesh-cols=%s --z-depth=%s --nu-chiplets-input=%s --wireless-input-pattern=u --wireless-input=%s --sim-cycles=10000000 --synthetic=%s --routing-algorithm=5 --vcs-per-vnet=4 --injectionrate=%s" %(count, (ir+30)/5, y_length*x_length*z_length, y_length*x_length*z_length/2, y_length, x_length, z_length, chiplet_layout_string, wireless_layout_string, pattern, injection_rate+float(ir/1000.0)))
			print("Initialdir = $(SYNCHRO_DIR)/ARGS_%s_%s" %(count, (ir+30)/5))
			print("arguments = \"$(SYNTHTRAFFIC_RUN_SCRIPT) $(ARGS_%s_%s)\"" %(count, (ir+30)/5))
			print("Queue\n")
   