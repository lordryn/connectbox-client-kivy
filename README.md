# ConnectBox Client (Kivy)

A lightweight Python + Kivy client for ConnectBox devices.  
It handles authentication, polling, heartbeat, and (eventually) reverse SSH tunnel setup — all with a visual debug interface.

---

## 🎯 Features

- 🔐 SSH key generation (if missing)
- 📬 Sends auth request to the jump server
- ⏳ Polls for approval status
- 📡 Sends heartbeat pings every 30s
- 🧪 Manual debug buttons for keygen, auth, ping, polling
- 🛠 Built with Kivy for cross-platform GUI support

> Reverse shell/tunnel logic will be added in future versions

---

## 📦 Setup

```bash
git clone https://github.com/youruser/connectbox-client-kivy.git
cd connectbox-client-kivy
pip install -r requirements.txt
python main.py
```

---

## 🧰 Requirements

- Python 3.9+
- `kivy`
- `requests`
- SSH installed and accessible on the system (`ssh-keygen` must work)

---

## 🔧 Configuration

Current jump server:
```
JUMP_SERVER = "http://wcserv.local:5000"
KEY_PATH = ~/.ssh/id_ed25519
```

To change hostname, port, or server:
- Edit `main.py` constants at the top
- Future versions will allow editing via GUI

---

## 📋 Roadmap

- [ ] Add Start/Stop tunnel buttons
- [ ] Launch and manage SSH subprocess
- [ ] Visual tunnel + heartbeat status indicators
- [ ] System tray mode / background support
- [ ] Android APK packaging (Buildozer)
- [ ] Headless fallback mode via web

---

## 🛠️ Authorship & Project Ownership

This project, **ConnectBox™** and associated programs, were designed and developed by Ryan "Lord Ryn" Wheeler.

All system architecture, core code, and workflow logic were authored and tested by the developer, with AI used as a supplementary tool for troubleshooting, formatting, and planning.

Unless otherwise stated, all code and design decisions originate from the project's creator. AI contributions were used only under human supervision and refinement.

For licensing, contributions, or attribution inquiries, contact: lordryn@yahoo.com