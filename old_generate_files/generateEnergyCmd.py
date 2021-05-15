# to run: python3 generateNonUniformLayout.py
import random
import sys

print("Enter outer number (default = 7): ")
outer_num = int(input())
print("Enter inner number (default = 11): ")
inner_num = int(input())
print("Enter folder name number: ")
dir_index = int(input())

num_traffic_patterns = 7
dir_names = ["MC1", "MC2", "T1", "T2", "T4", "T8", "T16", "T4_Z1", "T4_Z4", "T4_Z8", "WT1_A8", "WT2_A8", "WT4_A8", "WT8_A8", "WT16_A8", "WT8_A16", "WT8_A32", "WT8_A64", "WMC_A32"]

file_name = dir_names[dir_index]

with open("condor_"+file_name+"_energy", 'w') as f:
    sys.stdout = f 
    print("""Universe = vanilla
Executable = /home/aw868/new_aw868_gem5/condor_energy.sh
Error = energy.err
Output = energy.out
Log = energy.log

RESULTS_DIR = /home/aw868/new_aw868_gem5/results/%s
DSENT_CFG =  /home/aw868/new_aw868_gem5/ext/dsent/configs/router.cfg /home/aw868/new_aw868_gem5/ext/dsent/configs/electrical-link.cfg\n"""  %(file_name))

    for out_num in range(outer_num):
		for in_num in range(inner_num):
			print("ARGS_%s_%s = /home/aw868/new_aw868_gem5/ results/%s/ARGS_%s_%s/m5out" %(out_num, in_num, file_name, out_num, in_num))
			print("Initialdir = $(RESULTS_DIR)/ARGS_%s_%s" %(out_num, in_num))
			print("arguments = \"$(ARGS_%s_%s) $(DSENT_CFG)\"" %(out_num, in_num))
			print("Queue\n")