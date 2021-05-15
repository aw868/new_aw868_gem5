# to run: python3 generateNonUniformLayout.py
import random
import sys

print("Enter topology type (0=T4_Z1, 1=T4_Z4, 2=T4_Z8): ")
topology_type = int(input())
print("Enter command type (0=gem5, 1=energy, 2=power sum): ")
command_type = int(input())
if command_type == 0:
	print("Enter injection rate sweep (0=general, 1=narrow): ")
	sweep_type = int(input())
	if sweep_type == 1:
		print("Enter saturation point: ")
		saturation_point = float(input())

topology_names = ["T4_Z1", "T4_Z4", "T4_Z8"]
file_name_prefix = ["general_","narrow_"]
sim_name = topology_names[topology_type]
results_dir_name = file_name_prefix[sweep_type]+"results"
x_length=16
y_length=16
chiplet_layout_string = "0,0,7,7,8,0,15,7,0,8,7,15,8,8,15,15"

if sweep_type==0:
	injection_rates = [0.085, 0.09, 0.095, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.275, 0.3, 0.325, 0.35, 0.375, 0.4, 0.425, 0.45, 0.475, 0.5, 0.525, 0.55, 0.575, 0.6, 0.625, 0.65]
if sweep_type==1:
	injection_rates = saturation_point + range(-30,25,5)/1000
	# [0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08]

traffic_patterns = [
	"uniform_random", "tornado", "bit_reverse", "neighbor", "shuffle", "transpose"
]

if topology_type==0:
	# T4_Z1 = 16x16x1
	z_length = 1
	topology = "NonUniform_Chiplets"
elif topology_type==1:
	# T4_Z4 = 16x16x4
	z_length = 4
	topology = "SuperSparse_NonUniform_Chiplets"
elif topology_type==2:
	# T4_Z8 = 16x16x8
	z_length = 8
	topology = "SuperSparse_NonUniform_Chiplets"

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
    for count, pattern in enumerate(traffic_patterns):
		for ir_index in range(len(injection_rates)):
			if command_type==0:
				print("ARGS_%s_%s = --num-cpus=%s --num-dirs=256 --network=garnet --topology=%s --mesh-rows=%s --mesh-cols=%s --z-depth=%s --nu-chiplets-input=%s --sim-cycles=10000000 --synthetic=%s --routing-algorithm=4 --vcs-per-vnet=4 --injectionrate=%s" %(count, ir_index, y_length*x_length*z_length, topology, y_length, x_length, z_length, chiplet_layout_string, pattern, injection_rates[ir_index]))
				print("Initialdir = $(RESULTS_DIR)/ARGS_%s_%s" %(count, ir_index))
				print("arguments = \"$(SYNTHTRAFFIC_RUN_SCRIPT) $(ARGS_%s_%s)\"" %(count, ir_index))
				print("Queue\n")
			elif command_type == 1:
				print("ARGS_%s_%s = /home/aw868/new_aw868_gem5/ %s/%s/ARGS_%s_%s/m5out" %(count, ir_index, results_dir_name, sim_name, count, ir_index))
				print("Initialdir = $(RESULTS_DIR)/ARGS_%s_%s" %(count, ir_index))
				print("arguments = \"$(ARGS_%s_%s) $(DSENT_CFG)\"" %(count, ir_index))
				print("Queue\n")
			elif command_type == 2:
				print("Initialdir = $(RESULTS_DIR)/ARG_%s_%s" %(count, ir_index))
				print("Queue\n")
   