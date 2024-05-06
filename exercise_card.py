from kivy.event import EventDispatcher
from kivy.properties import StringProperty
from kivy.uix.image import AsyncImage
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu


class Card(MDCard, EventDispatcher):
    text = StringProperty()
    image_source = StringProperty()
    description = StringProperty()
    reps = StringProperty()

    # checked = BooleanProperty(defaultvalue=False)  # Add a checked attribute

    def __init__(self, **kwargs):
        super(Card, self).__init__(**kwargs)

        self.size_hint_x = 1
        self.size_hint_y = None
        self.height = 150

        self.style = "elevated"

        self.register_event_type('on_more_selected')
        self.register_event_type('on_replace_card')
        self.register_event_type('on_delete_card')

        self.orientation = "horizontal"
        self.padding = "10dp"

        self.image = AsyncImage(source=self.image_source, size_hint=(None, 1)
                                )
        self.add_widget(self.image)


        self.layout = MDGridLayout(

            cols=1,
            padding=(10, 0, 0, 0), spacing=0)


        self.title_label = MDLabel(text=self.text, halign="left", valign="top")
        self.layout.add_widget(self.title_label)


        self.description_label = MDLabel(text=self.description, halign="left", valign="top")
        self.layout.add_widget(self.description_label)

        self.reps_label = MDLabel(text=self.reps, halign="left", valign="top")
        self.layout.add_widget(self.reps_label)


        self.add_widget(self.layout)

        self.buttons_layout = MDGridLayout(

            cols=1,

            spacing=0)

        self.buttons_layout.size_hint_x = 0.25

        self.menu_button = MDIconButton(icon="dots-vertical", pos_hint={"top": 1, "right": 1})
        self.menu_button.bind(on_release=self.card_menu)
        self.buttons_layout.add_widget(self.menu_button)



        self.add_widget(self.buttons_layout)




    def card_menu(self, *args):
        menu_text = ["More", "Replace", "Delete"]
        menu_items = [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.menu_callback(x),
            } for i in menu_text
        ]
        self.menu = MDDropdownMenu(
            # caller=self.ids.card_menu,
            caller=self.menu_button,
            items=menu_items,
            width_mult=4,
            position="bottom",
        )
        self.menu.open()

    def menu_callback(self, text_item):
        if text_item == "More":
            self.dispatch('on_more_selected')
            print(text_item)
        elif text_item == "Replace":
            self.dispatch('on_replace_card')
            # self.dispatch('on_exercise_selected')
            print(text_item)
        else:
            self.dispatch('on_delete_card')
            print(text_item)

        if self.menu:
            self.menu.dismiss()

    def on_more_selected(self, *args):
        pass

    def on_replace_card(self, *args):
        pass

    def on_delete_card(self):
        pass

    def set_card_text(self, new_text):
        self.text = new_text
        self.title_label.text = new_text