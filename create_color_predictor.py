import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from joblib import dump

blue_O1 = pd.read_csv("color_logs\\signal_blue\\signal\\O1.csv")
blue_O2 = pd.read_csv("color_logs\\signal_blue\\signal\\O2.csv")
blue_T3 = pd.read_csv("color_logs\\signal_blue\\signal\\T3.csv")
blue_T4 = pd.read_csv("color_logs\\signal_blue\\signal\\T4.csv")


red_O1 = pd.read_csv("color_logs\\signal_red\\signal\\O1.csv")
red_O2 = pd.read_csv("color_logs\\signal_red\\signal\\O2.csv")
red_T3 = pd.read_csv("color_logs\\signal_red\\signal\\T3.csv")
red_T4 = pd.read_csv("color_logs\\signal_red\\signal\\T4.csv")

green_O1 = pd.read_csv("color_logs\\signal_green\\signal\\O1.csv")
green_O2 = pd.read_csv("color_logs\\signal_green\\signal\\O2.csv")
green_T3 = pd.read_csv("color_logs\\signal_green\\signal\\T3.csv")
green_T4 = pd.read_csv("color_logs\\signal_green\\signal\\T4.csv")

def remove_outliers_mad(df, threshold=3.5):
    median = df['value'].median()
    mad = (df['value'] - median).abs().median() * 1.4826
    modified_zscore = (df['value'] - median).abs() / mad
    return df[modified_zscore < threshold]

blue_O1 = remove_outliers_mad(blue_O1)
blue_O2 = remove_outliers_mad(blue_O2)
blue_T3 = remove_outliers_mad(blue_T3)
blue_T4 = remove_outliers_mad(blue_T4)


red_O1 = remove_outliers_mad(red_O1)
red_O2 = remove_outliers_mad(red_O2)
red_T3 = remove_outliers_mad(red_T3)
red_T4 = remove_outliers_mad(red_T4)

green_O1 = remove_outliers_mad(green_O1)
green_O2 = remove_outliers_mad(green_O2)
green_T3 = remove_outliers_mad(green_T3)
green_T4 = remove_outliers_mad(green_T4)

# Align the lengths of blue_O1 and blue_O2 and create a new DataFrame with columns "O1" and "O2"
min_len = min(len(blue_O1), len(blue_O2), len(blue_T3), len(blue_T4))
blue_df = pd.DataFrame({
    "O1": blue_O1["value"].iloc[:min_len].reset_index(drop=True),
    "O2": blue_O2["value"].iloc[:min_len].reset_index(drop=True),
    "T3": blue_T3["value"].iloc[:min_len].reset_index(drop=True),
    "T4": blue_T4["value"].iloc[:min_len].reset_index(drop=True)
})

min_len = min(len(red_O1), len(red_O2), len(red_T3), len(red_T4))
red_df = pd.DataFrame({
    "O1": red_O1["value"].iloc[:min_len].reset_index(drop=True),
    "O2": red_O2["value"].iloc[:min_len].reset_index(drop=True),
    "T3": red_T3["value"].iloc[:min_len].reset_index(drop=True),
    "T4": red_T4["value"].iloc[:min_len].reset_index(drop=True)
})

min_len = min(len(green_O1), len(green_O2), len(green_T3), len(green_T4))
green_df = pd.DataFrame({
    "O1": green_O1["value"].iloc[:min_len].reset_index(drop=True),
    "O2": green_O2["value"].iloc[:min_len].reset_index(drop=True),
    "T3": green_T3["value"].iloc[:min_len].reset_index(drop=True),
    "T4": green_T4["value"].iloc[:min_len].reset_index(drop=True)
})

blue_df['label'] = 'blue'
red_df['label'] = 'red'
green_df['label'] = 'green'

df = pd.concat([blue_df, red_df, green_df])

X = df[['O1', 'O2', 'T3', 'T4']]
y = df['label']

# Create a pipeline that scales data then applies Logistic Regression
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression(class_weight="balanced", max_iter=5000))
])

# Setup hyperparameter grid for Logistic Regression
param_grid = {
    'model__C': [0.001, 0.01, 0.1, 1, 10, 100],
    'model__solver': ['lbfgs', 'sag', 'saga']
}

# Use StratifiedKFold to maintain class proportions
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Set up grid search to find the best hyperparameters based on accuracy
grid_search = GridSearchCV(estimator=pipeline, param_grid=param_grid, cv=cv, scoring='accuracy')
grid_search.fit(X, y)

print("Best Parameters:", grid_search.best_params_)
print("Best CV Accuracy: {:.4f}".format(grid_search.best_score_))