#Role Assign
import random
import character 
import chat_group 

class Players():
    
    def __init__(self):
        self.gaming_group = []
        self.win_side = ''

    def role_assign(self, chat_group):
        #roles for 2 players is just for test
        roles = {3:["villager","wolf","wolf"],\
                 4:["villager","villager", "wolf", "prophet"],\
                 5:['villager', 'villager', 'wolf', 'prophet', 'witch'],\
                 6:['villager','villager', 'wolf', 'prophet', 'witch', 'wolf'],\
                 7:['villager','villager', 'wolf','wolf', 'prophet', 'witch', 'villager'],\
                 8:['villager','villager','villager', 'wolf','wolf', 'prophet', 'witch', 'wolf'],\
                 9:['villager','villager','villager','villager', 'wolf','wolf','wolf', 'prophet', 'witch', 'villager'],\
                 10:['villager','villager','villager','villager', 'wolf','wolf','wolf', 'prophet', 'witch', 'wolf']}
        number = len(chat_group)
        game_roles = roles[number]
        print("Roles in this round: ", game_roles)
        gaming_groups = []
        for player in chat_group:
            c = character.Character(player)
            random.shuffle(game_roles)
            c.set_role(game_roles.pop())
            gaming_groups.append(c)
            
        return gaming_groups
    
    def get_gaming_group(self, chat_group):
        self.gaming_group = self.role_assign(chat_group)
        return self.gaming_group
    
    def judge_result(self,gaming_group):
        alive = {}
        for player in gaming_group:
            if player.get_status() == 'alive':
                alive[player.playerName] = player.get_role()
        if 'wolf' not in alive.values():
            if 'villager' not in alive.values():
                self.win_side = 'no one wins, both villagers and wolves are dead. \n'
                self.status = 'gameover'
                return self.win_side
            else:
                self.win_side = 'villager\n'
                self.status = 'gameover'
                return self.win_side
        elif 'villager' not in alive.values():
            if 'wolf' not in alive.values():
                self.win_side = 'no one wins, both villagers and wolves are dead. \n'
                self.status = 'gameover'
                return self.win_side
            else:
                self.win_side = 'wolf\n'
                self.status = 'gameover'
                return self.win_side
        elif 'prophet' not in alive.values() and 'witch' not in alive.values():
            self.win_side = 'wolves\n'
            self.status = 'gameover'
            return self.win_side
        else:
            return "continue"
        
        
  
            
            
            






    

