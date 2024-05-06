
import bcrypt
import psycopg2
from user import UserManager
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivymd.uix.screen import MDScreen
from user import UserManager
Builder.load_string("""
<LoginScreen>:

    MDFloatLayout:
        md_bg_color: 99/255, 210/255, 218/255, 1

        MDLabel:
            text: "Login"
            font_size: "26sp"
            color: 1, 1, 1, 1
            pos_hint: {"center_x": .55, "center_y": .85}

        MDIconButton:
            icon: "account-plus"
            pos_hint: {"top": 1, "right": 1}
            size_hint: None, None
            on_release: root.manager.current = "SignUpScreen"

        MDFloatLayout:
            size_hint_y: 0.75
            canvas:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [50, 50, 0, 0]

            MDLabel:
                text: "Welcome Back To INCLINE"
                font_size: '20sp'
                pos_hint: {"center_x": 0.6, "center_y": .8}

            MDTextField:
                id: username_input
                hint_text: "Username"
                size_hint: (0.8, None)
                pos_hint: {"center_x": 0.5, "center_y": 0.6}
                line_color_focus: [99/255, 210/255, 218/255, 1]

            MDTextField:
                id: password_input
                hint_text: "Password"
                size_hint: (0.8, None)
                pos_hint: {"center_x": 0.5, "center_y": 0.45}
                line_color_focus: [99/255, 210/255, 218/255, 1]
                password: True

            MDRaisedButton:
                text: "Login"
                size_hint: 0.5, None
                md_bg_color: 99/255, 210/255, 218/255, 1
                text_color: 1, 1, 1, 1
                pos_hint: {"center_x": 0.35, "center_y": 0.25}
                on_release: 
                    root.check_credentials(username_input.text, password_input.text)

            MDLabel:
                id: wrong_input
                text: "Wrong username or password"
                pos_hint: {"center_x": 0.6, "center_y": 0.15}
                opacity: 0
""")




class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.db = self.connect_to_db()
        self.user_manager = kwargs.get('user_manager')

    user_manager = ObjectProperty(None)

    def connect_to_db(self):
        rds_host = 'Refer to email
        rds_port = 'Refer to email'
        rds_dbname = 'refer to email'
        rds_user = 'refer to email'
        rds_password = 'refer to email'
        conn_string = f"host={rds_host} port={rds_port} dbname={rds_dbname} user={rds_user} password={rds_password}"
        try:
            conn = psycopg2.connect(conn_string)
            print("Connected to the database!")
            return conn
        except psycopg2.Error as e:
            print("Unable to connect to the database:", e)
            return None

    def on_stop(self):
        # This method should be called when the app is about to close
        if self.db:
            self.db.close()
            self.db = None
            print("Database connection closed as the app is stopping.")

    def show_error_message(self, message):
        self.ids.wrong_input.text = message
        self.ids.wrong_input.opacity = 1

    def check_credentials(self, username, password):
        if not self.db:
            self.show_error_message('Database connection error')
            return

        username = self.ids.username_input.text.strip()
        password = self.ids.password_input.text.encode('utf-8')

        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT userid, password FROM account WHERE username = %s", (username,))
                user_record = cursor.fetchone()
                if user_record:
                    user_id, hashed_password = user_record
                    hashed_password = hashed_password.tobytes() if isinstance(hashed_password, memoryview) else hashed_password
                    if bcrypt.checkpw(password, hashed_password):
                        self.current_user_id = user_id
                        UserManager.get_instance().set_user_id(user_id)
                        cursor.execute("SELECT * FROM profile WHERE userid = %s", (user_id,))
                        profile_record = cursor.fetchone()
                        if profile_record:
                            self.show_error_message('Login successful, redirecting...')
                            self.manager.current = 'testpage'
                        else:
                            self.show_error_message('No profile found, redirecting to setup...')
                            self.manager.current = 'new_setup'
                    else:
                        self.show_error_message('Invalid username or password')
                else:
                    self.show_error_message('Invalid username or password')
        except psycopg2.Error as e:
            print(f"Database query error: {e}")
            self.show_error_message('Database query error')
