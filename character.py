class Character:
    
    def __init__(self, playerName):
        self.playerName = playerName
        self.status = 'alive'
        self.role = ''
        self.poison = 0
        self.cure = 0
        
    def set_status(self,new_status):
        self.status = new_status
        return self.status
        
    def set_role(self,new_role):
        self.role = new_role
        return self.role
    
    def get_status(self):
        return self.status
    
    def get_role(self):
        return self.role



# Functions for the Witch
    def set_poison(self):
        self.poison = 1
    def use_poison(self):
        self.poison = 0
    def get_poison(self):
        return self.poison

    def set_cure(self):
        self.cure = 1
    def use_cure(self):
        self.cure = 0
    def get_cure(self):
        return self.cure
    
    
