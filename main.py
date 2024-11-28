from datetime import datetime
import json
import google.generativeai as genai
from home_controls import HomeController
from speech_recognition import SpeechRecognizer
from text_to_speech import Speaker

class AIA:
    def __init__(self, gemini_api_key):
        # Initialize Gemini AI
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Initialize components
        self.home_controller = HomeController()
        self.speech_recognizer = SpeechRecognizer()
        self.speaker = Speaker()
        
        # Load command mappings
        self.load_commands()

    def load_commands(self):
        with open('commands.json', 'r') as f:
            self.commands = json.load(f)

    async def process_command(self, user_input):
        # Generate response using Gemini
        response = await self.model.generate_content(
            f"Act as a smart home assistant. User says: {user_input}. " +
            "Determine the intent and provide a natural response."
        )
        
        # Parse the response and extract intent
        intent = self.parse_intent(response.text)
        
        # Execute corresponding home automation command
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

    async def run(self):
        print("AIA: Hello! I'm your Advanced Intelligent Assistant. How can I help?")
        
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
