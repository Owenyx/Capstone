import joblib
import pandas as pd
import numpy as np
import subprocess

model = joblib.load('heg_classifier.joblib')

# Start the C program as a subprocess
process = subprocess.Popen(
    ["Start HEG\\main.exe"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

while True:
    for line in iter(process.stdout.readline, ''):
        value = line.strip()
        data = pd.DataFrame({'reading': [value]})
        prediction = model.predict(data)[0]
        print(f"Value: {value}, {'Wearing' if prediction == 1 else 'Not wearing'}")
