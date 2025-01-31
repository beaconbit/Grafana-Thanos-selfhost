import json
import time
import os
import struct
from datetime import datetime, timedelta
import random

def delta_encode_timestamps(timestamps):
    deltas = [timestamps[0]]
    for i in range(1, len(timestamps)):
        deltas.append(timestamps[i] - timestamps[i - 1])
    return deltas

def xor_encode_values(values):
    if not values:
        return []
    encoded = [values[0]]
    prev = values[0]
    for value in values[1:]:
        xor = struct.unpack(">Q", struct.pack(">d", prev))[0] ^ struct.unpack(">Q", struct.pack(">d", value))[0]
        encoded.append(xor)
        prev = value
    return encoded

def generate_metrics(start_time, metric_name, labels, values):
    metrics = []
    for i, value in enumerate(values):
        timestamp = int((start_time + timedelta(seconds=i)).timestamp() * 1000)  # Prometheus uses milliseconds
        labels_str = format_labels(labels)
        metric_line = f'{metric_name}{{{labels_str}}} {value} {timestamp}'
        metrics.append(metric_line)
    return metrics

def format_labels(labels_dict):
    return ",".join(f'{key}="{value}"' for key, value in labels_dict.items())


def write_binary(filename, metric_name, labels, deltas, encoded_values):
    with open(filename, "wb") as f:
        # Write metric name length and name
        f.write(struct.pack(">H", len(metric_name)))  # Metric name length (big-endian, 2 bytes)
        f.write(metric_name.encode("utf-8"))  # Metric name (utf-8 encoded)

        # Write labels as key-value pairs
        f.write(struct.pack(">H", len(labels)))  # Number of labels (big-endian, 2 bytes)
        for key, value in labels.items():
            f.write(struct.pack(">H", len(key)))  # Key length
            f.write(key.encode("utf-8"))  # Key
            f.write(struct.pack(">H", len(value)))  # Value length
            f.write(value.encode("utf-8"))  # Value

        # Write timestamp deltas
        f.write(struct.pack(">I", len(deltas)))  # Number of deltas (big-endian, 4 bytes)
        for delta in deltas:
            f.write(struct.pack(">Q", delta))  # Delta timestamps (big-endian, 8 bytes)

        # Write XOR encoded values
        f.write(struct.pack(">I", len(encoded_values)))  # Number of values (big-endian, 4 bytes)
        for encoded in encoded_values:
            f.write(struct.pack(">Q", encoded))  # XOR encoded values (big-endian, 8 bytes)



def main():
    # Define initial parameters
    start_time = datetime.strptime("2025-01-23 11:06:00", "%Y-%m-%d %H:%M:%S")

    metric_name = "load_count_cbw_1"
    labels = {
        "job": "webserver",
        "instance": "192.168.1.100:8080",
        "env": "prod",
        "region": "us-west",
    }

    # Metric values
    values = [10, 11, 12, 13, 14]


    timestamps = [
        int((start_time + timedelta(seconds=i)).timestamp() * 1000) for i in range(len(values))
    ]

    delta_timestamps = delta_encode_timestamps(timestamps)
    xor_encoded_values = xor_encode_values(values)

    # Write to binary file
    output_file = "metrics.bin"
    write_binary(output_file, metric_name, labels, delta_timestamps, xor_encoded_values)


if __name__ == "__main__":
    main()









