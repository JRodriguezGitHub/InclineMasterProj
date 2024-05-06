from datetime import datetime

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.screen import MDScreen

from model3 import Model3

Builder.load_string("""
<NewSetGoals>:
    MDBoxLayout:
        orientation: "vertical"

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"top": 1}
            on_release: root.manager.current = "new_setup"

        MDBoxLayout:
            orientation: 'vertical'
            padding: 30, 0, 30, 30
            spacing: 30
            size_hint_y: 0.1
            MDLabel:
                text: 'Set a Goal'
                font_style: 'H5'
                size_hint_y: None  # Disable size_hint for height
                height: self.texture_size[1]
        ScrollView:
            MDGridLayout:
                cols: 1
                spacing: 20
                padding: 30, 0, 30, 0
                size_hint_y: None
                height: self.minimum_height

                MDLabel:
                    text: 'What is your goal'
                    size_hint_y: None  # Disable size_hint for height
                    height: self.texture_size[1]  # Set height to match the height of the text content
                    text_size: self.width, None

                MDRectangleFlatIconButton:
                    id: goal_button
                    icon: "chevron-right"
                    text: "Select Goal"
                    theme_text_color: "Custom"
                    text_color: "black"
                    line_color: "black"
                    theme_icon_color: "Custom"
                    icon_color: "black"
                    on_release: root.goal_menu()

                MDLabel:
                    text: "How much weight do you want to lose"
                    size_hint_y: None  # Disable size_hint for height
                    height: self.texture_size[1]  # Set height to match the height of the text content
                    text_size: self.width, None
                    font_style: "Caption"

                MDTextField:
                    id: weight_input
                    hint_text: "Enter in pounds"
                    mode: "rectangle"
                    size_hint_x: None
                    width: "150dp"

                MDLabel:
                    text: "Frequency"
                    size_hint_y: None  # Disable size_hint for height
                    height: self.texture_size[1]  # Set height to match the height of the text content
                    text_size: self.width, None

                MDLabel:
                    text: 'How many days can you commit?'
                    size_hint_y: None  # Disable size_hint for height
                    height: self.texture_size[1]  # Set height to match the height of the text content
                    text_size: self.width, None
                    font_style: "Caption"

                MDRectangleFlatIconButton:
                    id: frequency_button
                    icon: "chevron-right"
                    text: "Days/Week"
                    theme_text_color: "Custom"
                    text_color: "black"
                    line_color: "black"
                    theme_icon_color: "Custom"
                    icon_color: "black"
                    on_release: root.frequency_menu()

                MDLabel:
                    text: "Workout Preferences"
                    size_hint_y: None  # Disable size_hint for height
                    height: self.texture_size[1]  # Set height to match the height of the text content
                    text_size: self.width, None

                MDLabel:
                    text: 'What type of split do you prefer?'
                    size_hint_y: None  # Disable size_hint for height
                    height: self.texture_size[1]  # Set height to match the height of the text content
                    text_size: self.width, None
                    font_style: "Caption"

                MDRectangleFlatIconButton:
                    id: workout_split_button
                    icon: "chevron-right"
                    text: "Workout Split"
                    theme_text_color: "Custom"
                    text_color: "black"
                    line_color: "black"
                    theme_icon_color: "Custom"
                    icon_color: "black"
                    on_release: root.split_menu()

                MDBoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: 140

                    MDLabel:
                        text: 'How much time a day can you commit?'
                        size_hint_y: None  # Disable size_hint for height
                        height: self.texture_size[1]  # Set height to match the height of the text content
                        text_size: self.width, None
                        font_style: "Caption"

                    ScrollView:
                        do_scroll_x: True
                        do_scroll_y: False

                        MDBoxLayout
                            id: time_box
                            # orientation: 'horizontal'
                            # padding: 0, 5, 0, 0
                            spacing: 30
                            adaptive_width: True

                MDBoxLayout:

                MDRectangleFlatButton:
                    text: "Done"
                    size_hint: 0.5, None
                    md_bg_color: 99/255, 210/255, 218/255, 1
                    text_color: 1,1,1,1
                    theme_text_color: "Custom"
                    line_color: 99/255, 210/255, 218/255, 1
                    pos_hint: {"center_x": 0.5, "center_y": 0.5}
                    on_release: root.save_goals()
""")


class NewSetGoals(MDScreen):
    selected_goal = StringProperty("")
    frequency = StringProperty("")
    workout_split = StringProperty("")
    user_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(NewSetGoals, self).__init__(**kwargs)
        self.goal_dropdown = DropDown()
        self.frequency_dropdown = DropDown()
        self.workout_split_dropdown = DropDown()
        self.init_dropdown()
        self.freq_dropdown()
        self.split_dropdown()

        self.add_time_buttons()

        self.selected_time = []

        self.model = Model3()

    def init_dropdown(self):
        options = ['Lose Fat', 'Build Muscle']
        for i in options:
            btn = Button(text=i, size_hint_y=None, height="48dp")
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.goal_dropdown.add_widget(btn)

    def goal_menu(self):
        self.goal_dropdown.open(self.ids.goal_button)
        self.ids.goal_button.icon = "chevron-down"

    def select(self, text):
        self.selected_goal = text
        self.ids.goal_button.text = text
        self.goal_dropdown.dismiss()
        self.ids.goal_button.icon = "chevron-right"

    def freq_dropdown(self):

        for i in range(7):
            btn = Button(text=f"{i + 1} days/week", size_hint_y=None, height="48dp")
            btn.bind(on_release=lambda btn: self.select1(btn.text))
            self.frequency_dropdown.add_widget(btn)

    def frequency_menu(self):
        self.frequency_dropdown.open(self.ids.frequency_button)
        self.ids.frequency_button.icon = "chevron-down"

    def select1(self, text):
        self.frequency = text
        self.ids.frequency_button.text = text
        self.frequency_dropdown.dismiss()
        self.ids.frequency_button.icon = "chevron-right"

    def split_dropdown(self):
        options = ['Split', 'Full Body']
        for i in options:
            btn = Button(text=i, size_hint_y=None, height="48dp")
            btn.bind(on_release=lambda btn: self.select2(btn.text))
            self.workout_split_dropdown.add_widget(btn)

    def split_menu(self):
        self.workout_split_dropdown.open(self.ids.workout_split_button)
        self.ids.workout_split_button.icon = "chevron-down"

    def select2(self, text):
        self.workout_split = text
        self.ids.workout_split_button.text = text
        self.workout_split_dropdown.dismiss()
        self.ids.workout_split_button.icon = "chevron-right"

    def add_time_buttons(self):
        level = ["30-45 min", "45-60 min", "60-75 min", "75-90 min"]
        for text in level:
            button = MDRoundFlatButton(
                text=text,
                pos_hint={'center_y': 0.5},
                line_color=(99 / 255, 210 / 255, 218 / 255, 1),
                text_color=(99 / 255, 210 / 255, 218 / 255, 1)
            )
            button.bind(on_press=self.select_time)
            self.ids.time_box.add_widget(button)

    def select_time(self, button):
        if button.text in self.selected_time:
            self.selected_time.remove(button.text)
            button.text_color = (99 / 255, 210 / 255, 218 / 255, 1)
            button.md_bg_color = (0, 0, 0, 0)

        else:
            self.selected_time.append(button.text)
            button.text_color = (1, 1, 1, 1)
            button.md_bg_color = (99 / 255, 210 / 255, 218 / 255, 1)


    def save_goals(self):
        weight = self.ids.weight_input.text

        selected_time = self.selected_time[0]

        user_preferences = {
            'Frequency days/week': self.frequency,
            'Workout Split': self.workout_split,
            'Selected Time': selected_time
        }

        self.user_manager.set_user_preferences(user_preferences)
        self.user_manager.process_user_preferences()


        self.user_manager.set_user_goals(self.selected_goal, weight, self.frequency, self.workout_split)


        self.user_manager.process_frequency()
        self.user_manager.add_weight_loss_scale()

        self.user_manager.save_user_profile()

        self.user_manager.load_user_profile()


        workout = self.model.similarity()

        current_date = datetime.now()

        self.user_manager.set_user_start_date(current_date)
        self.user_manager.set_user_rec_workout(workout)

        self.user_manager.extract_exercises()

        self.manager.current = 'testpage'


    pass