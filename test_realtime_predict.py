import joblib
import pandas as pd
import numpy as np
import subprocess

model = joblib.load('eeg_color_classifier.joblib')

# Start the C program as a subprocess
mystery_O1 = pd.read_csv("logs_mystery/signal/O1.csv")
mystery_O2 = pd.read_csv("logs_mystery/signal/O2.csv")

mystery_O1.drop(columns=["timestamp"], inplace=True)
mystery_O2.drop(columns=["timestamp"], inplace=True)

def remove_outliers_mad(df, threshold=3.5):
    median = df['value'].median()
    mad = (df['value'] - median).abs().median() * 1.4826
    modified_zscore = (df['value'] - median).abs() / mad
    return df[modified_zscore < threshold]

mystery_O1 = remove_outliers_mad(mystery_O1)
mystery_O2 = remove_outliers_mad(mystery_O2)

min_len = min(len(mystery_O1), len(mystery_O2))
mystery_df = pd.DataFrame({
    "O1": mystery_O1["value"].iloc[:min_len].reset_index(drop=True),
    "O2": mystery_O2["value"].iloc[:min_len].reset_index(drop=True)
})

prediction = model.predict(mystery_df)

# count of each predicion