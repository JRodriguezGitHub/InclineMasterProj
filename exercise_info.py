import pandas as pd
from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard



Builder.load_string("""
<ExerciseInfo>:  
    MDBoxLayout:
        orientation: 'vertical'
        MDIconButton:
            icon: "close"
            pos_hint: {"right": 1, "top": 1}
            on_release: root.close_more()

        ScrollView:
            size_hint_y: 0.9
            GridLayout:
                rows: 5
                spacing: "10dp"
                padding: "10dp", 0, "10dp", 0
                size_hint_y: None
                height: self.minimum_height
                canvas.before:
                    Color:
                        rgba: 0.67, 0.52, 0.78, 1

                AsyncImage:
                    id: exercise_image
                    source: root.selected_card_image_source
                    pos_hint: {'center_x': .5}
                    size_hint_y: None
                    height: self.width * 0.4 / self.image_ratio
                    allow_stretch: True
                    keep_ratio: True

                AsyncImage:
                    id: gif_image
                    source: ""  # Initially blank, to be set dynamically
                    pos_hint: {'center_x': .5}
                    size_hint_y: None
                    height: self.width * 0.6 / self.image_ratio
                    allow_stretch: True
                    keep_ratio: True

                MDLabel:
                    id: text_label
                    text: root.selected_card_text
                    halign: 'center'
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None
                    bold: True
                    font_size: "20sp"

                MDLabel:
                    id: instruction
                    text: "desc1"
                    halign: 'center'
                    valign: 'top'
                    size_hint_y: None
                    height: self.texture_size[1]
                    font_size: "14sp"

                MDLabel:
                    id: desc
                    text: ""
                    padding: 5
                    font_size: "14sp"
                    halign: 'center'
                    size_hint_y: None
                    height: self.texture_size[1]

""")
class ExerciseInfo(MDScreen):

    selected_card_text = StringProperty()
    selected_card_image_source = StringProperty()
    exercise_info_df = pd.read_csv('all_exercises_final.csv')

    def __init__(self, **kwargs):
        super(ExerciseInfo, self).__init__(**kwargs)

        self.register_event_type = ''

    def get_exercise_info(self, exercise_names):
        exercise_info_list = []


        for exercise_name in exercise_names:

            exercise_data = self.exercise_info_df[self.exercise_info_df['Name'] == exercise_name]


            if not exercise_data.empty:

                exercise_info = {
                    'Exercise Name': exercise_data['Name'].iloc[0],
                    'Description': exercise_data['Instructions'].iloc[0],

                }

                description = exercise_info['Description']
                description = description[1:-1]
                sentences = [sentence.strip().replace("'", "") for sentence in description.split(",")]
                formatted_description = " ".join(sentences)
                exercise_info['Description'] = formatted_description

                exercise_info_list.append(exercise_info)
            else:
                print(f"No information found for exercise: {exercise_name}")

        return exercise_info_list

    def add_text(self):
        self.ids.exercise_image.source = self.selected_card_image_source
        self.ids.text_label.text = self.selected_card_text


        exercise_name = self.selected_card_text.lower()
        exercise_info = self.get_exercise_info([exercise_name])
        if exercise_info:
            description = exercise_info[0]['Description']
            self.ids.instruction.text = description
        else:
            self.ids.instruction.text = "No description available"

    def on_pre_enter(self, *args):

        self.add_text()

    def close_more(self):
        self.manager.current = 'testpage'

    pass