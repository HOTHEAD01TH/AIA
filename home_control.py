class HomeController:
    def __init__(self):
        self.devices = {
            'lights': {
                'living_room': False, 
                'bedroom': False, 
                'kitchen': False,
                'bathroom': False,
                'office': False
            },
            'thermostat': {
                'temperature': 20, 
                'mode': 'auto',
                'humidity': 45,
                'fan': 'auto'
            },
            'security': {
                'armed': False, 
                'cameras': True,
                'motion_sensors': True,
                'door_locks': True
            },
            'entertainment': {
                'tv': False,
                'music': False,
                'volume': 50,
                'current_app': None
            }
        }
    
    async def execute_command(self, command):
        device_type = command.get('device')
        action = command.get('action')
        location = command.get('location', None)
        
        if device_type in self.devices:
            if device_type == 'lights':
                self.devices['lights'][location] = (action == 'on')
            elif device_type == 'thermostat':
                if action == 'set':
                    self.devices['thermostat']['temperature'] = command.get('value')
            elif device_type == 'security':
                self.devices['security']['armed'] = (action == 'arm')
