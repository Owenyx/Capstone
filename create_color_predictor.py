import pandas as pd
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
import numpy as np

class ColorPredictor:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.colors = ["blue", "green", "red"]
        self.wave_types = ["alpha", "beta", "theta"]
        self.channels = ["O1", "O2"]

        # create wave channel pairs
        self.wave_channel_pairs = []
        for wave in self.wave_types:
            for channel in self.channels:
                self.wave_channel_pairs.append(f"{channel}_{wave}")

        # this is a dictionary of dataframes for each color
        self.train_color_dfs = self.create_color_dataframes()

        self.best_model = self.train_model()

    def create_color_dataframes(self):
        #dictionary of dataframes for each color
        color_dfs = {}

        # for each color, create a dataframe for each wave type
        for color in self.colors:
            wave_dfs = []

            for wave in self.wave_types:
                data = {channel: [] for channel in self.channels}
                for channel in self.channels:
                    filepath = f"{self.folder_path}\\signal_{color}\\waves\\{channel}\\{wave}\\percent.csv"
                    df_temp = pd.read_csv(filepath)
                    # Append the 'value' column data from the file
                    data[channel].append(df_temp['value'])
                # Create a dataframe for this wave type by concatenating the values per channel
                wave_df = pd.DataFrame({
                    f"{channel}_{wave}": pd.concat(readings, ignore_index=True)
                    for channel, readings in data.items()
                })
                wave_dfs.append(wave_df)
            # Concatenate all wave dataframes horizontally for the current color
            color_dfs[color] = pd.concat(wave_dfs, axis=1)
        return color_dfs
    
    def train_model(self):

        train_blue_df = self.train_color_dfs["blue"]
        train_green_df = self.train_color_dfs["green"]
        train_red_df = self.train_color_dfs["red"]

        train_blue_df["label"] = "blue"
        train_green_df["label"] = "green"
        train_red_df["label"] = "red"

        train_waves = pd.concat([train_blue_df, train_green_df, train_red_df])
        
        X_train, X_test, y_train, y_test = train_test_split(train_waves[self.wave_channel_pairs], train_waves['label'], test_size=0.3, stratify=train_waves['label'])

        # Build a pipeline that applies scaling and Logistic Regression
        pipeline = Pipeline([
            ('scaler', RobustScaler()),
            ('classifier', LogisticRegression())
        ])

        # Define the hyperparameter grid for tuning
        param_grid = {
            'classifier__C': np.logspace(-4, 4, 20),
            'classifier__penalty': ['l1', 'l2'],       # Try both l1 and l2 regularization
            'classifier__solver': ['liblinear'],       # liblinear supports both l1 and l2
            'classifier__max_iter': [100, 200, 500]      # Vary max_iter to ensure convergence
        }

        # Perform grid search cross-validation to tune hyperparameters
        grid_search = GridSearchCV(pipeline, param_grid, cv=10, scoring='accuracy', n_jobs=-1)
        grid_search.fit(X_train, y_train)

        print("Best parameters found: ", grid_search.best_params_)

        # Predict on the test set using the best estimator from grid search
        y_pred = grid_search.predict(X_test)

        print(classification_report(y_test, y_pred))
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")

        return grid_search.best_estimator_