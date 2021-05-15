# to run: python3 generateNonUniformLayout.py
import random
import sys

print("Enter command type (0=gem5, 1=energy, 2=power sum): ")
command_type = int(input())
print("Enter injection rate sweep (0=general, 1=narrow): ")
sweep_type = int(input())
if sweep_type == 1:
	print("Enter saturation point: ")
	saturation_point = float(input())

file_name_prefix = ["general_","narrow_"]
sim_name = "T4_MC"
results_dir_name = file_name_prefix[sweep_type]+"results"

if sweep_type==0:
	injection_rates = [0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08, 0.085, 0.09, 0.095, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275]
if sweep_type==1:
	injection_rates = saturation_point + range(-30,25,5)/1000
	# [0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08]

traffic_patterns = [
	"uniform_random", "tornado", "bit_reverse", "neighbor", "shuffle", "transpose"
]

chiplet_layout_string = ['0,0,3,10,4,0,11,9,12,0,14,13,15,0,15,13,4,10,4,11,5,10,5,13,6,10,7,10,8,10,10,12,11,10,11,15,0,11,1,12,2,11,3,15,6,11,7,15,4,12,4,12,0,13,1,14,4,13,4,15,8,13,8,13,9,13,10,15,5,14,5,15,8,14,8,14,12,14,14,14,15,14,15,14,0,15,0,15,1,15,1,15,8,15,8,15,12,15,15,15', '0,0,14,5,15,0,15,15,0,6,13,6,14,6,14,12,0,7,10,11,11,7,11,14,12,7,13,15,0,12,4,15,5,12,7,13,8,12,10,14,14,13,14,13,5,14,5,15,6,14,6,14,7,14,7,14,14,14,14,14,6,15,7,15,8,15,9,15,10,15,11,15,14,15,14,15', '0,0,13,5,14,0,15,14,0,6,12,9,13,6,13,6,13,7,13,10,0,10,5,15,6,10,8,10,9,10,10,11,11,10,11,14,12,10,12,15,6,11,8,11,13,11,13,12,6,12,6,13,7,12,10,15,13,13,13,15,6,14,6,14,6,15,6,15,11,15,11,15,14,15,14,15,15,15,15,15', '0,0,7,11,8,0,12,5,13,0,13,14,14,0,14,9,15,0,15,11,8,6,10,13,11,6,12,15,14,10,14,11,0,12,7,12,14,12,14,13,15,12,15,14,0,13,1,14,2,13,6,15,7,13,7,13,7,14,9,14,10,14,10,14,14,14,14,14,0,15,1,15,7,15,10,15,13,15,13,15,14,15,15,15', '0,0,1,15,2,0,15,1,2,2,5,14,6,2,14,2,15,2,15,11,6,3,14,4,6,5,12,14,13,5,14,11,13,12,15,15,2,15,12,15', '0,0,3,15,4,0,10,9,11,0,12,0,13,0,14,14,15,0,15,3,11,1,11,13,12,1,12,4,15,4,15,13,12,5,12,5,12,6,12,8,12,9,12,13,4,10,9,13,10,10,10,12,10,13,10,13,4,14,10,15,11,14,11,15,12,14,12,14,15,14,15,15,12,15,14,15', '0,0,11,2,12,0,15,14,0,3,5,12,6,3,9,13,10,3,11,12,0,13,5,15,10,13,10,15,11,13,11,14,6,14,8,15,9,14,9,14,9,15,9,15,11,15,11,15,12,15,13,15,14,15,15,15', '0,0,15,5,0,6,10,9,11,6,13,15,14,6,14,6,15,6,15,14,14,7,14,14,0,10,3,12,4,10,5,14,6,10,8,14,9,10,9,12,10,10,10,14,0,13,3,15,9,13,9,14,4,15,9,15,10,15,10,15,14,15,14,15,15,15,15,15', '0,0,9,8,10,0,14,8,15,0,15,3,15,4,15,15,0,9,7,10,8,9,8,9,9,9,14,13,8,10,8,15,0,11,4,12,5,11,6,11,7,11,7,14,5,12,6,13,0,13,4,13,0,14,6,14,9,14,14,14,0,15,7,15,9,15,10,15,11,15,14,15', '0,0,11,8,12,0,13,5,14,0,14,10,15,0,15,14,12,6,12,13,13,6,13,10,0,9,2,15,3,9,9,9,10,9,11,15,3,10,3,14,4,10,4,12,5,10,6,11,7,10,8,14,9,10,9,15,13,11,13,12,14,11,14,11,5,12,6,15,14,12,14,12,4,13,4,14,13,13,13,13,14,13,14,13,12,14,13,15,14,14,14,15,3,15,4,15,7,15,8,15,15,15,15,15']
sim_num = [757, 711, 975, 453, 582, 448, 696, 761, 751, 432]

if command_type == 0:
	file_name = file_name_prefix[sweep_type]+sim_name
	header = """Universe = vanilla
Executable = /home/aw868/new_aw868_gem5/build/ARM/gem5.opt
Error = condor.err
Output = condor.out
Log = condor.log

RESULTS_DIR = /home/aw868/new_aw868_gem5/"""+results_dir_name+"""/"""+sim_name+"""
SYNTHTRAFFIC_RUN_SCRIPT =  /home/aw868/new_aw868_gem5/configs/example/garnet_synth_traffic.py\n"""

elif command_type == 1:
	file_name = file_name_prefix[sweep_type]+sim_name+'_energy'
	header = """Universe = vanilla
Executable = /home/aw868/new_aw868_gem5/condor_energy.sh
Error = energy.err
Output = energy.out
Log = energy.log

RESULTS_DIR = /home/aw868/new_aw868_gem5/"""+results_dir_name+"""/"""+sim_name+"""
DSENT_CFG =  /home/aw868/new_aw868_gem5/ext/dsent/configs/router.cfg /home/aw868/new_aw868_gem5/ext/dsent/configs/electrical-link.cfg\n"""
elif command_type == 2:
	file_name = file_name_prefix[sweep_type]+sim_name+'_power_sum'
	header = """Universe = vanilla
Executable = /home/aw868/new_aw868_gem5/condor_power_sum.sh
Error = power_sum.err
Output = power_sum.out
Log = power_sum.log

RESULTS_DIR = /home/aw868/new_aw868_gem5/"""+results_dir_name+"""/"""+sim_name+"""\n"""

with open(file_name, 'w') as f:
    sys.stdout = f 
    print(header)
    for num, sim in enumerate(sim_num):
		for count,pattern in enumerate(traffic_patterns):
			for ir_index in range(len(injection_rates)):
				if command_type==0:
					print("ARGS_%s_%s_%s = --num-cpus=512 --num-dirs=256 --network=garnet --topology=Sparse_NonUniform_Chiplets --mesh-rows=16 --mesh-cols=16 --z-depth=2 --nu-chiplets-input=%s --sim-cycles=10000000 --synthetic=%s --routing-algorithm=4 --vcs-per-vnet=4 --injectionrate=%s" %(sim, count, ir_index, chiplet_layout_string[num], pattern, injection_rates[ir_index]))
					print("Initialdir = $(RESULTS_DIR)/ARGS_%s_%s_%s" %(sim, count, ir_index))
					print("arguments = \"$(SYNTHTRAFFIC_RUN_SCRIPT) $(ARGS_%s_%s_%s)\"" %(sim, count, ir_index))
					print("Queue\n")
				elif command_type == 1:
					print("ARGS_%s_%s_%s = /home/aw868/new_aw868_gem5/ %s/%s/ARGS_%s_%s_%s/m5out" %(sim, count, ir_index, results_dir_name, sim_name, sim, count, ir_index))
					print("Initialdir = $(RESULTS_DIR)/ARGS_%s_%s_%s" %(sim, count, ir_index))
					print("arguments = \"$(ARGS_%s_%s_%s) $(DSENT_CFG)\"" %(sim, count, ir_index))
					print("Queue\n")
				elif command_type == 2:
					print("Initialdir = $(RESULTS_DIR)/ARG_%s_%s_%s" %(sim, count, ir_index))
					print("Queue\n")
   