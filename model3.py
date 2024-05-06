import json
import re

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from user import UserManager


class Model3:

    user_clusters = pd.read_csv('final_user_clusters.csv')
    encoded_clusters = pd.read_csv('final_encoded_clusters.csv')

    workout_plans = pd.read_csv('workout_plans2.csv')

    workout_plans = workout_plans.fillna('Rest')

    workouts = pd.read_csv('workouts2.csv')

    # pd.set_option('display.max_columns', None)
    # print(workouts)

    userManager = UserManager.get_instance()

    rec_workout = None

    def json_to_dataframe(self):
        try:

            with open("user_profile.json", 'r') as file:
                data = json.load(file)


            df = pd.DataFrame([data], index=[0])

            return df
        except FileNotFoundError:
            print(f"File user_profile.json not found.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def process_user_data(self):


        user_data = self.json_to_dataframe()

        pd.set_option('display.max_columns', None)


        expected_columns = ['Frequency days/week', 'Age Group', 'Weight Group', 'Weight Loss Scale',
                            'Gender_Female', 'Gender_Male',	'Goal_Build Muscle', 'Goal_Lose Fat', 'Experience Level_Beginner',
                            'Experience Level_Intermediate', 'Workout Type_Full Body', 'Workout Type_Split']


        # user_profile_df_encoded = pd.get_dummies(user_data, columns=['Gender', 'Goal', 'Experience Level', 'Age Group', 'Weight Group','Weight Loss Scale'])
        user_profile_df_encoded = pd.get_dummies(user_data, columns=['Gender', 'Goal', 'Experience Level', 'Workout Type'])

        for column in expected_columns:
            if column not in user_profile_df_encoded.columns:
                user_profile_df_encoded[column] = 0

        user_profile_df_encoded = user_profile_df_encoded[expected_columns]

        for column in user_profile_df_encoded.columns:

            if all(value in [True, False] for value in user_profile_df_encoded[column]):

                user_profile_df_encoded[column] = user_profile_df_encoded[column].astype(int)



        return user_profile_df_encoded

    def classify_user(self):
        user_df = self.process_user_data()

        X = self.encoded_clusters.drop(['Cluster'], axis=1)
        y = self.encoded_clusters['Cluster']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        rf_classifier = RandomForestClassifier(n_estimators=150, min_samples_split= 30,
                                               min_samples_leaf=10, random_state=42)

        rf_classifier.fit(X_train, y_train)


        predicted_cluster = rf_classifier.predict(user_df)

        if isinstance(predicted_cluster, np.ndarray):
            predicted_cluster = predicted_cluster[0]

        return predicted_cluster

    def get_cluster_workouts(self):
        cluster = self.classify_user()

        cluster_workouts = self.user_clusters[self.user_clusters['Cluster'] == cluster]

        workouts = cluster_workouts['Workout Plan'].unique()

        return workouts

    def similarity(self):
        workouts = self.get_cluster_workouts()
        num = len(workouts)

        if num == 1:
            rec_workout = workouts[0]
            return rec_workout
            print(workouts[0])
        else:

            filtered_df = self.workouts[self.workouts['Name'].isin(workouts)]

            filtered_df = filtered_df.drop(['Program Duration', 'Training Level', 'Goal', 'Equipment '],
                                           axis=1)

            filtered_df['Days per Week'] = filtered_df['Days per Week'].astype(str)

            filtered_df['Combined Text'] = filtered_df['Workout Type'].map(str) + " " + \
                                           filtered_df['Time per Workout'] + " " + filtered_df['Days per Week']

            filtered_df.drop(columns=['Workout Type', 'Time per Workout', 'Days per Week'], inplace=True)
            filtered_df['Combined Text'] = filtered_df['Combined Text'].str.replace('\n', '')

            count_vectorizer = CountVectorizer()

            count_features = count_vectorizer.fit_transform((filtered_df['Combined Text']))
            count_features_df = pd.DataFrame(count_features.toarray(), columns=count_vectorizer.get_feature_names_out())



            data = self.userManager.get_user_preferences()


            frequency = data.get('Frequency days/week', '')
            workout_split = data.get('Workout Split', '')
            selected_time = data.get('Selected Time', '')

            user_preferences = {'Text': [f'{frequency}, {workout_split}, {selected_time}']}

            # user_preferences = {'Text': ['Full Body 60 min 4']}
            # user_preferences_df = pd.DataFrame(user_preferences)
            # user_preferences_df

            user_preferences_df = pd.DataFrame(user_preferences)

            count_user_pref = count_vectorizer.transform((user_preferences_df['Text']))
            count_user_pref_df = pd.DataFrame(count_user_pref.toarray(),
                                              columns=count_vectorizer.get_feature_names_out())

            combined_text = list(filtered_df['Combined Text']) + list(user_preferences_df['Text'])

            count_vectorizer = CountVectorizer()
            count_vectorizer.fit(combined_text)

            count_vectors_first_df = count_vectorizer.transform(filtered_df['Combined Text'])
            count_vectors_second_df = count_vectorizer.transform(user_preferences['Text'])


            cosine_similarity_scores = cosine_similarity(count_vectors_second_df, count_vectors_first_df)

            similarity_df = pd.DataFrame({
                'Name': filtered_df['Name'],
                'Similarity Score': cosine_similarity_scores.flatten()
            })


            similarity_df
            ranked_results = similarity_df.sort_values(by='Similarity Score', ascending=False)
            # ranked_results
            rec_workout = ranked_results.iloc[0, 0]
            rec_workout

            print(num)
            return rec_workout

    pass

