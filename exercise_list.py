import csv

from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen

from kivymd.icon_definitions import md_icons
from kivymd.app import MDApp
from kivymd.uix.list import OneLineIconListItem, OneLineListItem
from kivymd.uix.screen import MDScreen

Builder.load_string(
    '''

<ExerciseListItem>

    # IconLeftWidget:
    #     icon: root.icon
    #     
    MDLabel:
        text: root.exercise_name

<ExerciseList>
    MDBoxLayout:
        MDIconButton:
            icon: "close"
            pos_hint: {"right": 1, "top": 1}
            on_release: root.close_replace()

    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        padding: dp(20)

        MDBoxLayout:
            adaptive_height: True

            MDIconButton:
                icon: 'magnify'

            MDTextField:
                id: search_field
                hint_text: 'Search exercise'
                on_text: root.search_exercises(self.text, True)

        RecycleView:
            id: rv
            key_viewclass: 'viewclass'
            key_size: 'height'

            RecycleBoxLayout:
                padding: dp(10)
                default_size: None, dp(48)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
'''
)


class ExerciseListItem(OneLineListItem):
    exercise_name = StringProperty()



    def on_release(self):
        app = MDApp.get_running_app()
        app.root.get_screen('testpage').replace_card_with_exercise(self.exercise_name)


class ExerciseList(MDScreen):

    def __init__(self, **kwargs):
        super(ExerciseList, self).__init__(**kwargs)
        self.load_exercises()
        # self.close_replace()

    def load_exercises(self, text="", search=False):
        self.ids.rv.data = []
        with open('all_exercises_final.csv',
                  newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                exercise_name = row[1]
                self.ids.rv.data.append({
                    'viewclass': 'ExerciseListItem',
                    'text': exercise_name,
                    'exercise_name': exercise_name
                })

    def search_exercises(self, text="", search=False):

        self.ids.rv.data = []
        with open('all_exercises_final.csv',
                  newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                exercise_name = row[1]
                if text.lower() in exercise_name.lower():
                    self.ids.rv.data.append({
                        'viewclass': 'ExerciseListItem',
                        'text': exercise_name,
                        'exercise_name': exercise_name
                    })

    def select_exercise(self, exercise_name):

        homepage = self.manager.get_screen('testpage')

        homepage.replace_card_with_exercise(exercise_name)

    def close_replace(self):
        self.manager.current = 'testpage'
