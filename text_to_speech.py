import pyttsx3

class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init()

    async def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"Error speaking: {str(e)}") 