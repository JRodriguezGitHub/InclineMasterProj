from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.spinner import Spinner
from kivymd.uix.button import MDRoundFlatButton, MDFillRoundFlatButton
from kivymd.uix.screen import MDScreen

from user import UserManager
from sign_up import SignUpScreen

Builder.load_string("""
<NewSetupScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: 0,0,0,30
        spacing: 10
        
        MDBoxLayout:
            size_hint_y: 0.2
            orientation: "vertical"
            padding: 30
            # canvas.before:
            #     Color:
            #         rgba: 99/255, 210/255, 218/255, 1
            #     Rectangle:
            #         size: self.size 
            #         pos: self.pos
            MDLabel:
                text: "Set Up"
                font_style: "H5"
                # theme_text_color: "Custom"
                # text_color: 1,1,1,1
                

        ScrollView:
            size_hint_y: 0.90
            GridLayout:
                cols: 1
                # size_hint_y: 0.9
                size_hint_y: None
                height: self.minimum_height
                spacing: 20
                padding: 30

                MDBoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: 100
                    spacing: 15
                    padding: 5, 5, 5, 10

                    MDLabel:
                        text: "Age"
                        valign: 'top'
                        # font_style: "Subtitle2"
                        # font_size: "15sp" 

                    Spinner:
                        id: age_spinner
                        values: [str(i) for i in range(18, 100)]
                        text: 'Select Age'
                        background_color: (99 / 255, 210 / 255, 218 / 255, 0.8)


                MDBoxLayout:
                    id: gender_box
                    orientation: 'vertical'
                    size_hint_y: None
                    height: 100
                    spacing: 15
                    padding: 5, 5, 5, 10

                    MDLabel:
                        text: "Gender"
                        valign: 'top'

                    Spinner:
                        id: gender_spinner
                        values: ["Male", "Female"]
                        text: 'Select Gender'
                        background_color: (99 / 255, 210 / 255, 218 / 255, 0.8)

                MDBoxLayout:
                    id: height_box
                    orientation: 'vertical'
                    size_hint_y: None
                    height: 100
                    spacing: 15
                    padding: 5, 5, 5, 10

                    MDLabel:
                        text: "Height"
                        valign: 'top'

                    Spinner:
                        id: height_spinner
                        values: ['{}\\'{}\\" ({}cm)'.format(ft, inch, \
                        round(ft * 30.48 + inch * 2.54)) for ft in range(4, 8) \
                        for inch in range(0, 12)]

                        text: 'Select Height'
                        background_color: (99 / 255, 210 / 255, 218 / 255, 0.8)

                MDBoxLayout:
                    id: name_box
                    orientation: 'vertical'
                    size_hint_y: None
                    height: 100
                    spacing: 15
                    padding: 5, 5, 5, 10

                    MDLabel:
                        text: "Weight"
                        valign: 'top'

                    MDBoxLayout:
                        MDTextField:
                            id: weight_input
                            input_filter: 'float'
                            input_type: 'number'
                            hint_text: "Enter your weight in pounds"
                            pos_hint: {"center_x": 0.5, "center_y": 0.3}
                            line_color_focus: [99/255, 210/255, 218/255, 1]

                # MDBoxLayout:
                #     orientation: 'vertical'
                #     size_hint_y: None
                #     height: 100
                #     spacing: 30

                    # MDLabel:
                    #     text: "Where do you workout?"
                    #     valign: 'top'
                    # 
                    # MDBoxLayout:
                    #     id: location_box
                    #     orientation: 'horizontal'
                    #     padding: 0, 5, 0, 0
                    #     spacing: 30

                MDBoxLayout:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: 140
                    # spacing: 30
                    # adaptive_height: True

                    MDLabel:
                        text: "Level"
                        valign: 'top'

                    ScrollView:
                        do_scroll_x: True
                        do_scroll_y: False
                        # cols:2
                        # adaptive_height: True
                        # size_hint_y: 0.3
                        MDBoxLayout
                            id: level_box
                            # orientation: 'horizontal'
                            # padding: 0, 5, 0, 0
                            spacing: 30
                            adaptive_width: True
        
        MDRectangleFlatButton:
            text: "Done"
            size_hint: 0.5, None
            md_bg_color: 99/255, 210/255, 218/255, 1
            text_color: 1,1,1,1
            theme_text_color: "Custom"
            line_color: 99/255, 210/255, 218/255, 1
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            # pos_hint: {"x": 0.5, "y": 0.5}
            on_release: root.save_profile()
            # root.manager.current = "setup"
              
""")


class NewSetupScreen(MDScreen):
    user_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(NewSetupScreen, self).__init__(**kwargs)

        self.add_level_buttons()


        self.selected_level = []

    def add_level_buttons(self):
        level = ["Beginner", "Intermediate"]
        for text in level:
            button = MDRoundFlatButton(
                text=text,
                pos_hint={'center_y': 0.5},
                line_color=(99 / 255, 210 / 255, 218 / 255, 1),
                text_color=(99 / 255, 210 / 255, 218 / 255, 1)
            )
            button.bind(on_press=self.select_level)
            self.ids.level_box.add_widget(button)

    def select_level(self, button):
        if button.text in self.selected_level:
            self.selected_level.remove(button.text)
            button.text_color = (99 / 255, 210 / 255, 218 / 255, 1)
            button.md_bg_color = (0, 0, 0, 0)

        else:
            self.selected_level.append(button.text)
            button.text_color = (1, 1, 1, 1)
            button.md_bg_color = (99 / 255, 210 / 255, 218 / 255, 1)


    def save_profile(self):
        age = self.ids.age_spinner.text
        gender = self.ids.gender_spinner.text
        height = self.ids.height_spinner.text
        weight = self.ids.weight_input.text
        level = ', '.join(self.selected_level)

        profile_data = {
            "Age": int(age),
            "Gender": gender,
            "Height (cm)": height,
            "Weight (lbs)": int(weight),
            "Experience Level": level
        }


        self.user_manager.set_user_profile(profile_data)
        self.user_manager.process_height()
        self.user_manager.add_user_groups()
        self.user_manager.save_user_profile()


        user_id = self.user_manager.get_user_id()
        if user_id:
            self.user_manager.save_profile_to_db(user_id, age, gender, height, int(weight), level)


        self.manager.current = "setupgoals"




    pass
