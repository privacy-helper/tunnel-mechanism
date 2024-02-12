import random
import collections
from math import log, e, floor, ceil
import matplotlib.pyplot as plt
import csv
import numpy as np
import pandas as pd
import array

test = 10

# # type: 0 --> basic
# # type: 1 --> with random traffic gen coefficient
# # type: 2 --> with tunnel build coefficient
# # type: 3 --> proposed structure
# type = 3

# test_1_step = 10
# test_1_num_iter = 10
# test_1_repeat = 100

# number_of_ids = 100
# number_of_tunnels = 10
# tunnel_length = 3
# calc_entropy_flag = True

# # adjustable_parameters
# traffic_gen_coefficient = 0.5   # (0, 1]
# tunnel_build_coefficient = 0.5  # (0, 1]
# num_cluster = 4
# num_permanent_per_cluster = 5
strict_list = set()             # ex. [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]




def object_to_list(object_value):
    list_len = len(object_value)
    two_dim_list = [[1 for x in range(2)] for y in range(list_len)]
    i = 0
    for key, value in object_value.items():
        two_dim_list[i][0] = key
        two_dim_list[i][1] = value
        i += 1

    return two_dim_list

def draw_plot(x, y):
    plt.plot(x, y, label = "line 2")

    # naming the x axis
    plt.xlabel('x - axis')
    # naming the y axis
    plt.ylabel('y - axis')
    # giving a title to my graph
    plt.title('Two lines on same graph!')

    # show a legend on the plot
    plt.legend()

    # function to show the plot
    plt.show()

def create_csv(filename, content):
    # create a csv file called test.csv and
    # store it a temp variable as outfile
    with open(filename, "w") as outfile:    
        # pass the csv file to csv.writer.
        writer = csv.writer(outfile)       
        # convert the dictionary keys to a list
        key_list = list(content.keys())
        # find the length of the key_list
        limit = len(content[key_list[0]])
        # the length of the keys corresponds to
        # no. of. columns.
        writer.writerow(content.keys())
        # iterate each column and assign the
        # corresponding values to the column
        for i in range(limit):
            writer.writerow([content[x][i] for x in key_list])


def select_random_list_from_range(lower, upper, len):
    random_list = random.sample(range(lower, upper), len)
    return random_list

def select_random_list_from_list(list, len):
    random_list = random.sample(list, len)
    return random_list

def create_list_from_range_with_exclude(lower, upper, exclude):
    choices = set(range(lower, upper + 1)) - set(exclude)
    return list(choices)

def select_random_list_from_range_with_exclude(lower, upper, len, exclude):
    global strict_list

    choices = create_list_from_range_with_exclude(lower, upper, exclude)
    random_list = []
    list_len = 0
    random_shared_loc_in_tunnel = select_random_list_from_range(0, len, 1)
    # random_shared_loc_in_tunnel = 1
    
    while(True):
        new_choice = 0
        if(random_shared_loc_in_tunnel == list_len and strict_list != set()):
            new_choice = random.choice(list(strict_list))
        else:
            new_choice = random.choice(list(choices))

        if(new_choice not in random_list):
            random_list.append(new_choice)
            list_len += 1

        if(list_len > (len - 1)):
            strict_list.update(set(random_list))
            # print(strict_list)
            break

    return random_list

def create_random_tunnel(lower, upper, num_tunnels, tunnel_len, tunnel_build_coefficient, type=0):
    tunnel_list = [[0 for x in range(tunnel_len + 2)] for y in range(num_tunnels)]
    random_tunnel_owners_list = select_random_list_from_range(lower, upper, num_tunnels)
    
    num_concurrent_build_tunnels = 0
    num_concurrent_build_tunnels_idx_list = []
    num_concurrent_build_tunnels_list = []
    if(type == 2):
        num_concurrent_build_tunnels = int(tunnel_build_coefficient * num_tunnels)
        num_concurrent_build_tunnels_idx_list = select_random_list_from_range(lower, num_tunnels, num_concurrent_build_tunnels)
        num_concurrent_build_tunnels_list = [random_tunnel_owners_list[i] for i in num_concurrent_build_tunnels_idx_list]

    tunnel_index = 0
    for tunnel_owner in random_tunnel_owners_list:
        tunnel_list[tunnel_index][0] = tunnel_owner
        tunnel_participants_list = select_random_list_from_range_with_exclude(lower, upper, tunnel_len, [tunnel_owner])
        tunnel_order_index = 0
        for tunnel_participant in tunnel_participants_list:
            tunnel_order_index += 1
            tunnel_list[tunnel_index][tunnel_order_index] = tunnel_participant
        
        if((tunnel_owner in num_concurrent_build_tunnels_list) or type != 2):
            tunnel_list[tunnel_index][4] = 1
        else:
            tunnel_list[tunnel_index][4] = -1
        tunnel_index += 1
    # print(tunnel_list)

    return tunnel_list

def create_clustering(num_cluster, lower, upper, num_permanent_per_cluster):
    num_ids = upper - lower
    num_ids_per_cluster = floor(num_ids/num_cluster)
    remain_ids = num_ids%num_cluster
    random_clustering_ids_mx = [[] for y in range(num_cluster)]
    random_clustering_permanents_ids_mx = [[0 for x in range(num_permanent_per_cluster)] for y in range(num_cluster)]

    allocated_remain_ids = 0
    for i in range(num_cluster):
        num_ids_in_this_cluster = num_ids_per_cluster
        if((remain_ids > 0) and (allocated_remain_ids < remain_ids)):
            num_ids_in_this_cluster = num_ids_per_cluster + 1
        random_clustering_ids_mx[i] = [(i*num_ids_per_cluster + allocated_remain_ids + x) for x in range(num_ids_in_this_cluster)]
        if((remain_ids > 0) and (allocated_remain_ids < remain_ids)):
            allocated_remain_ids += 1

    for i in range(num_cluster):
        random_clustering_permanents_ids_mx[i] = select_random_list_from_range_with_exclude(lower, upper, num_permanent_per_cluster, random_clustering_ids_mx[i])

    # print(random_clustering_permanents_ids_mx) 
    # print(random_clustering_ids_mx)

    return random_clustering_ids_mx, random_clustering_permanents_ids_mx

def find_cluster_id(tunnel_owner, clustering_ids_mx, num_cluster=4):
    for i in range (0, num_cluster):
        if(tunnel_owner in clustering_ids_mx[i]):
            return i

    return -1

def proposed_create_random_tunnel(lower, upper, num_tunnels, tunnel_len, tunnel_build_coefficient, clustering_ids_mx, clustering_permanents_ids_mx, num_cluster=4, num_permanent_per_cluster=5, type=0):
    tunnel_list = [[0 for x in range(tunnel_len + 2)] for y in range(num_tunnels)]
    random_tunnel_owners_list = select_random_list_from_range(lower, upper, num_tunnels)

    tunnel_index = 0
    for tunnel_owner in random_tunnel_owners_list:
        tunnel_list[tunnel_index][0] = tunnel_owner
        tunnel_participants_list = []
        if(type == 3):
            tunnel_order_index = 0
            owner_clustr_id = find_cluster_id(tunnel_owner, clustering_ids_mx, num_cluster)
            if(owner_clustr_id < 0):
                print('Error in finding cluster-id.')
                return
            first_participant = select_random_list_from_list(clustering_permanents_ids_mx[owner_clustr_id] ,1)[0] #select_random_list_from_range_with_exclude(lower, upper, tunnel_len, [tunnel_owner])
            tunnel_order_index += 1
            tunnel_list[tunnel_index][tunnel_order_index] = first_participant

            random_receiver_cluster_id = select_random_list_from_range_with_exclude(lower, num_cluster - 1, 1, [owner_clustr_id])[0]
            # print(random_receiver_cluster_id)
            random_receiver_id = select_random_list_from_list(clustering_ids_mx[random_receiver_cluster_id] ,1)[0]

            second_participant = select_random_list_from_list(clustering_permanents_ids_mx[random_receiver_cluster_id] ,1)[0]
            tunnel_order_index += 1
            tunnel_list[tunnel_index][tunnel_order_index] = second_participant

            third_participant = random_receiver_id
            tunnel_order_index += 1
            tunnel_list[tunnel_index][tunnel_order_index] = third_participant

        tunnel_list[tunnel_index][4] = 1
        tunnel_index += 1
    # print(tunnel_list)

    return tunnel_list

def i2p_create_random_tunnel(lower, upper, num_tunnels, tunnel_len, tunnel_build_coefficient, type=0):
    tunnel_list = [[0 for x in range(tunnel_len + 2)] for y in range(num_tunnels*2)]
    random_sender_tunnel_owners_list = select_random_list_from_range(lower, upper, num_tunnels)
    random_receiver_tunnel_owners_list = select_random_list_from_range(lower, upper, num_tunnels)
    active_receiver_tunnels = []

    # print(random_sender_tunnel_owners_list)
    # print(random_receiver_tunnel_owners_list)

    num_concurrent_build_tunnels = 0
    num_sender_concurrent_build_tunnels_idx_list = []
    num_sender_concurrent_build_tunnels_list = []
    num_receiver_concurrent_build_tunnels_idx_list = []
    num_receiver_concurrent_build_tunnels_list = []
    if(type == 2):
        num_concurrent_build_tunnels = int(tunnel_build_coefficient * num_tunnels)
        num_sender_concurrent_build_tunnels_idx_list = select_random_list_from_range(lower, num_tunnels, num_concurrent_build_tunnels)
        num_sender_concurrent_build_tunnels_list = [random_sender_tunnel_owners_list[i] for i in num_sender_concurrent_build_tunnels_idx_list]
        num_receiver_concurrent_build_tunnels_idx_list = select_random_list_from_range(lower, num_tunnels, num_concurrent_build_tunnels)
        num_receiver_concurrent_build_tunnels_list = [random_sender_tunnel_owners_list[i] for i in num_receiver_concurrent_build_tunnels_idx_list]

    tunnel_index = 0
    for tunnel_owner in random_sender_tunnel_owners_list:
        tunnel_list[tunnel_index][0] = tunnel_owner
        tunnel_participants_list = select_random_list_from_range_with_exclude(lower, upper, tunnel_len, [tunnel_owner])
        next_tunnel_id = select_random_list_from_list(random_receiver_tunnel_owners_list ,1)[0]
        active_receiver_tunnels.append(next_tunnel_id)
        tunnel_order_index = 0
        for tunnel_participant in tunnel_participants_list:
            tunnel_order_index += 1
            tunnel_list[tunnel_index][tunnel_order_index] = tunnel_participant
        
        if((tunnel_owner in num_sender_concurrent_build_tunnels_list) or type != 2):
            tunnel_list[tunnel_index][3] = 1
        else:
            tunnel_list[tunnel_index][3] = -1
        tunnel_index += 1
    # print(tunnel_list)

    for tunnel_owner in random_receiver_tunnel_owners_list:
        tunnel_list[tunnel_index][0] = tunnel_owner
        tunnel_participants_list = select_random_list_from_range_with_exclude(lower, upper, tunnel_len, [tunnel_owner])
        tunnel_order_index = 0
        for tunnel_participant in tunnel_participants_list:
            tunnel_order_index += 1
            tunnel_list[tunnel_index][tunnel_order_index] = tunnel_participant
        
        if((tunnel_owner in num_receiver_concurrent_build_tunnels_list) or type != 2):
            tunnel_list[tunnel_index][3] = 1
        else:
            tunnel_list[tunnel_index][3] = -1

        if(tunnel_owner not in active_receiver_tunnels):
            tunnel_list[tunnel_index][3] = -1

        tunnel_index += 1

    # print(tunnel_list)
    # del tunnel_list[tunnel_index:]
    # print(tunnel_list)

    return tunnel_list

def tor_create_random_tunnel(lower, upper, num_tunnels, tunnel_len, tunnel_build_coefficient, type=0, exit_node_proportion=1):
    tunnel_list = [[0 for x in range(tunnel_len + 2)] for y in range(num_tunnels)]
    random_tunnel_owners_list = select_random_list_from_range(lower, upper, num_tunnels)
    
    num_concurrent_build_tunnels = 0
    num_concurrent_build_tunnels_idx_list = []
    num_concurrent_build_tunnels_list = []
    if(type == 2):
        num_concurrent_build_tunnels = int(tunnel_build_coefficient * num_tunnels)
        num_concurrent_build_tunnels_idx_list = select_random_list_from_range(lower, num_tunnels, num_concurrent_build_tunnels)
        num_concurrent_build_tunnels_list = [random_tunnel_owners_list[i] for i in num_concurrent_build_tunnels_idx_list]

    tunnel_index = 0
    for tunnel_owner in random_tunnel_owners_list:
        tunnel_list[tunnel_index][0] = tunnel_owner
        tunnel_participants_list = select_random_list_from_range_with_exclude(lower, upper, tunnel_len-1, [tunnel_owner])
        tunnel_order_index = 0
        for tunnel_participant in tunnel_participants_list:
            tunnel_order_index += 1
            tunnel_list[tunnel_index][tunnel_order_index] = tunnel_participant
        
        exit_upper_restricted = ceil(upper * exit_node_proportion)
        tunnel_order_index += 1
        tunnel_list[tunnel_index][tunnel_order_index] = select_random_list_from_range_with_exclude(lower, exit_upper_restricted, 1, [tunnel_owner])[0]

        if((tunnel_owner in num_concurrent_build_tunnels_list) or type != 2):
            tunnel_list[tunnel_index][4] = 1
        else:
            tunnel_list[tunnel_index][4] = -1
        tunnel_index += 1
    # print(tunnel_list)

    return tunnel_list

def generate_random_traffic(tunnel_list_mx, traffic_gen_coefficient, num_active_tunnels):
    t_tunnel_list_mx = list(map(list, zip(*tunnel_list_mx)))
    tunnel_owners = t_tunnel_list_mx[0]
    upper = len(t_tunnel_list_mx[0])
    lower = 0
    random_active_tunnel_idx_list = select_random_list_from_range(lower, upper, num_active_tunnels)
    random_tunnel_traffic_list = [tunnel_list_mx[i] for i in random_active_tunnel_idx_list]

    return random_tunnel_traffic_list


def find_shared_tunnels(lower, upper, num_tunnels, tunnel_len, type=0, traffic_gen_coefficient=1, tunnel_build_coefficient=1, num_cluster=4, num_permanent_per_cluster=5):
    t_list_mx = []
    tunnel_list_mx = []
    num_list = 0

    if(type == 3):
        clustering_ids_mx, clustering_permanents_ids_mx = create_clustering(num_cluster, lower, upper, num_permanent_per_cluster)
        # print(clustering_permanents_ids_mx) 
        # print(clustering_ids_mx)
        tunnel_list_mx = proposed_create_random_tunnel(lower, upper, num_tunnels, tunnel_len, tunnel_build_coefficient, 
                                            clustering_ids_mx, clustering_permanents_ids_mx, num_cluster, num_permanent_per_cluster, type)
    else:
        tunnel_list_mx = create_random_tunnel(lower, upper, num_tunnels, tunnel_len, tunnel_build_coefficient, type)

    if(type == 1 or type == 2 or type == 3):
        num_active_tunnels = int(traffic_gen_coefficient * num_tunnels)
        active_tunnel_list_mx = generate_random_traffic(tunnel_list_mx, traffic_gen_coefficient, num_active_tunnels)
        t_active_tunnel_list_mx = list(map(list, zip(*active_tunnel_list_mx)))
        t_list_mx = t_active_tunnel_list_mx
        num_list = num_active_tunnels
    else:
        t_tunnel_list_mx = list(map(list, zip(*tunnel_list_mx)))
        t_list_mx = t_tunnel_list_mx
        num_list = num_tunnels

    tunnels_with_shared_id_list = set()
    # print(t_list_mx)

    # print(t_list_mx)
    for i in range (1, tunnel_len + 1):
        tunnel_loc_set = set(t_list_mx[i])
        if(len(tunnel_loc_set) < num_list):
            dup_ids = [item for item, count in collections.Counter(t_list_mx[i]).items() if count > 1]
            for j in range (0, num_list):
                if((t_list_mx[i][j] in dup_ids) and (t_list_mx[4][j] == 1)):
                    # tunnels_with_shared_id_list.add(t_list_mx[0][j])
                    for k in range (0, num_list):
                        if((t_list_mx[i][j] == t_list_mx[i][k]) and (j != k) and (t_list_mx[4][k] == 1)):
                            # print(str(num_tunnels) + '--' + str(j) + ': ' + str(t_list_mx[i][j]))
                            tunnels_with_shared_id_list.add(t_list_mx[0][j])
                            break

    num_shared = len(tunnels_with_shared_id_list)
    return num_shared

def eq_shannon_entropy(num):
    probs = [(1/num) for x in range(num)]
    ent = 0.
    base = 2
    # max_en = log(len(probs), base)
    # min_en = 0
    # print('[' + str(min_en) + ', ' + str(max_en) + ']')
    for i in probs:
        if(i != 0):
            ent -= i * log(i, base)

    # print(ent)
    return ent

def calc_entropy(lower, upper, num_tunnels, tunnel_len, type=0, traffic_gen_coefficient=1, tunnel_build_coefficient=1, num_cluster=4, num_permanent_per_cluster=5):
    t_list_mx = []
    tunnel_list_mx = []
    num_list = 0

    if(type == 3):
        clustering_ids_mx, clustering_permanents_ids_mx = create_clustering(num_cluster, lower, upper, num_permanent_per_cluster)
        # print(clustering_permanents_ids_mx) 
        # print(clustering_ids_mx)
        tunnel_list_mx = proposed_create_random_tunnel(lower, upper, num_tunnels, tunnel_len, tunnel_build_coefficient, 
                                            clustering_ids_mx, clustering_permanents_ids_mx, num_cluster, num_permanent_per_cluster, type)
    else:
        tunnel_list_mx = create_random_tunnel(lower, upper, num_tunnels, tunnel_len, tunnel_build_coefficient, type)

    if(type == 1 or type == 2 or type == 3):
        num_active_tunnels = int(traffic_gen_coefficient * num_tunnels)
        active_tunnel_list_mx = generate_random_traffic(tunnel_list_mx, traffic_gen_coefficient, num_active_tunnels)
        t_active_tunnel_list_mx = list(map(list, zip(*active_tunnel_list_mx)))
        t_list_mx = t_active_tunnel_list_mx
        num_list = num_active_tunnels   
    else:
        t_tunnel_list_mx = list(map(list, zip(*tunnel_list_mx)))
        t_list_mx = t_tunnel_list_mx
        num_list = num_tunnels

    tunnels_with_shared_id_list = set()

    entropy = []
    num_shared_list = [[0 for x in range(num_tunnels)] for y in range(tunnel_len + 2)]
    num_shared_list[0] = t_list_mx[0]
    num_shared_list[tunnel_len + 1] = [1 for y in range(num_tunnels)]
    shared_list = [[[] for x in range(tunnel_len)] for y in range(num_tunnels)]

    for i in range (1, tunnel_len + 1):
        tunnel_loc_set = set(t_list_mx[i])
        if(len(tunnel_loc_set) < num_list):
            dup_ids = [item for item, count in collections.Counter(t_list_mx[i]).items() if count > 1]
            for j in range (0, num_list):
                pushed = False
                if((t_list_mx[i][j] in dup_ids) and (t_list_mx[4][j] == 1)):
                    # tunnels_with_shared_id_list.add(t_list_mx[0][j])
                    num_share_id = 1
                    for k in range (0, num_list):
                        if((t_list_mx[i][j] == t_list_mx[i][k]) and (j != k) and (t_list_mx[4][k] == 1)):
                            num_share_id += 1
                            shared_list[j][i-1].append(k)
                        
                    if(num_share_id > 1):
                        num_shared_list[i][j] = num_share_id
                        if(num_share_id > 0):
                            num_shared_list[tunnel_len + 1][j] *= num_share_id
                        pushed = True              
                # if(not pushed):
                #     # probs.push(0)
                #     entropy.append(0)

    max_num_shared_list = [[1 for x in range(num_tunnels)] for y in range(tunnel_len + 1)]
    num_shared_list[0] = t_list_mx[0]
    num_shared_list[tunnel_len + 1] = [1 for y in range(num_tunnels)]

    for i in range (0, num_tunnels):
        if(num_shared_list[3][i] > max_num_shared_list[3][i]):
            max_num_shared_list[3][i] = num_shared_list[3][i]
    
    for i in range (0, num_tunnels):
        if(num_shared_list[2][i] > max_num_shared_list[2][i]):
            max_num_shared_list[2][i] = num_shared_list[2][i]
        max_num_shared_list[2][i] *= max_num_shared_list[3][i]

    for i in range (0, num_tunnels):
        for item in shared_list[i][1]:
            if(max_num_shared_list[2][item] > max_num_shared_list[2][i]): 
                max_num_shared_list[2][i] = num_shared_list[2][item]

    for i in range (0, num_tunnels):
        if(num_shared_list[1][i] > max_num_shared_list[1][i]):
            max_num_shared_list[1][i] = num_shared_list[1][i]
        max_num_shared_list[1][i] *= max_num_shared_list[2][i]

    for i in range (0, num_tunnels):
        for item in shared_list[i][0]:
            if(max_num_shared_list[1][item] > max_num_shared_list[1][i]): 
                max_num_shared_list[1][i] = num_shared_list[1][item]

        max_num_shared_list[0][i] = max_num_shared_list[1][i]

    for i in range (0, num_tunnels):
        ent = eq_shannon_entropy(max_num_shared_list[0][i])
        entropy.append(ent)

    # print(entropy)
    entropy_avg = 0
    scaled_entropy_avg = 0
    if(len(entropy) > 0):
        entropy_avg = sum(entropy)/len(entropy)
        scaled_entropy_avg = entropy_avg/log(len(entropy), 2)
    return scaled_entropy_avg


def i2p_calc_entropy(lower, upper, num_tunnels, tunnel_len, type=0, traffic_gen_coefficient=1, tunnel_build_coefficient=1):
    t_list_mx = []
    tunnel_list_mx = []
    num_list = 0

    tunnel_list_mx = i2p_create_random_tunnel(lower, upper, num_tunnels, tunnel_len, tunnel_build_coefficient, type)

    if(type == 1 or type == 2):
        num_active_tunnels = int(2 * traffic_gen_coefficient * num_tunnels)
        active_tunnel_list_mx = generate_random_traffic(tunnel_list_mx, traffic_gen_coefficient, num_active_tunnels)
        t_active_tunnel_list_mx = list(map(list, zip(*active_tunnel_list_mx)))
        t_list_mx = t_active_tunnel_list_mx
        num_list = num_active_tunnels   
    else:
        t_tunnel_list_mx = list(map(list, zip(*tunnel_list_mx)))
        t_list_mx = t_tunnel_list_mx
        num_list = 2 * num_tunnels

    # print(t_list_mx)
    tunnels_with_shared_id_list = set()

    entropy = []
    num_shared_list = [[0 for x in range(2 * num_tunnels)] for y in range(tunnel_len + 2)]
    num_shared_list[0] = t_list_mx[0]
    num_shared_list[tunnel_len + 1] = [1 for y in range(2 * num_tunnels)]
    shared_list = [[[] for x in range(tunnel_len)] for y in range(2 * num_tunnels)]

    for i in range (1, tunnel_len + 1):
        tunnel_loc_set = set(t_list_mx[i])
        if(len(tunnel_loc_set) < num_list):
            dup_ids = [item for item, count in collections.Counter(t_list_mx[i]).items() if count > 1]
            for j in range (0, num_list):
                pushed = False
                if((t_list_mx[i][j] in dup_ids) and (t_list_mx[3][j] == 1)):
                    # tunnels_with_shared_id_list.add(t_list_mx[0][j])
                    num_share_id = 1
                    for k in range (0, num_list):
                        if((t_list_mx[i][j] == t_list_mx[i][k]) and (j != k) and (t_list_mx[3][k] == 1)):
                            num_share_id += 1
                            shared_list[j][i-1].append(k)
                        
                    if(num_share_id > 1):
                        num_shared_list[i][j] = num_share_id
                        if(num_share_id > 0):
                            num_shared_list[tunnel_len + 1][j] *= num_share_id
                        pushed = True              
                # if(not pushed):
                #     # probs.push(0)
                #     entropy.append(0)

    max_num_shared_list = [[1 for x in range(2 * num_tunnels)] for y in range(tunnel_len + 1)]
    num_shared_list[0] = t_list_mx[0]
    num_shared_list[tunnel_len + 1] = [1 for y in range(2 * num_tunnels)]

    # for i in range (0, 2 * num_tunnels):
    #     if(num_shared_list[3][i] > max_num_shared_list[3][i]):
    #         max_num_shared_list[3][i] = num_shared_list[3][i]
    
    for i in range (0, 2 * num_tunnels):
        if(num_shared_list[2][i] > max_num_shared_list[2][i]):
            max_num_shared_list[2][i] = num_shared_list[2][i]
        # max_num_shared_list[2][i] *= max_num_shared_list[3][i]

    for i in range (0, 2 * num_tunnels):
        for item in shared_list[i][1]:
            if(max_num_shared_list[2][item] > max_num_shared_list[2][i]): 
                max_num_shared_list[2][i] = num_shared_list[2][item]

    for i in range (0, 2 * num_tunnels):
        if(num_shared_list[1][i] > max_num_shared_list[1][i]):
            max_num_shared_list[1][i] = num_shared_list[1][i]
        max_num_shared_list[1][i] *= max_num_shared_list[2][i]

    for i in range (0, 2 * num_tunnels):
        for item in shared_list[i][0]:
            if(max_num_shared_list[1][item] > max_num_shared_list[1][i]): 
                max_num_shared_list[1][i] = num_shared_list[1][item]

        max_num_shared_list[0][i] = max_num_shared_list[1][i]

    for i in range (0, 2 * num_tunnels):
        ent = eq_shannon_entropy(max_num_shared_list[0][i])
        entropy.append(ent)

    # print(entropy)
    entropy_avg = 0
    scaled_entropy_avg = 0
    if(len(entropy) > 0):
        entropy_avg = sum(entropy)/len(entropy)
        scaled_entropy_avg = entropy_avg/log(len(entropy), 2)
    return scaled_entropy_avg

def tor_calc_entropy(lower, upper, num_tunnels, tunnel_len, type=0, traffic_gen_coefficient=1, tunnel_build_coefficient=1, exit_node_proportion=1):
    t_list_mx = []
    tunnel_list_mx = []
    num_list = 0

    tunnel_list_mx = tor_create_random_tunnel(lower, upper, num_tunnels, tunnel_len, tunnel_build_coefficient, type, exit_node_proportion)

    if(type == 1 or type == 2):
        num_active_tunnels = int(traffic_gen_coefficient * num_tunnels)
        active_tunnel_list_mx = generate_random_traffic(tunnel_list_mx, traffic_gen_coefficient, num_active_tunnels)
        t_active_tunnel_list_mx = list(map(list, zip(*active_tunnel_list_mx)))
        t_list_mx = t_active_tunnel_list_mx
        num_list = num_active_tunnels   
    else:
        t_tunnel_list_mx = list(map(list, zip(*tunnel_list_mx)))
        t_list_mx = t_tunnel_list_mx
        num_list = num_tunnels

    tunnels_with_shared_id_list = set()

    entropy = []
    num_shared_list = [[0 for x in range(num_tunnels)] for y in range(tunnel_len + 2)]
    num_shared_list[0] = t_list_mx[0]
    num_shared_list[tunnel_len + 1] = [1 for y in range(num_tunnels)]
    shared_list = [[[] for x in range(tunnel_len)] for y in range(num_tunnels)]

    for i in range (1, tunnel_len + 1):
        tunnel_loc_set = set(t_list_mx[i])
        if(len(tunnel_loc_set) < num_list):
            dup_ids = [item for item, count in collections.Counter(t_list_mx[i]).items() if count > 1]
            for j in range (0, num_list):
                pushed = False
                if((t_list_mx[i][j] in dup_ids) and (t_list_mx[4][j] == 1)):
                    # tunnels_with_shared_id_list.add(t_list_mx[0][j])
                    num_share_id = 1
                    for k in range (0, num_list):
                        if((t_list_mx[i][j] == t_list_mx[i][k]) and (j != k) and (t_list_mx[4][k] == 1)):
                            num_share_id += 1
                            shared_list[j][i-1].append(k)
                        
                    if(num_share_id > 1):
                        num_shared_list[i][j] = num_share_id
                        if(num_share_id > 0):
                            num_shared_list[tunnel_len + 1][j] *= num_share_id
                        pushed = True              
                # if(not pushed):
                #     # probs.push(0)
                #     entropy.append(0)

    max_num_shared_list = [[1 for x in range(num_tunnels)] for y in range(tunnel_len + 1)]
    num_shared_list[0] = t_list_mx[0]
    num_shared_list[tunnel_len + 1] = [1 for y in range(num_tunnels)]

    for i in range (0, num_tunnels):
        if(num_shared_list[3][i] > max_num_shared_list[3][i]):
            max_num_shared_list[3][i] = num_shared_list[3][i]
    
    for i in range (0, num_tunnels):
        if(num_shared_list[2][i] > max_num_shared_list[2][i]):
            max_num_shared_list[2][i] = num_shared_list[2][i]
        max_num_shared_list[2][i] *= max_num_shared_list[3][i]

    for i in range (0, num_tunnels):
        for item in shared_list[i][1]:
            if(max_num_shared_list[2][item] > max_num_shared_list[2][i]): 
                max_num_shared_list[2][i] = num_shared_list[2][item]

    for i in range (0, num_tunnels):
        if(num_shared_list[1][i] > max_num_shared_list[1][i]):
            max_num_shared_list[1][i] = num_shared_list[1][i]
        max_num_shared_list[1][i] *= max_num_shared_list[2][i]

    for i in range (0, num_tunnels):
        for item in shared_list[i][0]:
            if(max_num_shared_list[1][item] > max_num_shared_list[1][i]): 
                max_num_shared_list[1][i] = num_shared_list[1][item]

        max_num_shared_list[0][i] = max_num_shared_list[1][i]

    for i in range (0, num_tunnels):
        ent = eq_shannon_entropy(max_num_shared_list[0][i])
        entropy.append(ent)

    # print(entropy)
    entropy_avg = 0
    scaled_entropy_avg = 0
    if(len(entropy) > 0):
        entropy_avg = sum(entropy)/len(entropy)
        scaled_entropy_avg = entropy_avg/log(len(entropy), 2)
    return scaled_entropy_avg

def test_traffic_seperation(test_step, num_iter, lower, upper, tunnel_len, type=0, traffic_gen_coefficient=1, tunnel_build_coefficient=1, num_cluster=4, num_permanent_per_cluster=5):
    test_result = {}
    for i in range(test_step, num_iter * test_step + 1, test_step):
        # result = find_shared_tunnels(lower, upper, i, tunnel_len, type, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)
        result = calc_entropy(lower, upper, i, tunnel_len, type, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

        test_result[i] = result
    return test_result

def simulate(test_1_repeat, test_1_step, test_1_num_iter, lower, number_of_ids, tunnel_length, type, 
                calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster):
    test_result_sum = {}
    test_result_avg = {}
    test_1_results = [0 for x in range(test_1_repeat)]
    for i in range(0, test_1_repeat):
        test_1_results[i] = test_traffic_seperation(test_1_step, test_1_num_iter, lower, number_of_ids, tunnel_length, 
                                                    type, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)
    for i in range(0, test_1_repeat):
        for key, value in test_1_results[i].items():
            if(key not in test_result_sum):
                test_result_sum[key] = 0
            test_result_sum[key] += value

    if(not calc_entropy_flag):
        for key, value in test_result_sum.items():
            # test_result_avg[key] = value / test_1_repeat
            if(type == 1 or type == 2 or type == 3):
                test_result_avg[key] = value / (test_1_repeat * int(key*traffic_gen_coefficient))
            else:
                test_result_avg[key] = value / (test_1_repeat * key)
    else:
        for key, value in test_result_sum.items():
            test_result_avg[key] = value / (test_1_repeat)

    # print(test_result_sum)
    # print(test_result_avg)
    # create_csv('mycsvfile.csv', test_result_avg)
    return test_result_avg, test_1_results
    
    # test_result_list = object_to_list(test_result_avg)
    # draw_plot(test_result_list[0], test_result_list[1])

# test: 1
# proposed_structure
# pr: {5, 10, 15, 20, 25, 30, 35, 40, 45, 50}
def proposed_with_different_pr():
    ### Fix Params ###
    type = 3
    test_1_step = 10
    test_1_num_iter = 10
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    traffic_gen_coefficient = 1   # (0, 1]
    tunnel_build_coefficient = 0.5  # (0, 1]
    num_cluster = 4
    ################

    num_permanent_per_cluster = 5
    test_result_avg = {}
    test_result_avg1, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

    test_result_avg[0] = []
    test_result_avg[0].append('#' + str(num_permanent_per_cluster))
    for key, value in test_result_avg1.items():
        if(key > 0):
            test_result_avg[key] = []
            test_result_avg[key].append(value) 

    for i in range (2,11):
        num_permanent_per_cluster = i * 5
        test_result_avg2, test_result_set1 = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

        # print(test_result_avg2)
        test_result_avg[0].append('#' + str(num_permanent_per_cluster))
        for key, value in test_result_avg2.items():
            if(key > 0):
                test_result_avg[key].append(value) 
                
        write_to_excel_file(test_result_set1, 'Proposed_PR_Impact_' + str(i))

    create_csv('test_num_pr.csv', test_result_avg)

# test: 2
# proposed_structure
# pr: {1, 2, 3, 4, 5}
def proposed_with_different_pr_small_set():
    ### Fix Params ###
    type = 3
    test_1_step = 10
    test_1_num_iter = 10
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    traffic_gen_coefficient = 1   # (0, 1]
    tunnel_build_coefficient = 0.5  # (0, 1]
    num_cluster = 4
    ################

    num_permanent_per_cluster = 1
    test_result_avg = {}
    test_result_avg1, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

    test_result_avg[0] = []
    test_result_avg[0].append('#' + str(num_permanent_per_cluster))
    for key, value in test_result_avg1.items():
        if(key > 0):
            test_result_avg[key] = []
            test_result_avg[key].append(value) 

    for i in range (2,6):
        num_permanent_per_cluster = i
        test_result_avg2, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

        # print(test_result_avg2)
        test_result_avg[0].append('#' + str(num_permanent_per_cluster))
        for key, value in test_result_avg2.items():
            if(key > 0):
                test_result_avg[key].append(value) 

    create_csv('test_num_pr_small_set.csv', test_result_avg)

# test: 3
# proposed_structure
# traffic_gen_coefficient: {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1}
def proposed_with_different_traffic_coefficient():
    ### Fix Params ###
    type = 3
    test_1_step = 10
    test_1_num_iter = 10
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    tunnel_build_coefficient = 0.5  # (0, 1]
    num_cluster = 4
    num_permanent_per_cluster = 5
    ################

    traffic_gen_coefficient = 0.1   # (0, 1]

    test_result_avg = {}
    test_result_avg1, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

    test_result_avg[0] = []
    test_result_avg[0].append('#' + str(traffic_gen_coefficient))
    for key, value in test_result_avg1.items():
        if(key > 0):
            test_result_avg[key] = []
            test_result_avg[key].append(value) 

    for i in range (2,11):
        traffic_gen_coefficient = i * 0.1
        test_result_avg2, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

        # print(test_result_avg2)
        test_result_avg[0].append('#' + str(traffic_gen_coefficient))
        for key, value in test_result_avg2.items():
            if(key > 0):
                test_result_avg[key].append(value) 

    create_csv('test_proposed_with_traffic_rate.csv', test_result_avg)

# test: 4
# proposed_structure
# cluster: {2, 4, 6, 8, 10, 12, 14, 16, 18, 20}
def proposed_with_different_cluster():
    ### Fix Params ###
    type = 3
    test_1_step = 10
    test_1_num_iter = 10
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    traffic_gen_coefficient = 1   # (0, 1]
    tunnel_build_coefficient = 0.5  # (0, 1]
    num_permanent_per_cluster = 5
    ################

    num_cluster = 2

    test_result_avg = {}
    test_result_avg1, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

    test_result_avg[0] = []
    test_result_avg[0].append('#' + str(num_cluster))
    for key, value in test_result_avg1.items():
        if(key > 0):
            test_result_avg[key] = []
            test_result_avg[key].append(value) 

    for i in range (2,11):
        num_cluster = i * 2
        test_result_avg2, test_result_set1 = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

        # print(test_result_avg2)
        test_result_avg[0].append('#' + str(num_cluster))
        for key, value in test_result_avg2.items():
            if(key > 0):
                test_result_avg[key].append(value) 
                
        write_to_excel_file(test_result_set1, 'Proposed_Cluster_Impact_' + str(i))

    create_csv('test_num_cluster.csv', test_result_avg)

# test: 5
# type_one
# traffic_gen_coefficient: {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1}
def type_one_with_different_traffic_coefficient():
    ### Fix Params ###
    type = 1
    test_1_step = 10
    test_1_num_iter = 10
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    tunnel_build_coefficient = 0.5  # (0, 1]
    num_cluster = 4
    num_permanent_per_cluster = 5
    ################

    traffic_gen_coefficient = 0.1   # (0, 1]

    test_result_avg = {}
    test_result_avg1, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

    test_result_avg[0] = []
    test_result_avg[0].append('#' + str(traffic_gen_coefficient))
    for key, value in test_result_avg1.items():
        if(key > 0):
            test_result_avg[key] = []
            test_result_avg[key].append(value) 

    for i in range (2,11):
        traffic_gen_coefficient = i * 0.1
        test_result_avg2, test_result_set1 = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

        # print(test_result_avg2)
        test_result_avg[0].append('#' + str(traffic_gen_coefficient))
        for key, value in test_result_avg2.items():
            if(key > 0):
                test_result_avg[key].append(value) 
                
        write_to_excel_file(test_result_set1, 'Type_One_ACT_' + str(i))

    create_csv('type_one_with_traffic_rate.csv', test_result_avg)

# test: 6
# type_two
# tunnel_build_coefficient: 0.5
# traffic_gen_coefficient: {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1}
def type_two_with_different_traffic_coefficient():
    ### Fix Params ###
    type = 2
    test_1_step = 10
    test_1_num_iter = 10
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    tunnel_build_coefficient = 0.5  # (0, 1]
    num_cluster = 4
    num_permanent_per_cluster = 5
    ################

    traffic_gen_coefficient = 0.1   # (0, 1]

    test_result_avg = {}
    test_result_avg1, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

    test_result_avg[0] = []
    test_result_avg[0].append('#' + str(traffic_gen_coefficient))
    for key, value in test_result_avg1.items():
        if(key > 0):
            test_result_avg[key] = []
            test_result_avg[key].append(value) 

    for i in range (2,11):
        traffic_gen_coefficient = i * 0.1
        test_result_avg2, test_result_set1 = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

        # print(test_result_avg2)
        test_result_avg[0].append('#' + str(traffic_gen_coefficient))
        for key, value in test_result_avg2.items():
            if(key > 0):
                test_result_avg[key].append(value) 
                
        write_to_excel_file(test_result_set1, 'Type_Two_ACT_' + str(i))

    create_csv('type_two_with_traffic_rate.csv', test_result_avg)

# test: 7
# type_two
# tunnel_build_coefficient: {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1}
# traffic_gen_coefficient: 0.5
def type_two_with_different_tunnel_build_coefficient():
    ### Fix Params ###
    type = 2
    test_1_step = 10
    test_1_num_iter = 10
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    traffic_gen_coefficient = 0.5   # (0, 1]
    num_cluster = 4
    num_permanent_per_cluster = 5
    ################

    tunnel_build_coefficient = 0.1  # (0, 1]
    test_result_avg = {}
    test_result_avg1, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

    test_result_avg[0] = []
    test_result_avg[0].append('#' + str(tunnel_build_coefficient))
    for key, value in test_result_avg1.items():
        if(key > 0):
            test_result_avg[key] = []
            test_result_avg[key].append(value) 

    for i in range (2,11):
        tunnel_build_coefficient = i * 0.1
        test_result_avg2, test_result_set1 = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

        # print(test_result_avg2)
        test_result_avg[0].append('#' + str(tunnel_build_coefficient))
        for key, value in test_result_avg2.items():
            if(key > 0):
                test_result_avg[key].append(value) 
                
        write_to_excel_file(test_result_set1, 'Type_Two_TBC_' + str(i))

    create_csv('type_two_with_tunnel_build_rate.csv', test_result_avg)

# test: 8
# type_zero
def type_zero():
    ### Fix Params ###
    type = 0
    test_1_step = 10
    test_1_num_iter = 10
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    traffic_gen_coefficient = 0.5   # (0, 1]
    tunnel_build_coefficient = 0.5  # (0, 1]
    num_cluster = 4
    num_permanent_per_cluster = 5
    ################

    test_result_avg = {}
    test_result_avg1, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

    test_result_avg[0] = []
    test_result_avg[0].append('basic')
    for key, value in test_result_avg1.items():
        if(key > 0):
            test_result_avg[key] = []
            test_result_avg[key].append(value) 

    create_csv('type_zero.csv', test_result_avg)

# test: 9
# comp_wit_rate
def comp_wit_rate():
    ### Fix Params ###
    test_1_step = 50
    test_1_num_iter = 1
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 50
    tunnel_length = 3
    calc_entropy_flag = True

    tunnel_build_coefficient = 0.5  # (0, 1]
    num_cluster = 4
    num_permanent_per_cluster = 5
    ################

    type = 0
    traffic_gen_coefficient = 0.1   # (0, 1]

    test_result_avg = {}
    test_result_avg[0] = [] 

    for t in range(1, 4):
        type = t
        test_result_avg[str(type)] = []
        for r in range(1, 11):
            traffic_gen_coefficient = r * 0.1
            test_result_avg1, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)
            if(type == 1):
                test_result_avg[0].append('#' + str(traffic_gen_coefficient))

            test_result_avg[str(type)].append(test_result_avg1[50]) 


    create_csv('comp_with_rate.csv', test_result_avg)

# test: 10
# comp_wit_number_of_tunnels
def comp_wit_number_of_tunnels():
    ### Fix Params ###
    test_1_step = 10
    test_1_num_iter = 10
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    traffic_gen_coefficient = 0.5   # (0, 1]
    num_cluster = 4
    ################

    type = 0
    tunnel_build_coefficient = 0.5  # (0, 1]
    num_permanent_per_cluster = 5

    tunnel_build_coefficient_list = [0.1, 0.5, 1]
    num_permanent_per_cluster_list = [25, 10, 5, 1]

    test_result_avg = {}
    test_result_avg[0] = [] 

    type = 2
    for r in tunnel_build_coefficient_list:
        tunnel_build_coefficient = r
        test_result_avg1, test_result_set1 = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

        test_result_avg[0].append('#TBC_' + str(tunnel_build_coefficient))
        for key, value in test_result_avg1.items():
            if(key > 0):
                if not(key in test_result_avg):
                    test_result_avg[key] = []
                test_result_avg[key].append(value) 
                
        write_to_excel_file(test_result_set1, 'Com_Tunnel_' + str(r))

    type = 3
    tunnel_build_coefficient = 1
    for r in num_permanent_per_cluster_list:
        num_permanent_per_cluster = r
        test_result_avg1, test_result_set1 = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

        test_result_avg[0].append('#PPC_' + str(num_permanent_per_cluster))
        for key, value in test_result_avg1.items():
            if(key > 0):
                test_result_avg[key].append(value) 
                
        write_to_excel_file(test_result_set1, 'Com_Proposed_' + str(r))

    create_csv('comp_wit_number_of_tunnels.csv', test_result_avg)



def evaluate_i2p(test_step, test_num_iter, num_ids, tunnel_len, type, traffic_gen_coefficient, tunnel_build_coefficient):
    test_result = {}
    for i in range(test_step, test_num_iter * test_step + 1, test_step):
        result = i2p_calc_entropy(0, num_ids, i, tunnel_len, type, traffic_gen_coefficient, tunnel_build_coefficient)
        test_result[i] = result
    return test_result

def simulate_i2P(test_repeat, test_step, test_num_iter, num_ids, tunnel_len, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient):
    test_result_sum = {}
    test_result_avg = {}
    test_results = [0 for x in range(test_repeat)]
    for i in range(0, test_repeat):
        test_results[i] = evaluate_i2p(test_step, test_num_iter, num_ids, tunnel_len, type, traffic_gen_coefficient, tunnel_build_coefficient)

    for i in range(0, test_repeat):
        for key, value in test_results[i].items():
            if(key not in test_result_sum):
                test_result_sum[key] = 0
            test_result_sum[key] += value

    if(not calc_entropy_flag):
        for key, value in test_result_sum.items():
            # test_result_avg[key] = value / test_1_repeat
            if(type == 1 or type == 2):
                test_result_avg[key] = value / (test_repeat * int(key*traffic_gen_coefficient))
            else:
                test_result_avg[key] = value / (test_repeat * key)
    else:
        for key, value in test_result_sum.items():
            test_result_avg[key] = value / (test_repeat)

    # print(test_result_sum)
    # print(test_result_avg)
    # create_csv('mycsvfile.csv', test_result_avg)
    return test_result_avg, test_results

# test: 11
def test_i2P_1():
    ### Fix Params ###
    type = 2
    test_1_step = 10
    test_1_num_iter = 10
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 2
    calc_entropy_flag = True

    traffic_gen_coefficient = 0.5  # (0, 1]
    tunnel_build_coefficient = 0.5  # (0, 1]
    ################

    test_result_avg = {}
    test_result_avg[0] = [] 

    test_result_avg1, _ = simulate_i2P(test_1_repeat, test_1_step, test_1_num_iter, number_of_ids, tunnel_length, type, 
                                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient)
    print(test_result_avg1)

def evaluate_tor(test_step, test_num_iter, num_ids, tunnel_len, type, traffic_gen_coefficient, tunnel_build_coefficient, exit_node_proportion):
    test_result = {}
    for i in range(test_step, test_num_iter * test_step + 1, test_step):
        result = tor_calc_entropy(0, num_ids, i, tunnel_len, type, traffic_gen_coefficient, tunnel_build_coefficient, exit_node_proportion)
        test_result[i] = result
    return test_result

def simulate_tor(test_repeat, test_step, test_num_iter, num_ids, tunnel_len, type, 
                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, exit_node_proportion):
    test_result_sum = {}
    test_result_avg = {}
    test_results = [0 for x in range(test_repeat)]
    for i in range(0, test_repeat):
        test_results[i] = evaluate_tor(test_step, test_num_iter, num_ids, tunnel_len, type, traffic_gen_coefficient, tunnel_build_coefficient, exit_node_proportion)

    for i in range(0, test_repeat):
        for key, value in test_results[i].items():
            if(key not in test_result_sum):
                test_result_sum[key] = 0
            test_result_sum[key] += value

    if(not calc_entropy_flag):
        for key, value in test_result_sum.items():
            # test_result_avg[key] = value / test_1_repeat
            if(type == 1 or type == 2):
                test_result_avg[key] = value / (test_repeat * int(key*traffic_gen_coefficient))
            else:
                test_result_avg[key] = value / (test_repeat * key)
    else:
        for key, value in test_result_sum.items():
            test_result_avg[key] = value / (test_repeat)

    # print(test_result_sum)
    # print(test_result_avg)
    # create_csv('mycsvfile.csv', test_result_avg)
    return test_result_avg, test_results

# test: 12
def test_tor_1():
    ### Fix Params ###
    type = 2
    test_1_step = 10
    test_1_num_iter = 10
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    traffic_gen_coefficient = 0.5  # (0, 1]
    tunnel_build_coefficient = 0.5  # (0, 1]
    exit_node_proportion = 0.5 # (0, 1]
    ################

    test_result_avg = {}
    test_result_avg[0] = [] 

    test_result_avg1, _ = simulate_tor(test_1_repeat, test_1_step, test_1_num_iter, number_of_ids, tunnel_length, type, 
                                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, exit_node_proportion)
    print(test_result_avg1)


# test: 13
# comp_with_tor_and_i2p
def comp_with_tor_and_i2p_by_number_of_tunnels():
    ### Fix Params ###
    test_1_step = 10
    test_1_num_iter = 10
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    traffic_gen_coefficient = 0.5   # (0, 1]
    num_cluster = 4
    ################

    type = 0
    tunnel_build_coefficient = 0.5  # (0, 1]
    exit_node_proportion = 0.5  # (0, 1]
    num_permanent_per_cluster = 5

    tunnel_build_coefficient_list = [0.1, 0.5, 1]
    tor_exit_node_proportion_list = [0.1, 0.5, 1]
    num_permanent_per_cluster_list = [25, 10, 5, 1]

    test_result_avg = {}
    test_result_avg[0] = [] 

    type = 2
    for r in tunnel_build_coefficient_list:
        tunnel_build_coefficient = r
        test_result_avg1, test_result_set1 = simulate_i2P(test_1_repeat, test_1_step, test_1_num_iter, number_of_ids, tunnel_length, type, 
                                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient)

        test_result_avg[0].append('#I2P_TBC_' + str(tunnel_build_coefficient))
        for key, value in test_result_avg1.items():
            if(key > 0):
                if not(key in test_result_avg):
                    test_result_avg[key] = []
                test_result_avg[key].append(value) 

        write_to_excel_file(test_result_set1, 'Com_I2P_' + str(r))
    
    for r in tunnel_build_coefficient_list:
        tunnel_build_coefficient = r
        for e in tor_exit_node_proportion_list:
            exit_node_proportion = e
            test_result_avg1, test_result_set1 = simulate_tor(test_1_repeat, test_1_step, test_1_num_iter, number_of_ids, tunnel_length, type, 
                                    calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, exit_node_proportion)

            test_result_avg[0].append('#Tor_TBC_' + str(tunnel_build_coefficient) + '_ENP_' + str(exit_node_proportion))
            for key, value in test_result_avg1.items():
                if(key > 0):
                    test_result_avg[key].append(value) 

        write_to_excel_file(test_result_set1, 'Com_TOR_' + str(r))
    
    type = 3
    tunnel_build_coefficient = 1
    for r in num_permanent_per_cluster_list:
        num_permanent_per_cluster = r
        test_result_avg1, test_result_set1 = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

        test_result_avg[0].append('#Proposed_PPC_' + str(num_permanent_per_cluster))
        for key, value in test_result_avg1.items():
            if(key > 0):
                test_result_avg[key].append(value) 

        write_to_excel_file(test_result_set1, 'Com_Proposed_' + str(r))
        
    create_csv('comp_with_tor_and_i2p_by_number_of_tunnels.csv', test_result_avg)

# test: 14
# type_two
# tunnel_build_coefficient: {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1}
# traffic_gen_coefficient: {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1}
# test_1_num_iter = 1
# test_1_step = 50
def type_two_wit_two_dim_rate():
    ### Fix Params ###
    type = 2
    test_1_step = 50
    test_1_num_iter = 1
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    num_cluster = 4
    num_permanent_per_cluster = 5
    ################

    tunnel_build_coefficient = 0.1  # (0, 1]
    traffic_gen_coefficient = 0.1   # (0, 1]

    test_result_avg = {}
    # test_result_avg1 = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
    #                 calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

    test_result_avg[0] = []
    # test_result_avg[0].append('#' + str(tunnel_build_coefficient))
    # for key, value in test_result_avg1.items():
    #     if(key > 0):
    #         test_result_avg['0.1'] = []
    #         test_result_avg[key].append(value) 

    for i in range (1,11):
        tunnel_build_coefficient = i * 0.1
        key = str(tunnel_build_coefficient)

        for j in range (1,11):
            traffic_gen_coefficient = j * 0.1
            test_result_avg2, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                        calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

            # print(test_result_avg2)
            if(i == 1):
                test_result_avg[0].append('#' + str(traffic_gen_coefficient))

            for _, value in test_result_avg2.items():
                if not(key in test_result_avg):
                    test_result_avg[key] = []
                test_result_avg[key].append(value) 

    print(test_result_avg)
    create_csv('type_two_wit_two_dim_rate.csv', test_result_avg)

# test: 15
# proposed_structure
# num_permanent_per_cluster: {2, 4, 6, 8, 10, 15, 20, 30, 40, 50}
# num_cluster: {2, 4, 6, 8, 10, 15, 20, 30 , 40 ,50}
# test_1_num_iter = 1
# test_1_step = 50
def proposed_with_two_dim():
    ### Fix Params ###
    type = 3
    test_1_step = 50
    test_1_num_iter = 1
    test_1_repeat = 100

    number_of_ids = 100
    number_of_tunnels = 10
    tunnel_length = 3
    calc_entropy_flag = True

    tunnel_build_coefficient = 0.5  # (0, 1]
    traffic_gen_coefficient = 0.5   # (0, 1]

    ################

    num_cluster = 4
    num_permanent_per_cluster = 5

    test_result_avg = {}
    # test_result_avg1 = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
    #                 calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

    test_result_avg[0] = []
    # test_result_avg[0].append('#' + str(tunnel_build_coefficient))
    # for key, value in test_result_avg1.items():
    #     if(key > 0):
    #         test_result_avg['0.1'] = []
    #         test_result_avg[key].append(value) 

    num_permanent_per_cluster_list = [2, 4, 6, 8, 10, 15, 20, 30, 40, 50]
    num_cluster_list = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

    for c_item in num_cluster_list:
        num_cluster = c_item
        key = str(num_cluster)

        for pr_item in num_permanent_per_cluster_list:
            num_permanent_per_cluster = pr_item
            test_result_avg2, _ = simulate(test_1_repeat, test_1_step, test_1_num_iter, 0, number_of_ids, tunnel_length, type, 
                        calc_entropy_flag, traffic_gen_coefficient, tunnel_build_coefficient, num_cluster, num_permanent_per_cluster)

            # print(test_result_avg2)
            if(i == 1):
                test_result_avg[0].append('#' + str(num_permanent_per_cluster))

            for _, value in test_result_avg2.items():
                if not(key in test_result_avg):
                    test_result_avg[key] = []
                test_result_avg[key].append(value) 

    print(test_result_avg)
    create_csv('proposed_with_two_dim.csv', test_result_avg)

def write_to_excel_file(array, name):
    # print(array)
    converted_array_len = 1
    if len(array) > 0:
        converted_array_len = len(array[0])
    converted_array = [[] for x in range(converted_array_len) ]
        
    for i in range (len(array)):
        j = 0
        for _, value in array[i].items():
            converted_array[j].append(value)
            j = j+1
    # print(converted_array)
    data = np.array(converted_array, dtype=np.float32)
    df = pd.DataFrame(data)
    df.to_excel(excel_writer = name + ".xlsx")
    
def main():
    test = 4
    if(test == 1):
        proposed_with_different_pr()
    elif(test == 2):
        proposed_with_different_pr_small_set()
    elif(test == 3):
        proposed_with_different_traffic_coefficient()
    elif(test == 4):
        proposed_with_different_cluster()
    elif(test == 5):
        type_one_with_different_traffic_coefficient()
    elif(test == 6):
        type_two_with_different_traffic_coefficient()
    elif(test == 7):
        type_two_with_different_tunnel_build_coefficient()
    elif(test == 8):
        type_zero()
    elif(test == 9):
        comp_wit_rate()
    elif(test == 10):
        comp_wit_number_of_tunnels()
    elif(test == 11):
        test_i2P_1()
    elif(test == 12):
        test_tor_1()
    elif(test == 13):
        comp_with_tor_and_i2p_by_number_of_tunnels()
    elif(test == 14):
        type_two_wit_two_dim_rate()
    elif(test == 15):
        proposed_with_two_dim()

if __name__ == "__main__":
    main()

