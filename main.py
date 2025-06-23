from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
import subprocess
import os
import json
import requests
import threading
import time

JUMP_SERVER = "http://wcserv.local:5000"
KEY_PATH = os.path.expanduser("~/.ssh/id_ed25519")
HOSTNAME = os.uname().nodename

class ConnectBoxCore:
    def __init__(self):
        self.pubkey = ""
        self.port = None
        self.heartbeat_active = False

    def generate_key(self):
        if not os.path.exists(KEY_PATH):
            subprocess.run(["ssh-keygen", "-t", "ed25519", "-f", KEY_PATH, "-N", ""])
        with open(KEY_PATH + ".pub") as f:
            self.pubkey = f.read()
        return self.pubkey

    def request_auth(self):
        if not self.pubkey:
            self.generate_key()
        data = {
            "hostname": HOSTNAME,
            "port": 22222,
            "public_key": self.pubkey,
            "notes": "Kivy client test"
        }
        res = requests.post(f"{JUMP_SERVER}/api/request-auth", json=data)
        return res.json()

    def poll_auth(self, callback):
        def poll():
            while True:
                try:
                    r = requests.get(f"{JUMP_SERVER}/api/is-authed", params={"hostname": HOSTNAME})
                    res = r.json()
                    if res.get("status") == "authed":
                        self.port = res.get("port")
                        callback(f"Authorized! Assigned port: {self.port}")
                        break
                    else:
                        callback("Waiting for approval...")
                except Exception as e:
                    callback(f"Error polling: {e}")
                time.sleep(5)
        threading.Thread(target=poll, daemon=True).start()

    def send_ping(self, callback):
        try:
            requests.post(f"{JUMP_SERVER}/api/ping/{HOSTNAME}")
            callback("Ping sent successfully.")
        except Exception as e:
            callback(f"Ping failed: {e}")

class ConnectBoxUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.core = ConnectBoxCore()
        self.status = Label(text="Ready")
        self.add_widget(self.status)

        self.btn_key = Button(text="Generate Key")
        self.btn_key.bind(on_press=self.on_gen_key)
        self.add_widget(self.btn_key)

        self.btn_auth = Button(text="Request Auth")
        self.btn_auth.bind(on_press=self.on_auth)
        self.add_widget(self.btn_auth)

        self.btn_poll = Button(text="Poll Approval")
        self.btn_poll.bind(on_press=self.on_poll)
        self.add_widget(self.btn_poll)

        self.btn_ping = Button(text="Send Ping")
        self.btn_ping.bind(on_press=self.on_ping)
        self.add_widget(self.btn_ping)

    def update_status(self, msg):
        self.status.text = msg
        print(msg)

    def on_gen_key(self, instance):
        pub = self.core.generate_key()
        self.update_status("Key generated.")

    def on_auth(self, instance):
        res = self.core.request_auth()
        self.update_status(f"Auth requested: {res.get('status')}")

    def on_poll(self, instance):
        self.core.poll_auth(self.update_status)

    def on_ping(self, instance):
        self.core.send_ping(self.update_status)

class ConnectBoxApp(App):
    def build(self):
        return ConnectBoxUI()

if __name__ == "__main__":
    ConnectBoxApp().run()
