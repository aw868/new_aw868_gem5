# to run: python3 generateNonUniformLayout.py
import random
import sys

# print("Enter outer number (default = 7): ")
# outer_num = int(input())
# print("Enter inner number (default = 11): ")
# inner_num = int(input())
print("Enter folder name number: ")
dir_index = int(input())
# print("Enter energy type (0=router_dynamic, 1=router_leakage, 2=link_dynamic, 3=link_leakage): ")
# energy_index = int(input())

num_traffic_patterns = 7
dir_names = ["MC1", "MC2", "T1", "T2", "T4", "T8", "T16", "T4_Z1", "T4_Z4", "T4_Z8", "WT1_A8", "WT2_A8", "WT4_A8", "WT8_A8", "WT16_A8", "WT8_A16", "WT8_A32", "WT8_A64", "WMC_A32"]
outer_num_array = [10,1000,8,8,8,8,8,7,7,7,8,8,8,8,8,8,8,8,1000]
inner_num_array = [9,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11]
# energy_type = ["condor_router_dynamic","condor_router_leakage","condor_link_dynamic","condor_link_leakage"]
energy_name = ["router_dynamic","router_leakage","link_dynamic","link_leakage"]
outer_num = outer_num_array[dir_index]
inner_num = inner_num_array[dir_index]

file_name = dir_names[dir_index] + "_power_sum"
# energy_executable = energy_type[energy_index]

with open(file_name, 'w') as f:
	sys.stdout = f 
	print("""Universe = vanilla
Executable = /home/aw868/new_aw868_gem5/condor_power_sum.sh
Error = power_sum.err
Output = power_sum.out
Log = power_sum.log

RESULTS_DIR = /home/aw868/new_aw868_gem5/results/%s\n"""  %(dir_names[dir_index]))

	for out_num in range(outer_num):
		for in_num in range(inner_num):
			print("Initialdir = $(RESULTS_DIR)/ARGS_%s_%s" %(out_num, in_num))
			print("Queue\n")