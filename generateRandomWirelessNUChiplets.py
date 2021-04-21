# to run: python3 generateNonUniformLayout.py
import random
import sys

# print("Enter num rows (y-length): ")
# y_length = int(input())
# print("Enter num cols (x-length): ")
# x_length = int(input())
# print("Enter number of layers (z-length): ")
# z_length = int(input())
# print("Enter chiplet layout: ")
# chiplet_layout = input()
# print("Enter wireless antenna placement: ")
# wireless_layout = input()
print("Enter the number of random topologies to generate: ")
num_simulations = int(input())

y_length = 16
x_length = 16
z_length = 2
injection_rate = 0.06
chiplet_layout_string = "0,0,7,3,8,0,15,3,0,4,7,7,8,4,15,7,0,8,7,11,8,8,15,11,0,12,7,15,8,12,15,15"
# 8 chiplets (hardcoded)

# chiplet_layout_string = ','.join(str(v) for v in chiplet_layout)
# wireless_layout_string = ','.join(str(v) for v in wireless_layout)

with open('condor_WMC_A32', 'w') as f:
    sys.stdout = f 
    print("""Universe = vanilla
Executable = /home/aw868/new_aw868_gem5/build/ARM/gem5.opt
Error = condortest.err
Output = condortest.out
Log = condortest.log

SYNCHRO_DIR = /home/aw868/new_aw868_gem5/results/WMC_A32
SYNTHTRAFFIC_RUN_SCRIPT =  /home/aw868/new_aw868_gem5/configs/example/garnet_synth_traffic.py\n""")
		
    for count in range(num_simulations):
		availableRouters = [x for x in range(y_length*x_length*(z_length+1))]
		wirelessRouters = []
		wirelessRouterCoords = []
		for i in range(2):
			layer_routers = [x for x in range((i+1)*x_length*y_length, (i+2)*x_length*y_length)]
			layer_set = set(layer_routers)
			for x in range(16):
				repeat = True
				while(repeat):
					# make sure there are enough routers in the layer that can be designated as wireless
					assert(len(layer_set.intersection(set(availableRouters))) >= 16-x)
					router = random.randint((i+1)*x_length*y_length, (i+2)*x_length*y_length-1)
					if(router not in wirelessRouters and router in availableRouters):
						# only add to the array if it does not already exist in array
						wirelessRouters.append(router)
						# add an additional layer to the router value to account for addition of layer 0
						# remove wireless router and its adjacent routers from availableRouters list
						availableRouters.remove(router)
						if (router+1 in availableRouters and router%x_length != x_length-1):
							availableRouters.remove(router+1)
						if (router-1 in availableRouters and router%x_length != 0):
							availableRouters.remove(router-1)
						if (router+x_length in availableRouters and router/x_length < y_length-1):
							availableRouters.remove(router+x_length)
						if (router-x_length in availableRouters and router/x_length > 0):
							availableRouters.remove(router-x_length)
						if (router+x_length*y_length in availableRouters):
							availableRouters.remove(router+x_length*y_length)
						if (router-x_length*y_length in availableRouters):
							availableRouters.remove(router-x_length*y_length)
						repeat = False
		for router_id in wirelessRouters:
			z_coord = router_id/(y_length*x_length)
			x_coord = -1
			y_coord = -1

			if(x_length == 1):
				x_coord = (router_id-(z_coord*y_length*x_length)) / x_length
				y_coord = (router_id-(z_coord*y_length*x_length)) % x_length
			else:
				x_coord = (router_id-(z_coord*y_length*x_length)) % x_length
				y_coord = (router_id-(z_coord*y_length*x_length)) / x_length
		
			wirelessRouterCoords.extend([x_coord,y_coord,z_coord])

		wireless_layout_string = ','.join(str(v) for v in wirelessRouterCoords)
		for ir in range(-30,25,5):
			print("ARGS_%s_%s = --num-cpus=%s --num-dirs=%s --network=garnet --topology=Sparse_Wireless_NUChiplets --mesh-rows=%s --mesh-cols=%s --z-depth=%s --nu-chiplets-input=%s --wireless-input-pattern=u --wireless-input=%s --sim-cycles=10000000 --synthetic=uniform_random --routing-algorithm=5 --vcs-per-vnet=4 --injectionrate=%s\n" %(count, (ir+30)/5, y_length*x_length*z_length, y_length*x_length*z_length/2, y_length, x_length, z_length, chiplet_layout_string, wireless_layout_string, injection_rate+float(ir/1000.0)))
			print("Initialdir = $(SYNCHRO_DIR)/ARGS_%s_%s" %(count, (ir+30)/5))
			print("arguments = \"$(SYNTHTRAFFIC_RUN_SCRIPT) $(ARGS_%s_%s)\"" %(count, (ir+30)/5))
			print("Queue\n")