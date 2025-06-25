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
        self.heartbeat_thread = None
        self.ssh_process = None

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

    def start_heartbeat(self, callback):
        if self.heartbeat_active:
            callback("Heartbeat already running.")
            return

        self.heartbeat_active = True
        def loop():
            while self.heartbeat_active:
                self.send_ping(callback)
                time.sleep(30)
        self.heartbeat_thread = threading.Thread(target=loop, daemon=True)
        self.heartbeat_thread.start()
        callback("Heartbeat started.")

    def stop_heartbeat(self, callback):
        if not self.heartbeat_active:
            callback("Heartbeat is not running.")
            return
        self.heartbeat_active = False
        callback("Heartbeat stopped.")

    def start_tunnel(self, callback):
        if self.ssh_process:
            callback("Tunnel already running.")
            return
        if not self.port:
            callback("No port assigned. Cannot start tunnel.")
            return
        try:
            self.ssh_process = subprocess.Popen([
                "ssh", "-i", KEY_PATH,
                "-o", "StrictHostKeyChecking=no",
                "-N", "-R", f"{self.port}:localhost:22",
                f"ryn@wcserv.local"
            ])
            callback("Tunnel started.")
        except Exception as e:
            callback(f"Tunnel failed: {e}")

    def stop_tunnel(self, callback):
        if self.ssh_process:
            self.ssh_process.terminate()
            self.ssh_process = None
            callback("Tunnel stopped.")
        else:
            callback("No tunnel to stop.")

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

        self.btn_start_hb = Button(text="Start Heartbeat")
        self.btn_start_hb.bind(on_press=self.on_start_heartbeat)
        self.add_widget(self.btn_start_hb)

        self.btn_stop_hb = Button(text="Stop Heartbeat")
        self.btn_stop_hb.bind(on_press=self.on_stop_heartbeat)
        self.add_widget(self.btn_stop_hb)

        self.btn_start_tunnel = Button(text="Start Tunnel")
        self.btn_start_tunnel.bind(on_press=self.on_start_tunnel)
        self.add_widget(self.btn_start_tunnel)

        self.btn_stop_tunnel = Button(text="Stop Tunnel")
        self.btn_stop_tunnel.bind(on_press=self.on_stop_tunnel)
        self.add_widget(self.btn_stop_tunnel)

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

    def on_start_heartbeat(self, instance):
        self.core.start_heartbeat(self.update_status)

    def on_stop_heartbeat(self, instance):
        self.core.stop_heartbeat(self.update_status)

    def on_start_tunnel(self, instance):
        self.core.start_tunnel(self.update_status)

    def on_stop_tunnel(self, instance):
        self.core.stop_tunnel(self.update_status)

class ConnectBoxApp(App):
    def build(self):
        return ConnectBoxUI()

if __name__ == "__main__":
    ConnectBoxApp().run()
