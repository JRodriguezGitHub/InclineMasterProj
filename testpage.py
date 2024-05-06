import json
import os
import pickle
from kivy.graphics.texture import Texture
import re
from datetime import timedelta, datetime
import re
from PIL import Image, ImageOps, ImageSequence
import pandas as pd
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from datetime import datetime, timedelta
import calendar
import requests
from kivymd.uix.card import MDCard
from kivy.core.image import Image as CoreImage
from io import BytesIO
import os
from kivymd.uix.button import MDRaisedButton
import openai
import json
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
import pandas as pd
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.utils import get_color_from_hex
from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.screen import MDScreen
from model3 import Model3
from exercise_card import Card
import unicodedata

Builder.load_string("""
<HomePage7>:
    MDBottomNavigation:

        MDBottomNavigationItem:
            name: 'journal_tab'
            text: 'Journal'
            icon: 'book-open-variant'
            MDTabs:
                Tab:
                    title: 'Workout'
                    icon: 'dumbbell'
                    # Ensure WorkoutScreen is defined and accessible
                    WorkoutScreen:
                Tab:
                    title: 'Calories'
                    icon: 'food'
                    # Ensure CalorieTrackerScreen is defined and accessible
                    CalorieTrackerScreen:
                Tab:
                    title: 'Summary'
                    icon: 'chart-bar'
                    # Include SummaryScreen under this tab
                    SummaryScreen:

        MDBottomNavigationItem:
            name: 'create_tab'
            text: 'My Workout'
            icon: 'creation'

            MDBoxLayout:
                orientation: 'vertical'
                MDTopAppBar:
                    title: "Your Workout"
                    elevation: 0
                    # md_bg_color: 99/255, 210/255, 218/255, 1

                MDBoxLayout:
                    size_hint_y: None
                    height: category_box.minimum_height
                    canvas.before:
                        Color:
                            rgba: 0.129, 0.588, 0.953, 1  # Blue color
                        Rectangle:
                            size: self.size
                            pos: self.pos
                    ScrollView:
                        do_scroll_x: True
                        do_scroll_y: False
                        size_hint_y: None
                        height: category_box.minimum_height

                        MDBoxLayout:
                            id: category_box
                            orientation: 'horizontal'
                            size_hint_x: None  # Ensure the width adapts to content
                            width: self.minimum_width 
                            heigth: self.minimum_height 
                            spacing: 30

                ScrollView:
                    id: card_scroll
                    GridLayout:
                        id: card_grid
                        cols: 1
                        spacing: '10dp'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: '10dp'


        
""")


def get_first_frame_of_gif(gif_path):
    with Image.open(gif_path) as img:
        img.seek(0)
        first_frame = img.convert('RGB')
        first_frame_path = gif_path.replace('.gif', '_first_frame.png')
        first_frame.save(first_frame_path)
        return first_frame_path

class HomePage7(MDScreen):
    class Tab(MDFloatLayout, MDTabsBase):
        pass

    class CalendarPopup(Popup):
        def __init__(self, date_button, **kwargs):
            super(HomePage7.CalendarPopup, self).__init__(**kwargs)
            self.size_hint = (0.8, 0.8)
            self.title = 'Select a Date'
            self.date_button = date_button
            self.date_format = "%Y-%m-%d"
            self.selected_date = datetime.now()
            layout = BoxLayout(orientation='vertical', spacing=5)
            header_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=5)
            prev_month_button = Button(text='<', on_press=self.change_month)
            self.month_label = Label(text=self.get_month_year())
            next_month_button = Button(text='>', on_press=self.change_month)
            header_layout.add_widget(prev_month_button)
            header_layout.add_widget(self.month_label)
            header_layout.add_widget(next_month_button)
            layout.add_widget(header_layout)
            self.today_button = Button(text="Today", size_hint_y=None, height=40)
            self.today_button.bind(on_press=self.set_today)
            layout.add_widget(self.today_button)
            self.calendar_layout = GridLayout(cols=7, size_hint_y=0.7)
            layout.add_widget(self.calendar_layout)
            self.create_calendar()
            self.content = layout


        def set_today(self, instance):
            self.selected_date = datetime.now()
            self.month_label.text = self.get_month_year()
            self.create_calendar()
            self.date_button.text = self.selected_date.strftime(self.date_format)
            self.dismiss()

        def get_month_year(self):
            return self.selected_date.strftime("%B %Y")

        def create_calendar(self):
            self.calendar_layout.clear_widgets()
            year = self.selected_date.year
            month = self.selected_date.month
            _, last_day = calendar.monthrange(year, month)
            for day in range(1, last_day + 1):
                button = Button(text=str(day), size_hint_y=None, height=40)
                button.bind(on_press=self.select_date)
                self.calendar_layout.add_widget(button)

        def select_date(self, instance):
            day = int(instance.text)
            self.selected_date = self.selected_date.replace(day=day)
            self.date_button.text = self.selected_date.strftime(self.date_format)
            self.dismiss()

        def change_month(self, instance):
            if instance.text == '<':
                self.selected_date = self.selected_date.replace(day=1) - timedelta(days=1)
            else:
                _, last_day = calendar.monthrange(self.selected_date.year, self.selected_date.month)
                self.selected_date = self.selected_date.replace(day=last_day) + timedelta(days=1)
            self.month_label.text = self.get_month_year()
            self.create_calendar()

    class SummaryScreen(ScrollView):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.orientation = 'vertical'
            self.padding = dp(10)

            print("Initializing SummaryScreen")
            self.layout = BoxLayout(orientation='vertical', spacing=dp(30), size_hint_y=None)
            self.layout.bind(minimum_height=self.layout.setter('height'))
            self.add_widget(self.layout)

            self.date_button = Button(text=datetime.now().strftime("%Y-%m-%d"), size_hint_y=None, height=dp(40))
            self.date_button.bind(on_press=self.show_calendar_popup)
            self.layout.add_widget(self.date_button)

            self.calories_consumed_label = MDLabel(halign='center')
            self.layout.add_widget(self.calories_consumed_label)

            self.calories_burned_label = MDLabel(halign='center')
            self.layout.add_widget(self.calories_burned_label)

            self.total_calories_label = MDLabel(halign='center')
            self.layout.add_widget(self.total_calories_label)

            self.expected_calories_label = MDLabel(halign='center')
            self.layout.add_widget(self.expected_calories_label)

            self.protein_consumed_label = MDLabel(halign='center')
            self.layout.add_widget(self.protein_consumed_label)

            self.expected_protein_label = MDLabel(halign='center')
            self.layout.add_widget(self.expected_protein_label)


            self.layout.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))

            self.warning_label = MDLabel(halign='center', theme_text_color='Custom', text_color=(1, 0, 0, 1))
            self.layout.add_widget(self.warning_label)

            print("SummaryScreen initialized")

        def show_calendar_popup(self, instance):
            print("Showing calendar popup")
            popup = HomePage7.CalendarPopup(self.date_button)
            popup.bind(on_dismiss=self.on_calendar_popup_dismiss)
            popup.open()

        def on_calendar_popup_dismiss(self, instance):
            print("Calendar popup dismissed")
            self.load_summary(self.date_button.text)
            self.calculate_tdee()

        def load_summary(self, selected_date):
            print(f"Loading summary for date: {selected_date}")
            calories_consumed = self.get_calories_consumed(selected_date)
            protein_consumed = self.get_protein_consumed(selected_date)
            calories_burned = self.get_calories_burned(selected_date)
            total_calories = round(calories_consumed - calories_burned, 2)

            self.calories_consumed_label.text = f"Calories Consumed: {calories_consumed}"
            self.protein_consumed_label.text = f"Protein Consumed: {protein_consumed}g"
            self.calories_burned_label.text = f"Calories Burned: {calories_burned}"
            self.total_calories_label.text = f"Today's Caloric Total: {total_calories}"

            try:
                caloric_split = self.expected_calories_label.text.split('Caloric Goal: ')
                if len(caloric_split) > 1:
                    expected_calories = int(caloric_split[1].strip())
                else:
                    expected_calories = 0
                    print("Caloric goal label is improperly formatted or missing.")

                protein_split = self.expected_protein_label.text.split('Expected Protein: ')
                if len(protein_split) > 1:
                    expected_protein = int(protein_split[1].strip('g'))
                else:
                    expected_protein = 0
                    print("Protein goal label is improperly formatted or missing.")

                print(f"Parsed expected calories: {expected_calories}, expected protein: {expected_protein}g")


                if total_calories > expected_calories > 0:
                    difference = round(total_calories - expected_calories, 1)
                    self.warning_label.text = f"You are {difference} calories over your caloric goal. " \
                                              "This may result in your goal taking longer to achieve if you continue this habit."
                else:
                    self.warning_label.text = ""


                if protein_consumed < expected_protein and expected_protein > 0:
                    protein_deficit = round(expected_protein - protein_consumed, 1)
                    self.warning_label.text += (f" You are {protein_deficit}g under your protein goal. " \
                                                "Increasing your protein intake is important for muscle growth and repair.")
                elif protein_consumed >= expected_protein:
                    if not self.warning_label.text:
                        self.warning_label.text = ""

            except (ValueError, TypeError) as e:
                print(f"Failed to parse expected goals due to an error: {str(e)}")
                self.warning_label.text = "Error in parsing goal data."

        def calculate_tdee(self):
            try:
                with open('user_profile.json', 'r') as file:
                    user_profile = json.load(file)
                weight = user_profile.get("Weight (lbs)", 0)
                if weight == 0:
                    self.expected_calories_label.text = "Caloric Goal: Weight not specified"
                    print("Weight not specified in user profile.")
                    return


                with open('user_data.json', 'r') as file:
                    user_data = json.load(file)
                current_workout = user_data.get("user_workout", "").lower().strip()
                print(f"Current workout from user data: '{current_workout}'")

                if user_profile["Gender"].lower() == 'female':
                    bmr = 10 * weight / 2.20462 + 6.25 * user_profile["Height (cm)"] - 5 * user_profile["Age"] - 161
                else:
                    bmr = 10 * weight / 2.20462 + 6.25 * user_profile["Height (cm)"] - 5 * user_profile["Age"] + 5
                tdee = int(bmr * 1.55)  # we have to assume a regular activiity daily


                workouts_df = pd.read_csv('workouts2.csv')
                workouts_df['Name'] = workouts_df['Name'].str.lower().str.strip()


                workout_info = workouts_df[workouts_df['Name'] == current_workout]
                if not workout_info.empty:
                    nutrition_info = workout_info.iloc[0]['Nutrition'].lower()
                    print(f"Nutrition info for '{current_workout}': {nutrition_info}")
                    if 'reduce' in nutrition_info:
                        try:
                            reduction = int(nutrition_info.split('reduce')[-1].strip())
                            tdee -= reduction
                            print(f"Caloric reduction of {reduction} calories applied successfully.")
                        except ValueError:
                            print("Failed to parse the reduction amount from nutrition info.")
                    else:
                        print("No 'reduce' keyword found in the Nutrition info for the specified workout.")
                else:
                    print(f"No matching workout found for '{current_workout}' in the workout plan CSV.")


                self.expected_calories_label.text = f"Caloric Goal: {tdee}"

                if user_profile.get("Goal", "").lower() == "build muscle":
                    self.expected_protein_label.text = f"Expected Protein: {weight}g"  # 1g per lb

            except FileNotFoundError as e:
                print(f"File not found: {e}")
                self.expected_calories_label.text = "Caloric Goal: Data not available"
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                self.expected_calories_label.text = "Caloric Goal: Data not available"

        def get_calories_consumed(self, selected_date):
            try:
                with open('calorie_tracker_data.json', 'r') as file:
                    data = json.load(file)
                    if selected_date in data:
                        print(f"Found calorie data for {selected_date}")
                        return sum(
                            float(item[1]) for item in data[selected_date] if item[1].replace('.', '', 1).isdigit())
            except FileNotFoundError:
                print("The file calorie_tracker_data.json does not exist.")
            return 0

        def get_protein_consumed(self, selected_date):
            try:
                with open('calorie_tracker_data.json', 'r') as file:
                    data = json.load(file)
                    if selected_date in data:
                        print(f"Found protein data for {selected_date}")
                        return sum(
                            float(item[2]) for item in data[selected_date] if item[2].replace('.', '', 1).isdigit())
            except FileNotFoundError:
                print("The file calorie_tracker_data.json does not exist.")
            return 0

        def get_calories_burned(self, selected_date):
            try:
                with open('Calories_Burned.json', 'r') as file:
                    data = json.load(file)
                    if selected_date in data:
                        print(f"Found data for calories burned on {selected_date}")
                        return sum(data[selected_date])
            except FileNotFoundError:
                print("The file Calories_Burned.json does not exist.")
            except Exception as e:
                print(f"An error occurred while fetching calories burned: {e}")
            return 0

    class WorkoutScreen(BoxLayout):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.orientation = 'vertical'
            self.date_button = Button(text=datetime.now().strftime("%Y-%m-%d"), size_hint_y=None, height=dp(40))
            self.date_button.bind(on_press=self.show_calendar_popup)
            self.add_widget(self.date_button)

            title_label = MDLabel(text="Completed Exercises", halign='center', size_hint_y=None, height=dp(30))
            self.add_widget(title_label)

            self.exercise_list = ScrollView()

            self.exercise_grid = GridLayout(cols=1, spacing=10, padding=[10, 0], size_hint_y=None)
            self.exercise_grid.bind(minimum_height=self.exercise_grid.setter('height'))
            self.exercise_list.add_widget(self.exercise_grid)
            self.add_widget(self.exercise_list)

            self.load_exercises()

        def show_calendar_popup(self, instance):
            popup = HomePage7.CalendarPopup(self.date_button)
            popup.bind(on_dismiss=lambda instance: self.load_exercises(self.date_button.text))
            popup.open()

        def load_exercises(self, selected_date=None):
            if selected_date is None:
                selected_date = datetime.now().strftime("%Y-%m-%d")
            self.exercise_grid.clear_widgets()
            total_calories = 0

            try:
                with open('completed_workout.json', 'r') as file:
                    exercises = json.load(file)
                    for date_key in exercises:
                        match = re.search(r'\d{4}-\d{2}-\d{2}', date_key)
                        if match and match.group(0) == selected_date:
                            exercise_list = exercises[date_key]
                            i = 0
                            while i < len(exercise_list):
                                item = exercise_list[i]
                                if isinstance(item, str):
                                    if i + 1 < len(exercise_list) and isinstance(exercise_list[i + 1], (int, float)):

                                        calories_burned = exercise_list[i + 1]
                                        i += 1
                                    else:

                                        calories_burned = self.find_calories(item)
                                    self.add_exercise_item(item, calories_burned)
                                    total_calories += float(calories_burned)
                                i += 1
                self.save_total_calories(selected_date, total_calories)
            except FileNotFoundError:
                print("The file completed_workout.json does not exist.")
            except Exception as e:
                print(f"An error occurred while loading exercises: {e}")

        def add_exercise_item(self, exercise_name, calories_burned):
            card = MDCard(spacing=10, padding=8, size_hint=(1, None), height=60, radius=[8], elevation=2)
            hbox = BoxLayout(orientation='horizontal', spacing=10)
            display_text = f"{exercise_name} - Calories Burned: {calories_burned}"
            exercise_label = MDLabel(text=display_text, font_size='14sp', theme_text_color='Primary',
                                     size_hint=(1, None), height=40, halign='left')
            hbox.add_widget(exercise_label)
            card.add_widget(hbox)
            self.exercise_grid.add_widget(card)

        def find_calories(self, exercise_name):
            try:

                with open('user_profile.json', 'r') as file:
                    user_profile = json.load(file)
                gender = user_profile.get("Gender", "Male")


                df = pd.read_csv('all_exercises_final.csv')
                df['Name'] = df['Name'].str.lower()

                normalized_exercise_name = exercise_name.lower()

                calorie_column = 'Calories Burned (Woman)' if gender == "Female" else 'Calories Burned (Man)'


                result = df[df['Name'] == normalized_exercise_name][calorie_column]
                if not result.empty:
                    return result.iloc[0]
                else:
                    return "N/A"
            except FileNotFoundError:
                print("File not found. Ensure the 'user_profile.json' and 'all_exercises_final.csv' exist.")
                return "N/A"
            except Exception as e:
                print(f"An error occurred: {e}")
                return "N/A"

        def save_total_calories(self, date, total_calories):
            try:
                with open('Calories_Burned.json', 'r') as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {}
            data[date] = [total_calories]
            with open('Calories_Burned.json', 'w') as file:
                json.dump(data, file, indent=4)
                print("Total calories burned saved successfully.")

    class CalorieTrackerScreen(GridLayout):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.cols = 1
            self.spacing = dp(10)
            self.padding = dp(10)

            self.date_button = Button(text=datetime.now().strftime("%Y-%m-%d"), size_hint_y=None, height=dp(40))
            self.date_button.bind(on_press=self.show_calendar_popup)
            self.date_button.bind(on_press=lambda instance: self.load_data())

            self.add_widget(self.date_button)

            add_food_button = Button(text="Add Food", size_hint_y=None, height=dp(50))
            add_food_button.bind(on_press=lambda instance: self.add_food_item(instance))
            self.add_widget(add_food_button)

            self.food_layout = ScrollView()
            self.food_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
            self.food_grid.bind(minimum_height=self.food_grid.setter('height'))
            self.food_layout.add_widget(self.food_grid)
            self.add_widget(self.food_layout)

            self.save_button = Button(text="Save", size_hint_y=None, height=dp(40))
            self.save_button.bind(on_press=self.save_meal_entry)
            self.add_widget(self.save_button)


            self.food_items = []
            ai_coach_button = MDRaisedButton(
                text="Get Nutrition Advice",
                size_hint=(None, None),
                size=(dp(200), dp(50)),
                pos_hint={'center_x': 0.5}
            )
            ai_coach_button.bind(on_press=self.show_ai_coach_popup)
            self.add_widget(ai_coach_button)

            self.load_data()

        def show_ai_coach_popup(self, instance):
            popup = Popup(title='Nutrition Advice', size_hint=(None, None), size=(400, 400))
            chat_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            chat_history = ScrollView()
            chat_content = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
            chat_content.bind(minimum_height=chat_content.setter('height'))
            chat_history.add_widget(chat_content)

            user_input = TextInput(size_hint=(1, 0.2), multiline=False)
            send_btn = MDRaisedButton(text='Send', size_hint=(1, 0.1))
            send_btn.bind(on_press=lambda instance: self.process_input(chat_content, user_input.text, user_input))

            chat_layout.add_widget(chat_history)
            chat_layout.add_widget(user_input)
            chat_layout.add_widget(send_btn)

            popup.content = chat_layout
            popup.open()

        def process_input(self, chat_content, user_input, input_widget):

            user_message = f"You: {user_input.strip()}\n"
            popup_width = 400
            text_width = popup_width - dp(40)
            chat_content.add_widget(Label(text=user_message, size_hint_y=None, height=30, font_size='16sp',
                                          color=(1, 1, 1, 1), text_size=(text_width, None), halign='left', valign='top',
                                          markup=True, padding=(10, 10)))
            self.get_nutrition_advice(chat_content, user_input)
            input_widget.text = ''

        def get_nutrition_advice(self, chat_content, question):
            ai_color = (195 / 255, 1, 104 / 255, 1)
            try:

                client = openai.Client(api_key="your key here")
                # key emailed for use"
                base_prompt = """
                 You are a helpful nutrition coach. Your job is to guide users in choosing a food item(s) 
                 that will help them meet their goal or preference. 
                  do not add tags like 'response'. Below is the users question/concern please answer it 
                 to the best of your ability:
                 QUESTION:   
                 """


                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": base_prompt + question}
                    ]
                )



                if response.choices:
                    advice = response.choices[0].message.content
                    popup_width = 400
                    text_width = popup_width - dp(40)
                    advice_label = Label(text=f"AI: {advice}\n", size_hint_y=None, height=30, font_size='16sp',
                                         color=(ai_color), text_size=(text_width, None), halign='left', valign='top',
                                         markup=True, padding=(10, 8))
                    advice_label.bind(texture_size=advice_label.setter('size'))
                    chat_content.add_widget(advice_label)
                else:
                    chat_content.add_widget(
                        Label(text="AI: No response generated.", size_hint_y=None, height=30, font_size='16sp',
                              color=(ai_color)))


            except Exception as e:
                print(f"Error: {e}")
                chat_content.add_widget(
                    Label(text="AI: An error occurred while fetching nutrition advice.", size_hint_y=None,
                          height=dp(30), font_size='16sp', color=(ai_color)))

        def show_calendar_popup(self, instance):
            popup = HomePage7.CalendarPopup(self.date_button)
            popup.bind(on_dismiss=lambda instance: self.load_data(self.update_food_items))
            popup.open()

        def add_food_item(self, instance):
            food_item_input = TextInput(hint_text="Food Item", multiline=False)
            calorie_input = TextInput(hint_text="Calories", multiline=False, input_filter="int")
            protein_input = TextInput(hint_text="Protein (g)", multiline=False,
                                      input_filter="float")  # New protein input
            food_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(50))
            remove_button = Button(text="Remove", size_hint=(None, None), size=(dp(100), dp(50)))
            remove_button.bind(on_press=lambda x, layout=food_layout: self.remove_food_item(layout))
            food_layout.add_widget(food_item_input)
            food_layout.add_widget(calorie_input)
            food_layout.add_widget(protein_input)
            food_layout.add_widget(remove_button)
            self.food_grid.add_widget(food_layout)

        def remove_food_item(self, item_layout):
            self.food_grid.remove_widget(item_layout)

        def save_meal_entry(self, instance):
            self.food_items.clear()
            for index, food_layout in enumerate(self.food_grid.children[::-1]):
                food_item_input = None
                calorie_input = None
                protein_input = None
                for widget in food_layout.children:
                    if isinstance(widget, TextInput):
                        hint_text = widget.hint_text.lower()
                        if 'food' in hint_text:
                            food_item_input = widget.text
                        elif 'calorie' in hint_text:
                            calorie_input = widget.text
                        elif 'protein' in hint_text:
                            protein_input = widget.text


                if not calorie_input or not protein_input:
                    nutrition_info = self.query_nutrition_api(food_item_input)
                    if nutrition_info:
                        if not calorie_input:
                            calorie_input = str(nutrition_info.get("calories", "NA"))
                        if not protein_input:
                            protein_input = str(nutrition_info.get("protein_g", "NA"))
                    else:
                        if not calorie_input:
                            calorie_input = "NA"
                        if not protein_input:
                            protein_input = "NA"


                for widget in food_layout.children:
                    if isinstance(widget, TextInput) and 'calorie' in widget.hint_text.lower():
                        widget.text = calorie_input
                    elif isinstance(widget, TextInput) and 'protein' in widget.hint_text.lower() and not widget.text:
                        widget.text = protein_input

                self.food_items.append((food_item_input, calorie_input, protein_input))

            print("Food items saved:", self.food_items)
            self.save_data()

        def query_nutrition_api(self, food_item):
            api_url = 'https://api.api-ninjas.com/v1/nutrition?query={}'.format(food_item)
            api_key = 'Your key here'
            #Enter key emailed here
            try:
                response = requests.get(api_url, headers={'X-Api-Key': api_key})
                if response.status_code == requests.codes.ok:
                    return response.json()[0] if response.json() else None
                else:
                    print("Error:", response.status_code, response.text)
                    return None
            except Exception as e:
                print("Error occurred during API call:", e)
                return None

        def load_data(self, instance=None):
            filename = "calorie_tracker_data.json"
            if os.path.exists(filename):
                with open(filename, "r") as file:
                    data = json.load(file)
                    selected_date = self.date_button.text
                    if selected_date in data:
                        self.food_items = data[selected_date]
                        self.update_food_items()
                    else:
                        self.food_items = []
                        self.update_food_items()

        def save_data(self):
            data = {}
            filename = "calorie_tracker_data.json"
            if os.path.exists(filename):
                with open(filename, "r") as file:
                    data = json.load(file)
            selected_date = self.date_button.text
            data[selected_date] = self.food_items
            with open(filename, "w") as file:
                json.dump(data, file)

        def update_food_items(self, event=None):
            self.food_grid.clear_widgets()
            for food_item, calorie, protein in self.food_items:
                food_item_input = TextInput(hint_text="Food Item", multiline=False, text=food_item)
                calorie_input = TextInput(hint_text="Calories", multiline=False, text=calorie, input_filter="int")
                protein_input = TextInput(hint_text="Protein (g)", multiline=False, text=protein,
                                          input_filter="float")
                food_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=dp(50))
                remove_button = Button(text="Remove", size_hint=(None, None), size=(dp(100), dp(50)))
                remove_button.bind(on_press=lambda x, layout=food_layout: self.remove_food_item(layout))
                food_layout.add_widget(food_item_input)
                food_layout.add_widget(calorie_input)
                food_layout.add_widget(protein_input)
                food_layout.add_widget(remove_button)
                self.food_grid.add_widget(food_layout)

    dataset_file = 'workout_plans2.csv'


    df = pd.read_csv(dataset_file)
    checkbox_states = {}
    card_titles_by_day = {}
    user_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(HomePage7, self).__init__(**kwargs)
        self.card_to_replace = None
        self.add_buttons()
        self.selected_button = None
        self.model = Model3()
        self.animation_event = None
        self.checkbox_states = {}
        self.checkbox_states_file = "completed_workout.pkl"
        self.load_checkbox_states()
        self.last_reset_date = datetime.now().date()
        self.reset_checkboxes_if_week_passed()
        if self.need_to_update_gif_urls():
            self.fetch_and_cache_gif_urls()

    def fetch_and_cache_gif_urls(self):
        """Fetch GIF URLs from the API and update the CSV file."""
        url = "https://exercisedb.p.rapidapi.com/exercises"
        headers = {
            "X-RapidAPI-Key": "5b39f9b1bdmshca723d12e3a8fb7p142a21jsn63673a55e45c",
            "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params={"limit": "3000"})
        if response.status_code == 200:
            exercises_data = response.json()
            self.update_gif_urls_cache(exercises_data)
            self.save_last_update_date(datetime.now().date())
        else:
            print("Error fetching GIF URLs:", response.status_code)

    def update_gif_urls_cache(self, exercises_data):
        """Update the GIF URLs in the existing CSV file."""
        df = pd.read_csv('all_exercises_final.csv')
        gif_urls = {exercise['name'].lower(): exercise['gifUrl'] for exercise in exercises_data}
        df['Name'] = df['Name'].str.lower()
        df['GIF URL'] = df['Name'].map(gif_urls)
        df.to_csv('all_exercises_final.csv', index=False)
        print("GIF URLs updated and cached.")

    def need_to_update_gif_urls(self):
        """Check if the GIF URLs need to be updated by comparing the current date to the last update date."""
        last_update_file = 'last_update_date.txt'
        if not os.path.exists(last_update_file):
            return True
        with open(last_update_file, 'r') as file:
            last_update_date = datetime.strptime(file.read(), '%Y-%m-%d').date()
        return datetime.now().date() > last_update_date

    def save_last_update_date(self, date):

        with open('last_update_date.txt', 'w') as file:
            file.write(date.strftime('%Y-%m-%d'))
        print("Last update date saved:", date.strftime('%Y-%m-%d'))


    def reset_checkboxes_if_week_passed(self):

        current_date = datetime.now().date()

        one_week_ago = current_date - timedelta(weeks=1)


        if self.last_reset_date <= one_week_ago:

            self.reset_all_checkboxes()


            self.last_reset_date = current_date

    def reset_all_checkboxes(self):

        for day, exercises in self.checkbox_states.items():
            # Reset all checkbox states to False
            for exercise_title in exercises:
                self.checkbox_states[day][exercise_title] = False

        # Save the updated checkbox states
        self.save_checkbox_states_to_json()

    def set_custom_date_for_testing(self, custom_date):
        self.last_reset_date = custom_date
        self.reset_checkboxes_if_week_passed()

    def on_stop(self):

        with open(self.checkbox_states_file, "wb") as f:
            pickle.dump(self.checkbox_states, f)

    def on_start(self):

        self.load_checkbox_states()
        # self.reset_checkboxes_if_week_passed()

    def load_checkbox_states(self):
        try:
            with open(self.checkbox_states_file, "rb") as f:
                self.checkbox_states = pickle.load(f)
        except FileNotFoundError:

            self.checkbox_states = {}
        except Exception as e:

            print("Error loading checkbox states:", e)
            self.checkbox_states = {}

    def add_buttons(self):
        days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7']
        for i in days:
            button = MDFlatButton(text=i, theme_text_color="Custom", text_color=(1, 1, 1, 1))
            button.elevation_normal = 0
            button.bind(on_release=self.show_cards)
            # button.bind(on_press=self.set_button_color, on_release=self.reset_button_color)
            button.bind(on_press=self.set_button_color)
            self.ids.category_box.add_widget(button)

    def set_button_color(self, instance):
        if self.selected_button:
            self.selected_button.md_bg_color = [1, 1, 1, 0]
        instance.md_bg_color = get_color_from_hex("#00BCD4")
        self.selected_button = instance

    def show_cards(self, instance):
        self.ids.card_grid.clear_widgets()
        self.show_cards_for_day(instance.text)



    def show_cards_for_day(self, day):
        with open('exercise_data.json', 'r') as json_file:
            exercise_data = json.load(json_file)

        if day in exercise_data:
            for exercise_info in exercise_data[day]:
                exercise_name = next(iter(exercise_info))
                if exercise_name == "Rest":
                    rest_card = Card(text="Rest", image_source='exercise.png')
                    self.ids.card_grid.add_widget(rest_card)
                else:
                    exercise_details = exercise_info[exercise_name]
                    sets, reps = exercise_details["Sets"], exercise_details["Reps"]
                    gif_name = exercise_name.replace(' ', '_') + '.gif'
                    gif_path = f'./gifs/{gif_name}'
                    image_source = get_first_frame_of_gif(gif_path) if os.path.exists(gif_path) else 'exercise.png'
                    card = Card(text=exercise_name, description=f"Sets: {sets}", reps=f"Reps: {reps}",
                                image_source=image_source)
                    card.bind(on_more_selected=self.on_more_selected)
                    card.bind(on_replace_card=self.on_replace_card)
                    card.bind(on_delete_card=self.delete_card)
                    self.add_checkbox_to_card(card, day)
                    self.ids.card_grid.add_widget(card)

    def add_checkbox_to_card(self, card, day):
        card_text = card.text
        if day not in self.checkbox_states:
            self.checkbox_states[day] = {}

        checkbox_state = self.checkbox_states[day].get(card_text, False)
        checkbox_button = MDIconButton(icon="checkbox-marked" if checkbox_state else "checkbox-blank-outline")
        checkbox_button.bind(on_release=lambda instance: self.on_toggle_checkbox(instance, day, card_text))
        card.buttons_layout.add_widget(checkbox_button)

    def on_toggle_checkbox(self, checkbox_button, day, card_text):
        if day not in self.checkbox_states:
            self.checkbox_states[day] = {}
        checkbox_button.icon = "checkbox-marked" if checkbox_button.icon == "checkbox-blank-outline" else "checkbox-blank-outline"

        self.checkbox_states[day][card_text] = checkbox_button.icon == "checkbox-marked"


        for stored_card_text in list(self.checkbox_states[day].keys()):
            if stored_card_text not in [card.text for card in self.ids.card_grid.children]:
                del self.checkbox_states[day][stored_card_text]

        self.save_checkbox_states_to_json()

    def save_checkbox_states_to_json(self):
        checkbox_states_json = {}

        sorted_days = sorted(self.checkbox_states.keys())

        user_start_date = self.user_manager.get_user_start_date()

        if user_start_date:

            for i in range(7):
                day_number = i + 1
                future_date = user_start_date + timedelta(days=i)
                checkbox_states_json[f"Day {day_number}: {future_date.strftime('%Y-%m-%d')}"] = []


        for i, day in enumerate(sorted_days, start=1):

            current_date = user_start_date + timedelta(days=i - 1)
            key = f"Day {i}: {current_date.strftime('%Y-%m-%d')}"


            checked_exercises = [exercise_title for exercise_title, state in self.checkbox_states[day].items() if state]
            if checked_exercises:

                checkbox_states_json[key] = checked_exercises


        with open("completed_workout.json", "w") as json_file:
            json.dump(checkbox_states_json, json_file, indent=4)



    def on_more_selected(self, instance):
        selected_card = instance
        exercise_info_screen = self.manager.get_screen('exercise_info')
        exercise_info_screen.selected_card_text = selected_card.text


        gif_name = selected_card.text.replace(' ', '_') + '.gif'
        gif_path = f'./gifs/{gif_name}'

        if os.path.exists(gif_path):
            gif_frames = self.load_gif_frames(gif_path)
            self.play_gif(gif_frames, exercise_info_screen.ids.gif_image)
        else:
            exercise_info_screen.selected_card_image_source = 'exercise.png'  # Fallback image

        self.manager.current = 'exercise_info'

    def on_replace_card(self, instance):
        self.card_to_replace = instance
        self.manager.current = 'exercise_list'

    def replace_card_with_exercise(self, exercise_name):

        if self.card_to_replace:

            old_title = self.card_to_replace.text

            self.card_to_replace.set_card_text(exercise_name)

            self.update_exercise_titles_json(old_title, exercise_name)
            self.card_to_replace = None
            self.manager.current = 'testpage'

    def update_exercise_titles_json(self, old_title, new_title):
        try:
            with open('exercise_data.json', 'r') as json_file:
                exercise_data = json.load(json_file)
        except FileNotFoundError:
            exercise_data = {}

        print("Old Exercise Title:", old_title)
        print("New Exercise Title:", new_title)


        for day, exercises in exercise_data.items():

            for index, exercise_info in enumerate(exercises):

                if list(exercise_info.keys())[0] == old_title:
                    print("Old Exercise Info:", exercise_info)


                    exercise_data[day][index][new_title] = exercise_data[day][index].pop(old_title)
                    print("New Exercise Info:", exercise_data[day][index])


        with open('exercise_data.json', 'w') as json_file:
            json.dump(exercise_data, json_file, indent=4)

    def delete_card(self, instance):
        card_title = instance.text

        self.ids.card_grid.remove_widget(instance)
        self.remove_exercise_titles_json(card_title)

    def remove_exercise_titles_json(self, card_title):
        try:
            with open('exercise_data.json', 'r') as json_file:
                exercise_data = json.load(json_file)
        except FileNotFoundError:
            return

        for day, exercises in exercise_data.items():

            for index, exercise_info in enumerate(exercises):
                if list(exercise_info.keys())[0] == card_title:

                    del exercise_data[day][index]
                    break


        with open('exercise_data.json', 'w') as json_file:
            json.dump(exercise_data, json_file, indent=4)

    def load_gif_frames(self, gif_path):

        gif_frames = []
        with Image.open(gif_path) as img:
            for frame in ImageSequence.Iterator(img):

                rotated_frame = frame.rotate(180)


                corrected_frame = ImageOps.mirror(rotated_frame)


                rgba_frame = corrected_frame.convert('RGBA')
                gif_frames.append(rgba_frame)
        return gif_frames

    def play_gif(self, gif_frames, widget):

        self.gif_frames = gif_frames
        self.frame_index = 0
        self.widget_to_update = widget
        self.update_texture()


        if self.animation_event:
            Clock.unschedule(self.animation_event)


        self.animation_event = Clock.schedule_interval(self.update_texture, 3.0 / len(gif_frames))

    def update_texture(self, *args):

        if self.frame_index < len(self.gif_frames):
            frame = self.gif_frames[self.frame_index]
            width, height = frame.size
            texture = Texture.create(size=(width, height))
            texture.blit_buffer(frame.tobytes(), colorfmt='rgba', bufferfmt='ubyte')
            self.widget_to_update.texture = texture
            self.frame_index += 1
        else:
            self.frame_index = 0

    def stop_gif(self):

        if self.animation_event:
            Clock.unschedule(self.animation_event)
            self.animation_event = None

