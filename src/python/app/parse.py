import json

def extract_counts(raw_text):
    parsed_data = json.loads(raw_text)
    di_val = parsed_data["DIVal"]

    my_array = []
    for val in di_val:
        my_array.append(val["Val"])

    return my_array
