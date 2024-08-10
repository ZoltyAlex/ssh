import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
import paramiko

class SSHApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.password_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=40)
        self.password_input = TextInput(
            hint_text='Enter SSH Password',
            password=True,
            multiline=False,
            background_color=[0.7, 0.7, 0.7, 1],
            foreground_color=[0, 0, 0, 1],
            cursor_color=[0, 0, 0, 1],
            size_hint=(None, None),
            width=200,
            height=40
        )
        self.password_layout.add_widget(Label(size_hint=(None, None), width=100))
        self.password_layout.add_widget(self.password_input)
        self.password_layout.add_widget(Label(size_hint=(None, None), width=100))

        self.layout.add_widget(self.password_layout)

        self.connect_button = Button(text='Connect to Server')
        self.connect_button.bind(on_press=self.connect_to_server)
        self.layout.add_widget(self.connect_button)

        self.shutdown_button = Button(text='Shutdown Server', disabled=True)
        self.shutdown_button.bind(on_press=self.shutdown_server)
        self.layout.add_widget(self.shutdown_button)

        self.reboot_button = Button(text='Reboot Server', disabled=True)
        self.reboot_button.bind(on_press=self.reboot_server)
        self.layout.add_widget(self.reboot_button)

        return self.layout

    def connect_to_server(self, instance):
        hostname = '192.168.0.32'
        port = 22
        username = 'root'
        password = self.password_input.text

        if not password:
            self.show_popup("Error", "Password cannot be empty")
            return

        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname, port, username, password)

            self.show_popup("Success", "Connected successfully")
            self.shutdown_button.disabled = False
            self.reboot_button.disabled = False

        except Exception as e:
            self.show_popup("Connection Error", f"{str(e)}\nPlease check your connection settings.")

    def execute_ssh_command(self, command):
        try:
            full_command = f'echo {self.password_input.text} | sudo -S {command}'
            stdin, stdout, stderr = self.client.exec_command(full_command)

            output = stdout.read().decode()
            error = stderr.read().decode()

            if error:
                self.show_popup("Error", error)
            else:
                self.show_popup("Success", "Command executed successfully")

        except Exception as e:
            self.show_popup("Command Execution Error", str(e))

    def shutdown_server(self, instance):
        self.execute_ssh_command('shutdown -h now')

    def reboot_server(self, instance):
        self.execute_ssh_command('reboot')

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    def on_stop(self):
        if hasattr(self, 'client') and self.client:
            self.client.close()

if __name__ == '__main__':
    SSHApp().run()
