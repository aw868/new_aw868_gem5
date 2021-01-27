# to run: python3 generateHeteroLayout.py
import random

print('Enter num rows (y-length):')
y_length = int(input())
print('Enter num cols (x-length):')
x_length = int(input())
print('Enter number of layouts to generate:')
num_layouts = int(input())

chiplet_count = 0
for i in range(num_layouts):
    chiplet_array = [-1 for j in range(y_length*x_length)]
    for router,chiplet in enumerate(chiplet_array):
        if chiplet == -1:
            x_min = int(router%x_length)
            y_min = int(router/x_length)
            x_max = x_min
            y_max = y_min

            for x in range(1, x_length-x_min):
                # print(router+x)
                if chiplet_array[router+x] == -1:
                    x_max = x+x_min

            for y in range(1, y_length-y_min):
                # print(router+y*y_length)
                if chiplet_array[router+y*y_length] == -1:
                    y_max = y+y_min

            rand_x = random.randint(x_min, x_max+1)
            rand_y = random.randint(y_min, y_max+1)

            for fill_y in range(rand_y):
                for fill_x in range(rand_x):
                    chiplet_array[router+fill_x+fill_y*y_length] = chiplet_count

            chiplet_count+=1

            # print(x_min, y_min)
    # print(*chiplet_array, sep = ", ")
