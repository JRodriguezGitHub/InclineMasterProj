
from kivy.core.window import Window


from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivymd.app import MDApp

from user import UserManager
from login import LoginScreen
from testpage import HomePage7
from sign_up import SignUpScreen
from new_setup import NewSetupScreen
from new_set_goals import NewSetGoals
from exercise_info import ExerciseInfo
from exercise_list import ExerciseList


user_manager = UserManager.get_instance()

Window.size = (360, 640)


class WorkoutApp(MDApp):
    def on_stop(self):
        # Save checkbox states when the app is stopped
        current_screen = self.root.current_screen
        if hasattr(current_screen, "on_stop"):
            current_screen.on_stop()

        login_screen = self.root.get_screen('login')
        if login_screen.current_user_id is not None:
            print(f"Resetting user ID for user: {login_screen.current_user_id}")
        login_screen.current_user_id = None
        print("App is stopping and user ID has been reset.")

    def on_start(self):

        current_screen = self.root.current_screen
        if hasattr(current_screen, "on_start"):
            current_screen.on_start()

    def build(self):

        self.screen_manager = ScreenManager(transition=FadeTransition())

        self.screen_manager.add_widget(LoginScreen(name="login", user_manager=user_manager))
        self.screen_manager.add_widget(SignUpScreen(name="SignUpScreen", user_manager=user_manager))

        self.screen_manager.add_widget(NewSetupScreen(name="new_setup", user_manager=user_manager))
        self.screen_manager.add_widget(NewSetGoals(name="setupgoals", user_manager=user_manager))

        self.screen_manager.add_widget(HomePage7(name="testpage", user_manager=user_manager))
        self.screen_manager.add_widget(ExerciseInfo(name="exercise_info"))
        self.screen_manager.add_widget(ExerciseList(name="exercise_list"))


        return self.screen_manager



if __name__ == '__main__':
    app = WorkoutApp()
    app.run()
