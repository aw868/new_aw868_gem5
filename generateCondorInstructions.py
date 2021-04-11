# to run: python3 generateNonUniformLayout.py
import random
import sys

print("Enter num rows (y-length): ")
y_length = int(input())
print("Enter num cols (x-length): ")
x_length = int(input())
print("Enter number of layers (z-length): ")
z_length = int(input())
print("Enter chiplet layout: ")
chiplet_layout = input()
print("Enter injection rate: ")
injection_rate = float(input())
# print("Enter if wireless (0=wired only, 1=wireless): ")
# wireless = float(input())

traffic_patterns = [
	"uniform_random", "tornado", "bit_complement", "bit_reverse", "bit_rotation", "neighbor", "shuffle", "transpose"
]
i=0

with open('condor_T1', 'w') as f:
    sys.stdout = f 
    print("""Universe = vanilla
Executable = /home/aw868/new_aw868_gem5/build/ARM/gem5.opt
Error = condortest.err.$(Process)
Output = condortest.out.$(Process)
Log = condortest.log.$(Process)

SYNCHRO_DIR = /home/aw868/new_aw868_gem5/results/T1
SYNTHTRAFFIC_RUN_SCRIPT =  /home/aw868/new_aw868_gem5/configs/example/garnet_synth_traffic.py\n""")

    for patterns in traffic_patterns:
		for ir in range(-30,15,5):
			chiplet_layout_string = ','.join(str(v) for v in chiplet_layout)
			# print(chiplet_layout.replace(" ", "").replace(")", "").replace("(", ""))
			print("ARGS_%s = --num-cpus=%s --num-dirs=%s --network=garnet --topology=NonUniform_Chiplets --mesh-rows=%s --mesh-cols=%s --z-depth=%s --nu-chiplets-input=%s --sim-cycles=10000000 --synthetic=%s --routing-algorithm=4 --vcs-per-vnet=4 --injectionrate=%s" %(i, y_length*x_length*z_length, y_length*x_length*z_length, y_length, x_length, z_length, chiplet_layout_string, patterns, injection_rate+float(ir/100.0)))
			print("Initialdir = $(SYNCHRO_DIR)/$(Process)")
			print("arguments = \"$(SYNTHTRAFFIC_RUN_SCRIPT) $(ARGS_%s)\"" %(i))
			print("Queue\n")
			i=i+1
   