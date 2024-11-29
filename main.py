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
        # Try multiple possible locations for commands.json
        possible_paths = [
            'commands.json',  # Same directory
            'AIA/commands.json',  # AIA subdirectory
            '../commands.json',  # Parent directory
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    self.commands = json.load(f)
                return
                
        raise FileNotFoundError("Could not find commands.json in any expected location")

    async def process_command(self, user_input):
        # Generate response using Gemini
        prompt = f"""You are AIA, an advanced AI assistant that can:
            1. Control smart home devices:
               - Lights (on/off in any room)
               - Thermostat (set temperature, change mode)
               - Security system (arm/disarm, check cameras)
               - Smart appliances (TV, music, etc.)
            2. Web browser actions:
               - Open websites
               - Search information
               - Check weather
               - Play videos
               - Access news
            3. Create and edit content
            
            Previous context: {self.conversation_history}
            User says: {user_input}
            
            Respond naturally and include specific actions in your response:
            - For devices, mention the exact device and action
            - For browser, include the URL or search term
            - Keep responses concise but helpful
            """
        
        response = self.model.generate_content(prompt)
        text = response.text.lower()
        
        # Handle smart device commands
        if any(device in text for device in ['lights', 'thermostat', 'security', 'camera', 'tv']):
            intent = self.parse_intent(text)
            if intent in self.commands:
                await self.home_controller.execute_command(self.commands[intent])
        
        # Enhanced browser handling
        if any(action in text.lower() for action in ['search', 'open browser', 'go to', 'watch', 'play', 'show']):
            # Handle image searches
            if 'image' in text.lower() or 'images' in text.lower():
                search_query = text.lower().replace('show me', '').replace('search for', '').replace('images', '').replace('image', '').strip()
                await self.system_controller.open_browser(f'https://www.google.com/search?q={search_query}&tbm=isch')
            # Handle website URLs
            elif 'open' in text.lower() and ('website' in text.lower() or 'site' in text.lower()):
                website = text.lower().replace('open', '').replace('website', '').replace('site', '').strip()
                if 'acertinity' in website:
                    await self.system_controller.open_browser('https://acertinity.com')
                else:
                    # Add more specific website mappings here
                    await self.system_controller.open_browser(f'https://www.{website}.com')
            # Handle general searches
            else:
                search_query = self.extract_search_query(text)
                if search_query:
                    await self.system_controller.open_browser(f'https://www.google.com/search?q={search_query}')
        
        # Store conversation and return response
        self.conversation_history += f"\nUser: {user_input}\nAIA: {response.text}\n"
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
        
    def extract_search_query(self, text):
        # Extract search terms after "search for" or "look up"
        search_indicators = ['search for', 'look up', 'find', 'search']
        for indicator in search_indicators:
            if indicator in text:
                query = text.split(indicator, 1)[1].strip()
                return query.replace(' ', '+')
        return None

    async def run(self):
        try:
            greeting = "Hello! I'm your Advanced Intelligent Assistant. How can I help?"
            print(f"AIA: {greeting}")
            await self.speaker.speak(greeting)
            
            while True:
                try:
                    # Listen for voice input or accept text input
                    user_input = await self.speech_recognizer.listen()
                    
                    if user_input.lower() in ["exit", "quit", "bye"]:
                        print("AIA: Goodbye! Have a great day!")
                        await self.speaker.speak("Goodbye! Have a great day!")
                        return  # Gracefully exit the loop
                        
                    # Process the command
                    response = await self.process_command(user_input)
                    
                    # Speak and display the response
                    print(f"AIA: {response}")
                    await self.speaker.speak(response)
                    
                except Exception as e:
                    print(f"Error in main loop: {e}")
                    
        except KeyboardInterrupt:
            print("\nAIA: Shutting down gracefully...")
        finally:
            # Cleanup code
            if hasattr(self, 'speaker'):
                self.speaker.engine.stop()
            print("AIA: Goodbye!")

if __name__ == "__main__":
    import asyncio
    try:
        assistant = AIA()
        asyncio.run(assistant.run())
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Ensure proper cleanup
        print("Shutting down...")
