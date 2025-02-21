import pandas as pd
import ast
from sklearn.preprocessing import StandardScaler

def read_and_preprocess(file_path):
    """
    Reads the CSV file (which has a timestamp and a list of values per row)
    and converts it into a DataFrame with one column for the timestamp and separate
    columns for each feature.
    """
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            # Remove any extraneous whitespace
            s = line.strip()
            if not s:
                continue

            # Some lines might be prepended with line numbers or other extra characters.
            # For example, if a line looks like "2| 1740072222.455936,[...]", then remove the part before the actual data:
            if "|" in s:
                s = s.split("|", 1)[1].strip()

            # Split into timestamp and features using the first comma only
            parts = s.split(",", 1)
            if len(parts) != 2:
                continue

            try:
                timestamp = float(parts[0])
            except ValueError:
                print("Skipping an invalid timestamp in line:", s)
                continue

            feature_string = parts[1].strip()
            # Convert the string representation of the list into an actual list of numbers
            try:
                features = ast.literal_eval(feature_string)
            except Exception as e:
                print("Error parsing features from line:", s)
                continue

            # Combine timestamp and features into one list
            data.append([timestamp] + features)

    if not data:
        return None

    # Assume each row has the same number of features; create column names for features.
    num_features = len(data[0]) - 1
    columns = ['timestamp'] + [f'feat_{i}' for i in range(num_features)]
    df = pd.DataFrame(data, columns=columns)
    return df

# Path to your CSV file
file_path = 'color_logs_1/signal_green/spectrum/O2.csv'
df = read_and_preprocess(file_path)

# Preview the DataFrame
print("Initial DataFrame:")
print(df.head())

# OPTIONAL: Drop the timestamp if it is not useful for classification.
features = df.drop(columns=['timestamp'])

# Standardize the features (zero mean, unit variance)
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)
df_scaled = pd.DataFrame(scaled_features, columns=features.columns)

print("\nScaled features (ready for classification):")
print(df_scaled.head())

# Now, df_scaled is a clean, structured (and normalized) feature set that you can feed to your classification pipeline