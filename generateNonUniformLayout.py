# to run: python3 generateNonUniformLayout.py
import random

print("Enter num rows (y-length): ")
y_length = int(input())
print("Enter num cols (x-length): ")
x_length = int(input())
print("Enter number of layouts to generate: ")
num_layouts = int(input())

for i in range(num_layouts):
    chiplet_count = 0
    chiplet_array = [-1 for j in range(y_length*x_length)]
    chiplet_coords = []
    for router,chiplet in enumerate(chiplet_array):
        # print("router: " , router , " | chiplet: " , chiplet)
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

            # print("x_min: " , x_min , " | x_max: " , x_max)
            # print("y_min: " , y_min , " | y_max: " , y_max)
            
            rand_x = random.randint(x_min, x_max)
            rand_y = random.randint(y_min, y_max)
            # generate random coordinates for dimensions of chiplet

            # print("rand_x: " , rand_x , " | rand_y: " , rand_y)

            for fill_y in range(y_min, rand_y+1):
                for fill_x in range(x_min, rand_x+1):
                    # print("fill_x: " , fill_x , " | fill_y: " , fill_y)
                    # print("router,fill_x,fill_y*y_length: " , router+fill_x+fill_y*y_length)
                    assert chiplet_array[fill_x+fill_y*y_length] == -1
                    chiplet_array[fill_x+fill_y*y_length] = chiplet_count

            chiplet_count+=1
            chiplet_coords.extend([x_min, rand_x, y_min, rand_y])
    
    print(chiplet_coords, "\n")
    for o in range(y_length-1, -1, -1):
        # print out current values in chiplet_array
        print(chiplet_array[o*x_length:(o+1)*x_length])
    print("\n")

    assert not -1 in chiplet_array

    f = open("randomNonUniformLayouts.txt", "a")
    f.write(chiplet_coords)
    f.close()
