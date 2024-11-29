import webbrowser
import subprocess
import os

class SystemController:
    def __init__(self):
        # Initialize with default browser, fallback to system default if needed
        try:
            self.default_browser = webbrowser.get()
        except webbrowser.Error:
            self.default_browser = webbrowser
        self.temp_file = 'temp_note.txt'
        
    async def open_browser(self, url):
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url.strip()
            print(f"Attempting to open URL: {url}")  # Debug output
            
            # Try multiple methods to open the browser
            if os.name == 'nt':  # Windows
                try:
                    os.startfile(url)
                except:
                    subprocess.Popen(['start', url], shell=True)
            else:  # Mac/Linux
                try:
                    subprocess.Popen(['xdg-open', url])  # Linux
                except:
                    subprocess.Popen(['open', url])  # Mac
            
            return True
        except Exception as e:
            print(f"Error opening browser: {e}")
            # Fallback method
            try:
                webbrowser.open_new_tab(url)
                return True
            except Exception as e2:
                print(f"Fallback method failed: {e2}")
                return False
        
    async def open_notepad(self, content=None):
        if os.name == 'nt':  # Windows
            notepad_path = 'notepad.exe'
            if content:
                try:
                    with open(self.temp_file, 'w') as f:
                        f.write(content)
                    subprocess.Popen([notepad_path, self.temp_file])
                except Exception as e:
                    print(f"Error opening notepad: {e}")
            else:
                subprocess.Popen([notepad_path])
        else:
            print("Notepad functionality is only available on Windows")
            
    def __del__(self):
        # Cleanup temporary file if it exists
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except:
                pass