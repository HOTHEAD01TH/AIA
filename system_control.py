import webbrowser
import subprocess
import os

class SystemController:
    def __init__(self):
        self.default_browser = webbrowser.get()
        
    async def open_browser(self, url):
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.default_browser.open(url)
        
    async def open_notepad(self, content=None):
        if os.name == 'nt':  # Windows
            notepad_path = 'notepad.exe'
            if content:
                temp_file = 'temp_note.txt'
                with open(temp_file, 'w') as f:
                    f.write(content)
                subprocess.Popen([notepad_path, temp_file])
            else:
                subprocess.Popen([notepad_path])