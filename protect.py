#!/usr/bin/env python3

import os.path

from aes_encryption import AESCipher

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button


class MenuBarWidget(BoxLayout):
    pass

class PasswordWidget(BoxLayout):
    pass

class ProtectApp(App):
    save_location = StringProperty('')
    cipher = AESCipher('')
    default_text = StringProperty('')
    current_editor_text = StringProperty('')
    invalid_password = BooleanProperty('')

    def build(self):
        if self.invalid_password:
            Window.bind(on_touch_down=self.password_alert)
        Window.bind(on_request_close=self.disabled_alert)
        return MenuBarWidget()

    def password_alert(self, *args):
        if self.invalid_password:
            Alert(title='Wrong Password', text='Proceed at your own risk.')
            # unbind after showing once
            Window.unbind(on_touch_down=self.password_alert)
        return True

    def disabled_alert(self, *args):
        Alert(title='Disabled', text='This button is disabled.\nPlease use the other buttons.')
        return True

    def save_file(self):
        # encrypt the text in the editor
        encrypted_text = self.cipher.encrypt(self.current_editor_text)

        # write encrypted text
        with open(self.save_location, 'w') as writer:
            writer.write(str(encrypted_text))

class PasswordApp(App):
    password_key = StringProperty('')
    file_path = ListProperty()
    proceed = BooleanProperty(False)
    default_file = StringProperty('')

    def build(self):
        return PasswordWidget()

    def CheckConditions(self):
        if self.password_key == '':
            Alert(title='Invalid Password', text='Please enter a password')
        elif self.file_path == [] or not os.path.isfile(self.file_path[0]):
            Alert(title='Invalid Selection', text='Please select a file')
        else:
            self.proceed = True
            self.stop()

class Alert(Popup):
    def __init__(self, title, text):
        super(Alert, self).__init__()

        content = AnchorLayout(anchor_x='center', anchor_y='bottom')
        description_label = Label(text=text, halign='center', valign='top')
        ok_button = Button(text='Ok', size_hint=(None, None), size=(Window.width / 10, Window.height / 20))

        content.add_widget(description_label)
        content.add_widget(ok_button)

        popup = Popup(
            title=title,
            content=content,
            size_hint=(None, None),
            size=(Window.width / 3, Window.height / 3),
            auto_dismiss=True,
        )
        ok_button.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    # Create password app class
    password_window = PasswordApp()

    # get a default file selection if present
    if os.path.isfile('default_location.txt'):
        default_file = ''
        with open('default_location.txt', 'r') as reader:
            default_file = reader.read()
            print(default_file)

        if os.path.isfile(default_file) or os.path.isdir(default_file):
            password_window.default_file = default_file

    # run the password app class
    password_window.run()

    # Only run protect editor if file is selected and password is entered
    if password_window.proceed:
        # save chosen file location to
        with open('default_location.txt', 'w') as writer:
            writer.write(password_window.file_path[0])

        # Read the file
        raw_file_text = ''
        with open(password_window.file_path[0], 'r') as reader:
            raw_file_text = reader.read()

        # Create cipher
        cipher = AESCipher(password_window.password_key)

        # If file contains text decrypt the text and add it to the editor
        decrypted_text = ''
        failed_password = False
        if raw_file_text != '':
            try:
                decrypted_text = cipher.decrypt(raw_file_text)
            except:
                failed_password = True

            if decrypted_text == '':
                failed_password = True

        # Create app object
        protect = ProtectApp()

        # Add decrypted text to the editor
        protect.default_text = decrypted_text
        protect.cipher = cipher
        protect.save_location = password_window.file_path[0]
        protect.invalid_password = failed_password

        # Start the app
        protect.run()