from base_dataclass import Base

# inherited class decleration
class TimedMessages(Base):
    
    table_name:str = locals()['__qualname__']
        
    guild_id:str = ''
    toggle:int = -1
    # json('alias' -> [channel_id, period, message])
    alias_to_timed_message_map:dict = {}
    
    meta_data:dict = locals()['__annotations__'] 
    meta_data['super'] = {
        'primary_key': ['guild_id'], 
        'defaults': {
            'toggle': 1
        }
    }
    
    # helper
    def set_data(self):
        self.data = {
            'guild_id': self.guild_id,
            'toggle': self.toggle,
            'alias_to_timed_message_map': self.alias_to_timed_message_map
        }
    
    def load(self):
        self.set_data()
        tmp = self.callback_read(self.table_name, self.data, self.meta_data)
        self.guild_id = tmp[0]
        self.toggle = tmp[1]
        if tmp[2] is not None:
            self.alias_to_timed_message_map = tmp[2]
        else:
            self.alias_to_timed_message_map = {}
    #####

    ### Hidden ###
    def __init__(self) -> None:
        super().__init__()
        self.data = self.set_data()
    
    def create(self):
        self.set_data()
        self.callback_create(self.table_name, self.data, self.meta_data)
    
    def read(self):
        self.set_data()
        return self.callback_read(self.table_name, self.data, self.meta_data)
    
    def update(self):
        self.set_data()
        self.callback_update(self.table_name, self.data, self.meta_data)
    
    def delete(self):
        self.set_data()
        self.callback_delete(self.table_name, self.data, self.meta_data)
    ##############
    
if __name__ == '__main__':
    a = TimedMessages()
    a.create_table(a.table_name, a.meta_data)
    a.guild_id = 'avc'
    a.create()
    print(a.read())