import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline

def combine_waves(color_log_folders, color, channels, wave_type):
    data = {channel: [] for channel in channels}
    for folder in color_log_folders:
        for channel in channels:
            filepath = f"{folder}\\signal_{color}\\waves\\{channel}\\{wave_type}\\raw.csv"
            df_temp = pd.read_csv(filepath)
            # Append the 'value' column data from each file
            data[channel].append(df_temp['value'])
    return pd.DataFrame({f"{channel}_{wave_type}": pd.concat(readings, ignore_index=True) for channel, readings in data.items()})

def create_color_dataframes(colors, wave_types, channels, logs):
    """
    Creates a dictionary of dataframes for each color, where each dataframe is 
    the concatenation (along axis=1) of the waves for a given color.
    """
    color_dfs = {}
    for color in colors:
        # For each color, get the dataframe for each wave type (alpha, beta, theta)
        wave_dfs = [combine_waves(logs, color, channels, wave)
                    for wave in wave_types]
        # Concatenate the wave dataframes horizontally.
        color_dfs[color] = pd.concat(wave_dfs, axis=1)
    return color_dfs

# Define the configuration lists.
colors = ["green", "red", "violet"]
wave_types = ["alpha"]
channels = ["O1", "O2"]
logs = ["color_logs_5"]  # ['color_logs_1', 'color_logs_2', ..., 'color_logs_5']

# Generate dataframes for each color.
train_color_dfs = create_color_dataframes(colors, wave_types, channels, logs)
test_color_dfs = create_color_dataframes(colors, wave_types, channels, ["color_logs_5"])

# Now you can access your dataframes like so:
train_green_df = train_color_dfs["green"]
train_red_df = train_color_dfs["red"]
train_violet_df = train_color_dfs["violet"]

test_green_df = test_color_dfs["green"]
test_red_df = test_color_dfs["red"]
test_violet_df = test_color_dfs["violet"]

train_green_df["label"] = "green"
train_red_df["label"] = "red"
train_violet_df["label"] = "violet"

test_green_df["label"] = "green"
test_red_df["label"] = "red"
test_violet_df["label"] = "violet"

train_waves = pd.concat([train_green_df, train_red_df, train_violet_df])
test_waves = pd.concat([test_green_df, test_red_df, test_violet_df])

X_train = train_waves[['O1_alpha', 'O2_alpha']]
y_train = train_waves['label']

X_test = test_waves[['O1_alpha', 'O2_alpha']]
y_test = test_waves['label']

# Build a pipeline that applies scaling and Logistic Regression
pipeline = Pipeline([
    ('scaler', RobustScaler()),
    ('classifier', LogisticRegression(max_iter=1000))
])

# Define the hyperparameter grid for tuning
param_grid = {
    'classifier__C': [0.01, 0.1, 1, 10],
}

# Perform grid search cross-validation to tune hyperparameters
grid_search = GridSearchCV(pipeline, param_grid, cv=10, scoring='accuracy', n_jobs=-1)
grid_search.fit(X_train, y_train)

print("Best parameters found: ", grid_search.best_params_)

# Predict on the test set using the best estimator from grid search
y_pred = grid_search.predict(X_test)

print(classification_report(y_test, y_pred))
print(accuracy_score(y_test, y_pred))