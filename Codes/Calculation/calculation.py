# Regenerating the nodes DataFrame correctly, including the fix for IP addresses generation
import random
import secrets
import string
import time
from typing import Final
import numpy as np
import pandas as pd
import array

from encryption_algorithms import (
    generate_elgamal_keys,
    generate_aes_key,
    elgamal_encrypt,
    elgamal_decrypt, aes_encrypt, aes_decrypt
)

MIN_SEED_NODEID: Final[int] = 0
MAX_SEED_NODEID: Final[int] = 99

MAX_ITERATION_NUMBER: Final[int] = 10
MAX_ROUND_NUMBER: Final[int] = 10

MIN_COMMUNICATION_INTERVAL_VALUE: Final[int] = 10
MAX_COMMUNICATION_INTERVAL_VALUE: Final[int] = 100

MIN_SEED_LATENCY: Final[int] = 1
MAX_SEED_LATENCY: Final[int] = 100
TEST_ID = 'Proposed' # [TOR, I2P, Proposed]


def generate_random_string(length: int) -> str:
    """
    https://www.educative.io/edpresso/how-to-generate-a-random-string-in-python

    :param length: positive integer
    :Example:
        generate_random_string(10) => "Qk_qLAC}v?"
    """
    assert isinstance(length, int) and length > 0, "`length` argument must be positive integer."

    letters = string.ascii_letters + string.digits + string.punctuation
    # secrets.choice used instead of random.choice for more security.
    random_str = ''.join(secrets.choice(letters) for _ in range(length))
    return random_str


def calculate_communication_interval_random_number() -> int:
    return random.randint(MIN_COMMUNICATION_INTERVAL_VALUE, MAX_COMMUNICATION_INTERVAL_VALUE)


def generate_random_seed():
    return random.randint(MIN_SEED_NODEID, MAX_SEED_NODEID)


def aes_key_sharing() -> tuple:
    """ get_encrypted_and_decrypted_aes_keys """
    
    start = time.time()
    # Example usage
    key_size = 256  # Key size in bits for ElGamal
    keys = generate_elgamal_keys(key_size)
    public_key = keys['publicKey']
    private_key = keys['privateKey']

    # Generate AES key and encrypt it with ElGamal
    aes_key = generate_aes_key()
    # Simulate converting AES key to an integer for ElGamal encryption
    aes_key_int = int.from_bytes(aes_key, byteorder='big', signed=False)
    encrypted_aes_key = elgamal_encrypt(public_key, aes_key_int)    
    # Decrypt AES key with ElGamal
    decrypted_aes_key_int = elgamal_decrypt(private_key, encrypted_aes_key, public_key[0])
    decrypted_aes_key = decrypted_aes_key_int.to_bytes((decrypted_aes_key_int.bit_length() + 7) // 8, byteorder='big')

    end = time.time()
    execution_time_in_ms = end - start
    return aes_key, execution_time_in_ms


def encrypt_and_decrypt_message_with_aes(decrypted_aes_key) -> tuple:
    # Encrypt and decrypt a message with AES
    # random_plaintext: str = 'A' * 1024
    start = time.time()
    random_plaintext = '&>tsX@(3BjsAepZW'
    ciphertext = aes_encrypt(decrypted_aes_key, random_plaintext)
    # time.sleep(0.001)
    decrypted_text = aes_decrypt(decrypted_aes_key, ciphertext)
    end = time.time()
    execution_time_in_ms = end - start
    return decrypted_text, execution_time_in_ms


# output: list = []
sum_average_latency_total_for_each_iteration = 0
latency_array = array.array('f', [])

for iteration in range(1, MAX_ITERATION_NUMBER + 1):
    sum_latency_total: int = 0

    # Generating random data for X nodes
    nodes = pd.DataFrame({
        'NodeID': range(1, 101),
        'LatencyToNextNode_ms': np.random.uniform(MIN_SEED_LATENCY, MAX_SEED_LATENCY, size=100)
        # Random latency
    })
    nodes['IPAddress'] = ['.'.join(map(str, np.random.randint(1, 255, size=4))) for _ in range(100)]

    for round in range(1, MAX_ROUND_NUMBER + 1):
        # Setting a seed for reproducibility

        communication_interval_min_range: int = 0
        communication_interval_max_range: int = calculate_communication_interval_random_number()

        sum_latency_for_node = 0
        avg_sum_latency_for_node = 0
        sum_process_time_for_node = 0

        seed_01 = generate_random_seed()
        seed_02 = generate_random_seed()
        seed_03 = generate_random_seed()

        np.random.seed(seed_01)
        # Selecting specific nodes for the communication path
        sender = nodes.iloc[seed_02]  # First node
        middle_node_1 = nodes.iloc[np.random.randint(1, 99)]  # Random middle node 1
        middle_node_2 = nodes.iloc[
            np.random.randint(1, 99)]  # Random middle node 2, ensuring it's not the same as middle_node_1
        middle_node_3 = nodes.iloc[
            np.random.randint(1, 99)]  # Random middle node 3, ensuring it's not the same as middle_node_1-2
        middle_node_4 = nodes.iloc[
            np.random.randint(1, 99)]  # Random middle node 4, ensuring it's not the same as middle_node_1-3
        receiver = nodes.iloc[seed_03]  # Last node

        for communication_interval_index in range(communication_interval_min_range, communication_interval_max_range):
            is_first_time: bool = communication_interval_index == 0
        
            decrypted_aes_key, execution_time_aes_key_sharing_with_elgamal = aes_key_sharing()
            _, execution_time_encrypt_and_decrypt_message_with_aes = encrypt_and_decrypt_message_with_aes(
                decrypted_aes_key=decrypted_aes_key)
        
            if is_first_time:
                process_time_for_node = execution_time_aes_key_sharing_with_elgamal
            else:
                process_time_for_node = execution_time_encrypt_and_decrypt_message_with_aes
                
            if TEST_ID == 'TOR':
                sum_process_time_for_node = process_time_for_node + (
                        2 * execution_time_encrypt_and_decrypt_message_with_aes)
            elif TEST_ID == 'I2P':
                sum_process_time_for_node = 2 * process_time_for_node + (
                        4 * execution_time_encrypt_and_decrypt_message_with_aes)
            elif TEST_ID == 'Proposed':
                sum_process_time_for_node = 2 * process_time_for_node + (
                        6 * execution_time_encrypt_and_decrypt_message_with_aes)
        
            sum_latency_for_node += sum_process_time_for_node
            if TEST_ID == 'TOR':
                for node in (sender, middle_node_1, middle_node_2, receiver):
                    latency_to_next_node_in_seconds = node.LatencyToNextNode_ms /1000
                    sum_latency_for_node += latency_to_next_node_in_seconds
            elif TEST_ID == 'I2P':
                for node in (sender, middle_node_1, middle_node_2, middle_node_3, receiver):
                    latency_to_next_node_in_seconds = node.LatencyToNextNode_ms /1000
                    sum_latency_for_node += latency_to_next_node_in_seconds
            elif TEST_ID == 'Proposed':
                for node in (sender, middle_node_1, middle_node_2, middle_node_3, middle_node_4, receiver):
                    latency_to_next_node_in_seconds = node.LatencyToNextNode_ms /1000
                    sum_latency_for_node += latency_to_next_node_in_seconds

        avg_sum_latency_for_node = sum_latency_for_node / communication_interval_max_range
        sum_latency_total += avg_sum_latency_for_node

        # Creating a dataframe for the communication path
        path = pd.DataFrame([sender, middle_node_1, middle_node_2, receiver],
                            index=[
                                    'Sender -> MiddleNode1', 
                                    'MiddleNode1 -> MiddleNode2', 
                                    'MiddleNode2 -> MiddleNode3', 
                                    'MiddleNode3 -> Receiver'
                                    ]
                            )
        if TEST_ID == 'I2P':
            path = pd.DataFrame([sender, middle_node_1, middle_node_2, middle_node_3, receiver],
                                index=[
                                        'Sender -> MiddleNode1', 
                                        'MiddleNode1 -> MiddleNode2', 
                                        'MiddleNode2 -> MiddleNode3', 
                                        'MiddleNode3 -> MiddleNode4',
                                        'MiddleNode4 -> Receiver'
                                        ]
                                )
        elif TEST_ID == 'Proposed':
            path = pd.DataFrame([sender, middle_node_1, middle_node_2, middle_node_3, middle_node_4, receiver],
                                index=[
                                        'Sender -> MiddleNode1', 
                                        'MiddleNode1 -> MiddleNode2', 
                                        'MiddleNode2 -> MiddleNode3', 
                                        'MiddleNode3 -> MiddleNode4',
                                        'MiddleNode4 -> MiddleNode5',
                                        'MiddleNode5 -> Receiver'
                                        ]
                                )
                                
        # output.append((sender, middle_node_1, middle_node_2, receiver))
        # output.append((sender.values, middle_node_1.values, middle_node_2.values, receiver.values))

        latency_array.append(avg_sum_latency_for_node)
        print(f"ROUND #{round}")
        # print(path)
        print(f'SUM LATENCY for Iteration#{iteration} - Round#{round}----> {avg_sum_latency_for_node}')
        print('*' * 70)

    # print(output)

    print('%' * 100)
    average_latency_total_for_each_iteration: float = sum_latency_total / MAX_ROUND_NUMBER

    sum_average_latency_total_for_each_iteration += average_latency_total_for_each_iteration
    print(f"average_latency_total for iteration #{iteration}: {average_latency_total_for_each_iteration}")

    print('-' * 100)

average_latency_total_for_all_iterations: float = sum_average_latency_total_for_each_iteration / MAX_ITERATION_NUMBER
print('---------------FINAL RESULT------------------')
print(f'Average latency total for all iterations :--> {average_latency_total_for_all_iterations}')

print(latency_array)
data = np.array(latency_array, dtype=np.float32)
df = pd.DataFrame(data).T
df.to_excel(excel_writer = "./test_" + TEST_ID + "_" + str(MAX_SEED_LATENCY) + ".xlsx")
