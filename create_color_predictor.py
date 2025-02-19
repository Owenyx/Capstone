import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_validate

blue_O1 = pd.read_csv("logs_blue/signal/O1.csv")
blue_O2 = pd.read_csv("logs_blue/signal/O2.csv")

red_O1 = pd.read_csv("logs_red/signal/O1.csv")
red_O2 = pd.read_csv("logs_red/signal/O2.csv")

green_O1 = pd.read_csv("logs_green/signal/O1.csv")
green_O2 = pd.read_csv("logs_green/signal/O2.csv")

def remove_outliers_mad(df, threshold=3.5):
    median = df['value'].median()
    mad = (df['value'] - median).abs().median() * 1.4826
    modified_zscore = (df['value'] - median).abs() / mad
    return df[modified_zscore < threshold]

blue_O1 = remove_outliers_mad(blue_O1)
blue_O2 = remove_outliers_mad(blue_O2)

red_O1 = remove_outliers_mad(red_O1)
red_O2 = remove_outliers_mad(red_O2)

green_O1 = remove_outliers_mad(green_O1)
green_O2 = remove_outliers_mad(green_O2)

# Align the lengths of blue_O1 and blue_O2 and create a new DataFrame with columns "O1" and "O2"
min_len = min(len(blue_O1), len(blue_O2))
blue_df = pd.DataFrame({
    "O1": blue_O1["value"].iloc[:min_len].reset_index(drop=True),
    "O2": blue_O2["value"].iloc[:min_len].reset_index(drop=True)
})

min_len = min(len(red_O1), len(red_O2))
red_df = pd.DataFrame({
    "O1": red_O1["value"].iloc[:min_len].reset_index(drop=True),
    "O2": red_O2["value"].iloc[:min_len].reset_index(drop=True)
})

min_len = min(len(green_O1), len(green_O2))
green_df = pd.DataFrame({
    "O1": green_O1["value"].iloc[:min_len].reset_index(drop=True),
    "O2": green_O2["value"].iloc[:min_len].reset_index(drop=True)
})

blue_df['label'] = 'blue'
red_df['label'] = 'red'
green_df['label'] = 'green'

df = pd.concat([blue_df, red_df, green_df])

X = df[['O1', 'O2']]
y = df['label']

from sklearn.model_selection import cross_validate

model = LogisticRegression(class_weight="balanced", max_iter=1000)

scoring = {
    'accuracy': 'accuracy',
    'f1_macro': 'f1_macro'
}

cv_results = cross_validate(model, X, y, cv=100, scoring=scoring)

mean_accuracy = cv_results['test_accuracy'].mean()
mean_f1_macro = cv_results['test_f1_macro'].mean()
mean_error_rate = 1 - mean_accuracy

print("Mean Accuracy:     {:.4f}".format(mean_accuracy))
print("Mean F1-Score:     {:.4f}".format(mean_f1_macro))
print("Mean Error Rate:   {:.4f}".format(mean_error_rate))