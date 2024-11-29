from datetime import datetime
import json
import google.generativeai as genai
from home_control import HomeController
from speech_handler import SpeechRecognizer
from text_to_speech import Speaker
import os
from dotenv import load_dotenv
from system_control import SystemController

load_dotenv()

class AIA:
    def __init__(self, gemini_api_key=None):
        # Initialize Gemini AI
        if gemini_api_key is None:
            gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            raise ValueError("Gemini API key is required")
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize components
        self.home_controller = HomeController()
        self.speech_recognizer = SpeechRecognizer()
        self.speaker = Speaker()
        
        # Load command mappings
        self.load_commands()
        
        # Add this line after other initializations
        self.conversation_history = ""
        
        # Add this line with other initializations
        self.system_controller = SystemController()

    def load_commands(self):
        with open('AIA/commands.json', 'r') as f:
            self.commands = json.load(f)

    async def process_command(self, user_input):
        # Generate response using Gemini
        response = self.model.generate_content(
            f"""You are a friendly female AI assistant named AIA. You can:
            1. Control smart home devices
            2. Open web browsers with specific URLs
            3. Open notepad and write content
            
            Previous context: {self.conversation_history}
            User says: {user_input}. 
            
            Determine if this is a system command (browser/notepad) or a regular conversation.
            Provide a natural response and indicate any actions needed."""
        )
        
        # Check for system commands
        text = response.text.lower()
        if 'open browser' in text or 'go to' in text:
            url = self.extract_url(text)
            if url:
                await self.system_controller.open_browser(url)
                
        if 'notepad' in text:
            content = self.extract_content(text)
            await self.system_controller.open_notepad(content)
            
        # Store conversation for context
        self.conversation_history += f"\nUser: {user_input}\nAIA: {response.text}\n"
        
        # Parse the intent silently
        intent = self.parse_intent(response.text)
        
        # Execute command if needed
        if intent in self.commands:
            await self.home_controller.execute_command(self.commands[intent])
            
        return response.text

    def parse_intent(self, ai_response):
        # Basic intent parsing - can be enhanced with NLP
        intent = "unknown"
        if "lights" in ai_response.lower():
            intent = "lights"
        elif "temperature" in ai_response.lower():
            intent = "temperature"
        # Add more intent parsing logic
        return intent

    def extract_url(self, text):
        # Basic URL extraction - can be enhanced
        words = text.split()
        for word in words:
            if '.' in word and not word.startswith(('please', 'thank')):
                return word
        return None
        
    def extract_content(self, text):
        # Basic content extraction - can be enhanced
        if 'write' in text:
            start = text.find('write') + 5
            return text[start:].strip()
        return None

    async def run(self):
        greeting = "Hello! I'm your Advanced Intelligent Assistant. How can I help?"
        print(f"AIA: {greeting}")
        await self.speaker.speak(greeting)
        
        while True:
            # Listen for voice input or accept text input
            user_input = await self.speech_recognizer.listen()
            
            if user_input.lower() == "exit":
                break
                
            # Process the command
            response = await self.process_command(user_input)
            
            # Speak and display the response
            print(f"AIA: {response}")
            await self.speaker.speak(response)

if __name__ == "__main__":
    import asyncio
    assistant = AIA()
    asyncio.run(assistant.run())
