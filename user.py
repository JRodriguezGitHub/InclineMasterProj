import json
import os
import re
import threading
from datetime import datetime
import pandas as pd
import psycopg2


class UserManager:
    _instance = None
    user_id = None

    combined_data = {}
    user_profile_file = "user_profile.json"
    user_preferences = {}
    exercise_data_file = 'exercise_data.json'
    dataset_file = 'workout_plans2.csv'
    df = pd.read_csv(dataset_file)
    exercise_data = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = UserManager()
        return cls._instance

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_id(self):
        return self.user_id

    def set_user_profile(self, profile_data):
        self.combined_data.update(profile_data)


    def get_user_profile(self):
        return self.combined_data


    def process_height(self):
        profile_data = self.get_user_profile()
        height = profile_data['Height (cm)']

        start_index = height.find('(')
        end_index = height.find('c', start_index)
        number_str = height[start_index + 1:end_index]
        height_value = int(number_str)

        profile_data['Height (cm)'] = height_value

    def extract_height_cm(self, height_str):
        match = re.search(r"(\d+)cm", height_str)
        return int(match.group(1)) if match else None

    def add_user_groups(self):
        profile_data = self.get_user_profile()
        age = profile_data['Age']
        weight = profile_data['Weight (lbs)']

        if age >= 18 and age <= 30:
            profile_data['Age Group'] = 1
        elif age >= 31 and age <= 40:
            profile_data['Age Group'] = 2
        elif age >= 41 and age <= 50:
            profile_data['Age Group'] = 3
        else:
            profile_data['Age Group'] = 4

        if weight >= 80 and weight <= 101:
            profile_data['Weight Group'] = 1
        elif weight >= 100 and weight <= 121:
            profile_data['Weight Group'] = 2
        elif weight >= 120 and weight <= 141:
            profile_data['Weight Group'] = 3
        elif weight >= 140 and weight <= 161:
            profile_data['Weight Group'] = 4
        elif weight >= 160 and weight <= 181:
            profile_data['Weight Group'] = 5
        elif weight >= 180 and weight <= 201:
            profile_data['Weight Group'] = 6
        elif weight >= 201 and weight <= 220:
            profile_data['Weight Group'] = 7
        else:
            profile_data['Weight Group'] = 8

    def update_user_profile(self):
        pass

    def set_user_goals(self, goal, weight, days, split):
        self.combined_data["Goal"] = goal
        self.combined_data["Weight Loss (lbs)"] = weight
        self.combined_data["Frequency days/week"] = days
        self.combined_data["Workout Type"] = split

    def add_weight_loss_scale(self):
        profile_data = self.get_user_profile()
        weight_str = profile_data.get('Weight Loss (lbs)', '').strip()

        if weight_str.isdigit():
            weight = int(weight_str)
            if weight == 0:
                self.combined_data['Weight Loss Scale'] = 0
            elif weight <= 15:
                self.combined_data['Weight Loss Scale'] = 1
            elif weight <= 25:
                self.combined_data['Weight Loss Scale'] = 2
            elif weight <= 35:
                self.combined_data['Weight Loss Scale'] = 3
            elif weight <= 45:
                self.combined_data['Weight Loss Scale'] = 4
            else:
                self.combined_data['Weight Loss Scale'] = 5
        else:
            print("Invalid or missing weight input for weight loss scale calculation.")

    def process_frequency(self):
        profile_data = self.get_user_profile()
        frequency = profile_data['Frequency days/week']

        parts = frequency.split()
        for part in parts:
            if part.isdigit():
                frequency_value = int(part)
                profile_data['Frequency days/week'] = frequency_value
                return profile_data

    def set_user_preferences(self, preferences):
        self.user_preferences = preferences

    def process_user_preferences(self):
        preference_data = self.get_user_preferences()
        frequency = preference_data['Frequency days/week']

        parts = frequency.split()
        for part in parts:
            if part.isdigit():

                frequency_value = int(part)
                preference_data['Frequency days/week'] = frequency_value
                return preference_data
                # return int(part)

    def get_user_preferences(self):
        return self.user_preferences

    def get_user_goals(self):
        return self.user_goals


    def set_user_start_date(self, start_date):

        with open("user_data.json", "w") as f:
            json.dump({"user_start_date": start_date.strftime("%Y-%m-%d")}, f)

    def get_user_start_date(self):
        try:
            with open("user_data.json", "r") as f:
                data = json.load(f)
                return datetime.strptime(data["user_start_date"], "%Y-%m-%d")
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None

    # SAVE USER WORKOUT AFTER SETTING GOALS

    def set_user_rec_workout(self, workout):
        try:
            with open("user_data.json", "r+") as f:
                data = json.load(f)
                data["user_workout"] = workout
                f.seek(0)
                json.dump(data, f)
                f.truncate()
        except FileNotFoundError:
            print("User data file not found.")

    def get_user_rec_workout(self):
        try:
            with open("user_data.json", "r") as f:
                data = json.load(f)
                return data.get("user_workout")
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None

    def save_user_profile(self):
        with open(self.user_profile_file, "w") as f:
            json.dump(self.combined_data, f)

    def load_user_profile(self):
        file = self.user_profile_file
        try:
            with open(file, "r") as f:
                self.combined_data = json.load(f)
        except FileNotFoundError:
            self.combined_data = {}

    def extract_exercises(self):
        workout_plan_name = self.get_user_rec_workout()
        filtered_df = self.df[self.df['Name'] == workout_plan_name]
        exercise_data = {}
        if not filtered_df.empty:
            columns = filtered_df.columns[filtered_df.columns != 'Name']
            for col_name in columns:
                exercises_list = []
                if col_name.startswith('Day'):
                    for exercise_info in filtered_df[col_name]:
                        if exercise_info.strip() == "Rest":
                            exercises_list.append({"Rest": {"Sets": None, "Reps": None}})
                        else:
                            exercises = re.findall(r'\[(.*?)\]', exercise_info)
                            # print(exercises)
                            for exercise in exercises:
                                match = re.match(r'(.*?), Sets: (\d+), Reps: (\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)',
                                                         exercise)
                                    # match = re.match(r'(.*?), Sets: (\d+), Reps: (\d+-\d+)', exercise)
                                if match:
                                    exercise_name = match.group(1).strip()
                                    sets = match.group(2)
                                    reps = match.group(3)
                                    exercises_list.append({exercise_name: {"Sets": sets, "Reps": reps}})
                    exercise_data[col_name] = exercises_list

            with open('exercise_data.json', 'w') as json_file:
                json.dump(exercise_data, json_file, indent=4)

            print(exercise_data)


    def get_exercise_data(self):
        # self.file_created_event.wait()
        try:
            with open("exercise_data.json", "r") as f:
                exercise_data = json.load(f)
                return exercise_data
        # except (FileNotFoundError, json.JSONDecodeError, KeyError):
        #     return None
        except FileNotFoundError:
            print("FileNotFoundError: 'exercise_data.json' not found")
            return None
        except json.JSONDecodeError:
            print("JSONDecodeError: Failed to decode 'exercise_data.json'")
            return None
        except KeyError:
            print("KeyError: Unexpected structure in 'exercise_data.json'")
            return None

    # def temp_exercise_data(self):
    #     exercise_data = self.get_exercise_data()
    #     self.exercise_data = exercise_data
    #     return self.exercise_data

    def save_profile_to_db(self, user_id, age, gender, height, weight, experience):
        # Define connection parameters
        rds_host = 'refer to email'
        rds_port = 'refer to email'
        rds_dbname = 'refer to email'
        rds_user = 'refer to email'
        rds_password = 'refer to email'
        conn_string = f"host={rds_host} port={rds_port} dbname={rds_dbname} user={rds_user} password={rds_password}"
        height_cm = self.extract_height_cm(height)
        conn = None
        try:
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO profile (userid, age, gender, height, currentweight, explvl)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (user_id, age, gender, height_cm, weight, experience)
            )
            conn.commit()
            cursor.close()
        except Exception as e:
            print("Error saving profile to database:", e)
        finally:
            if conn is not None:
                conn.close()