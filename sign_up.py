from typing import re

import bcrypt
import re
import psycopg2
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen


from user import UserManager

Builder.load_string("""
<SignUpScreen>:

    MDFloatLayout:
        md_bg_color: 99/255, 210/255, 218/255, 1

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"top": 1}
            size_hint: None, None
            on_release: root.manager.current = "login"

        MDLabel
            text: "Sign Up"
            font_size: "26sp"
            color: 1,1,1,1
            pos_hint: {"center_x": .55, "center_y": .90}

        MDFloatLayout:
            size_hint_y: 0.85
            pos: self.pos
            canvas:
                Color:
                    rgba: 1,1,1,1
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [50, 50, 0, 0]

            MDLabel:
                text: "Create an account"
                font_size: '20sp'
                pos_hint: {"center_x": 0.6, "center_y": .9}

            MDTextField:
                id: username_input
                hint_text: "Enter a username"
                mode: "rectangle"
                size_hint: (0.8, None)
                pos_hint: {"center_x": 0.5, "center_y": 0.75}
                line_color_focus: [99/255, 210/255, 218/255, 1]

            MDTextField:
                id: password_input
                hint_text: "Enter a password"
                size_hint: (0.8, None)
                mode: "rectangle"
                pos_hint: {"center_x": 0.5, "center_y": 0.6}
                line_color_focus: [99/255, 210/255, 218/255, 1]
                password: True

            MDTextField:
                id: confirm_password_input
                hint_text: "Re-enter your password"
                size_hint: (0.8, None)
                mode: "rectangle"
                pos_hint: {"center_x": 0.5, "center_y": 0.45}
                line_color_focus: [99/255, 210/255, 218/255, 1]
                password: True

            MDRaisedButton:
                text: "Sign Up"
                size_hint: 0.5, None
                md_bg_color: 99/255, 210/255, 218/255, 1
                text_color: 1,1,1,1
                pos_hint: {"center_x": 0.35, "center_y": 0.25}
                on_release: root.create_account(username_input.text, password_input.text, confirm_password_input.text)

            MDLabel:
                id: create_message_label
                text: ""
                pos_hint: {"center_x": 0.6, "center_y": 0.18}
                opacity: 0
""")



def go_back(self, instance):
    self.manager.transition.direction = 'right'
    self.manager.current = 'login'


def connect_to_db():
    rds_host = 'refer to email'
    rds_port = 'refer to email'
    rds_dbname = 'refer to email'
    rds_user = 'refer to email'
    rds_password = 'refer to email'

    # Construct the connection string
    conn_string = f"host={rds_host} port={rds_port} dbname={rds_dbname} user={rds_user} password={rds_password}"


    try:
        conn = psycopg2.connect(conn_string)
        print("Connected to the database!")
        return conn
    except psycopg2.Error as e:
        print("Unable to connect to the database:", e)
        return None



class SignUpScreen(MDScreen):
    user_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SignUpScreen, self).__init__(**kwargs)
        self.user_manager = kwargs.get('user_manager')

    def show_message(self, message):
        print(f"Showing message: {message}")
        self.ids.create_message_label.text = message
        self.ids.create_message_label.opacity = 1

    def create_account(self, username, password, confirm_password):
        if password != confirm_password:
            self.show_message("Passwords don't match")
            return

        if not self.validate_password(password):
            self.show_message("Password does not meet the requirements")
            return

        if self.username_exists(username):
            self.show_message("This username already exists")
            return

        self.save_to_database(username, password)

    def username_exists(self, username):
        db = connect_to_db()
        if db is None:
            return True

        with db.cursor() as cursor:
            try:
                cursor.execute("SELECT username FROM account WHERE username = %s", (username,))
                exists = cursor.fetchone() is not None
                print(f"Username exists: {exists}")
                return exists
            except psycopg2.Error as e:
                print(f"Error checking username existence: {e.pgerror}")
                return True
            finally:
                db.close()

    def validate_password(self, password):
        pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+-]).{8,}$')
        valid = pattern.match(password) is not None
        print(f"Password valid: {valid}")
        return valid

    def save_to_database(self, username, password):
        db = connect_to_db()
        if db is None:
            self.show_message('Database connection error')
            return

        hashed_password = self.hash_password(password)
        with db.cursor() as cursor:
            try:
                cursor.execute("INSERT INTO account (username, password) VALUES (%s, %s)", (username, hashed_password))
                db.commit()
                self.show_message("Account created successfully")
            except psycopg2.Error as e:
                self.show_message(f"Error saving to database: {e.pgerror}")
            finally:
                db.close()

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed

    pass




