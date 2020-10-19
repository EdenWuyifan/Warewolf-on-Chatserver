"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
import json
import character

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.gaming_state = ''
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.role = ''

    def set_state(self, state):
        self.state = state
    
    def set_gaming_state(self, gaming_state):
        self.gaming_state = gaming_state

    def get_state(self):
        return self.state
    
    def get_gaming_state(self):
        return self.gaming_state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me
    
    def set_role(self,role):
        self.role = role
    
    def get_role(self):
        return self.role
    
    def set_gstatus(self,gstatus):
        self.gstatus = gstatus
    
    def get_gstatus(self):
        return self.gstatus

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def gaming_with(self,peer):
        msg = json.dumps({"action":"game", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You\'ve invited '+ self.peer + ' to your game\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot play with yourself\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def game_start(self):
        me = self.get_myname()
        mysend(self.s, json.dumps({"action":"start"}))

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:

                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"search", "target":term}))
                    search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    # print(poem)
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'


                elif my_msg[0] == 'g':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.gaming_with(peer) == True:
                        self.state = S_START
                        self.out_msg += 'Add ' + peer + ' to the game!\n\n'
                        self.out_msg += 'Type "start" to start the game\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Invatation unsuccessful\n'


                else:
                    self.out_msg += menu

                    

            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                elif peer_msg["action"] == "game":
                    self.peer = peer_msg["from"]
                    self.out_msg += 'You\'ve been invited to ' + self.peer + '\'s game\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_START
                elif peer_msg["action"] == "notenough":
                    self.out_msg += "There's not enough players in the room to start a game(at least 4)."

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                mysend(self.s, json.dumps({"action":"exchange", "from":"[" + self.me + "]", "message":my_msg}))
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                elif peer_msg["action"] == "exchange":
                    self.out_msg += peer_msg["from"] + peer_msg["message"]
                    
        elif self.state == S_START:
            if len(my_msg) > 0: 
                if my_msg == 'start':
                    try:
                        self.game_start()
                        self.out_msg += "Game started!\n"
                        self.out_msg += "----------------------------------------\n" 
                        send_back = json.loads(myrecv(self.s))
                        self.out_msg += "Your role is: " + send_back["role"] + ", and you are now " \
                        + send_back["status"] + '\n'
                        self.set_role(send_back["role"])
                        self.set_gstatus(send_back["status"])
                        self.state = S_GAMING
                        self.out_msg += "Night is coming, please close your eyes... \n-----------------------------------\n"
                        if self.get_role() == "wolf":
                            self.set_gaming_state("action")
                            mysend(self.s, json.dumps({"action":"checkPartner"}))
                            back = json.loads(myrecv(self.s))
                            self.out_msg += back["message"]
                            if back["result"] == "group":
                                self.out_msg += "Now please chat with your partners and decide a player to kill.\n"
                            elif back["result"] == "alone":
                                self.out_msg += "Now please decide a player to kill.\n"
                            mysend(self.s, json.dumps({"action":"listAlive"}))
                            logged_in = json.loads(myrecv(self.s))["results"]
                            self.out_msg += "Now gaming: " + logged_in + '\n'
                            self.out_msg += '''To kill a player, type "KILL" + player's name. \n-----------------------------------\n'''
                        else:
                            self.set_gaming_state("asleep")
                    except:
                        self.out_msg += "There's not enough players in the room to start a game(at least 4)."
                else:
                    mysend(self.s, json.dumps({"action":"listAlive"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Now in game: " + logged_in + '\n'
                    self.out_msg += 'Type "start" to start the game\n'
                    self.out_msg += '-----------------------------------\n'
            
            if len(peer_msg) > 0:
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "start":
                    self.out_msg += "Game started! \n----------------------------------------\n"
                    self.out_msg += "Your role is: " + peer_msg["role"] + ", and you are now " + peer_msg["status"] + '\n'
                    self.set_role(peer_msg["role"])
                    self.set_gstatus(peer_msg["status"])
                    self.state = S_GAMING
                    self.out_msg += "Night is coming, please close your eyes...\n----------------------------------------\n"
                    if self.get_role() == "wolf":
                        self.set_gaming_state("action")
                        mysend(self.s, json.dumps({"action":"checkPartner"}))
                        back = json.loads(myrecv(self.s))
                        self.out_msg += back["message"]
                        if back["result"] == "group":
                            self.out_msg += "Now please chat with your partners and decide a player to kill.\n"
                        elif back["result"] == "alone":
                            self.out_msg += "Now please decide a player to kill.\n"
                        mysend(self.s, json.dumps({"action":"listAlive"}))
                        logged_in = json.loads(myrecv(self.s))["results"]
                        self.out_msg += "Now gaming: " + logged_in + '\n'
                        self.out_msg += '''To kill a player, type "KILL" + player's name.\n-----------------------------------\n'''
                    else:
                        self.set_gaming_state("asleep")


                    #Prophet's making an action

                        
                        
                elif peer_msg["action"] == "game":
                    self.out_msg += "(" + peer_msg["from"] + " join the game lodge)\n"
                
            
           
        elif self.state == S_GAMING:
            if self.gaming_state == "action":
                
                if len(my_msg) > 0:     # my stuff going out
                    
                    if my_msg[:4] == "KILL":
                        kill = my_msg[4:]
                        kill.strip()
                        self.out_msg += "You have killed " + kill + ", now please go back to sleep.\n-----------------------------------\n"
                        mysend(self.s, json.dumps({"action":"gaming", "round":"kill", "role":self.role, \
                                                "from":"[" + self.me + "]", "message":kill}))
                        send_back = json.loads(myrecv(self.s))
                        if send_back["round"] == "asleep":
                            self.set_gaming_state("asleep")
                        else:
                            self.out_msg += send_back["message"]
                            self.out_msg += "Now please chat with your partners (if any) and decide a player to kill.\n"
                            mysend(self.s, json.dumps({"action":"listAlive"}))
                            logged_in = json.loads(myrecv(self.s))["results"]
                            self.out_msg += "Now gaming: " + logged_in + '\n'
                            self.out_msg += '''To kill a player, type "KILL" + player's name.\n-----------------------------------\n'''

                    #prophet's instructions
                    elif my_msg[:5] == "CHECK":
                        check = my_msg[5:]
                        check.strip()
                        if len(check) == 0:
                            self.out_msg += "Choose a player to see his/her role (type the name of the player): \n"
                            mysend(self.s, json.dumps({"action":"listAlive"}))
                            logged_in = json.loads(myrecv(self.s))["results"]
                            self.out_msg += "Now gaming: " + logged_in + '\n'
                            self.out_msg += 'Type "CHECK" + player\'s name to check their identity.\n-----------------------------------\n'
                        else:
                            mysend(self.s, json.dumps({"action":"gaming", "round":"check", "role":self.role, \
                                                        "from":"[" + self.me + "]", "message":check}))
                            send_back = json.loads(myrecv(self.s))["message"]
                            self.out_msg += check + " is a " + send_back + "\n-----------------------------------\n"
                            self.set_gaming_state("asleep")
                    #witch's instructions
                    elif my_msg[:6] == "POISON":
                        poison = my_msg[6:]
                        poison.strip()
                        mysend(self.s, json.dumps({"action":"gaming", "round":"poison", "role":self.role, \
                                                    "from":"[" + self.me + "]", "message":poison}))
                        send_back = json.loads(myrecv(self.s))
                        if send_back["round"] == "skip":
                            self.out_msg += send_back["message"]
                            self.set_gaming_state("asleep")
                        else:
                            if send_back["round"] == "poison":
                                self.out_msg += send_back["message"]
                            mysend(self.s, json.dumps({"action":"checkWitch"}))
                            back = json.loads(myrecv(self.s))
                            if back["cure"] == 1:
                                death = back["death"]
                                self.out_msg += death + '\n'
                                self.out_msg += '"CURE" + player\'s name to cure a player ("SKIPC" to skip).\n-----------------------------------\n'
                            else:
                                self.out_msg += "You have used up your cure.\nNow go back to sleep.\n-----------------------------------\n."
                                mysend(self.s, json.dumps({"action":"gaming", "round":"cure", "role":self.role, \
                                                "from":"[" + self.me + "]", "message":"useup"}))
                                self.set_gaming_state("asleep")

                    elif my_msg[:4] == "CURE":
                        cure = my_msg[4:]
                        cure.strip()
                        mysend(self.s, json.dumps({"action":"gaming", "round":"cure", "role":self.role, \
                                                    "from":"[" + self.me + "]", "message":cure}))
                        
                        send_back = json.loads(myrecv(self.s))["message"]
                        if send_back == "FAIL":
                            self.out_msg += "Curing failed. Please check your input name. \n"
                            self.out_msg += '"CURE" + player\'s name to cure a player ("SKIPC" to skip).\n-----------------------------------\n'
                        else:
                            self.out_msg += send_back
                        self.set_gaming_state("asleep")

                    
                    elif my_msg[:5] == "SKIPP":
                        mysend(self.s, json.dumps({"action":"gaming", "round":"poison", "role":self.role, \
                                                "from":"[" + self.me + "]", "message":"skip"}))
                        send_back = json.loads(myrecv(self.s))
                        self.out_msg += send_back["message"]
                        mysend(self.s, json.dumps({"action":"checkWitch"}))
                        send_back = json.loads(myrecv(self.s))
                        if send_back["cure"] == 1:
                            death = send_back["death"]
                            self.out_msg += death + '\n'
                            self.out_msg += '"CURE" + player\'s name to cure a player ("SKIPC" to skip).\n-----------------------------------\n'
                        else:
                            self.out_msg += "You have used up your cure.\nNow go back to sleep.\n-----------------------------------\n."
                            mysend(self.s, json.dumps({"action":"gaming", "round":"cure", "role":self.role, \
                                                "from":"[" + self.me + "]", "message":"useup"}))
                            self.set_gaming_state("asleep")
                    elif my_msg[:5] == "SKIPC":
                        mysend(self.s, json.dumps({"action":"gaming", "round":"cure", "role":self.role, \
                                                "from":"[" + self.me + "]", "message":"skip"}))
                        send_back = json.loads(myrecv(self.s))["message"]
                        self.out_msg += send_back
                        self.set_gaming_state("asleep")
                    else:
                        mysend(self.s, json.dumps({"action":"gaming", "round":"action", "role":self.role, \
                                                "from":"[" + self.me + "]", "message":my_msg}))

                        
                if len(peer_msg) > 0:    # peer's stuff, coming in
                    peer_msg = json.loads(peer_msg)
                    if peer_msg["round"] == "action" and peer_msg["role"] == "wolf":
                        self.out_msg += peer_msg["from"] + peer_msg["message"]
                    elif peer_msg["round"] == "asleep":
                        if self.get_role() == "wolf":
                            self.out_msg += "You have killed " + peer_msg["message"] + ", now please go back to sleep.\n" + "\n-----------------------------------\n"
                        else:
                            self.out_msg += peer_msg["message"]
                        self.set_gaming_state("asleep")
                    elif peer_msg["round"] == "discuss":
                        self.set_gaming_state("discussion")
                        mysend(self.s, json.dumps({"action":"gaming", "round":"discussion","from":"[" + self.me + "]", "message":""}))
                        self.out_msg += peer_msg["message"]
                        self.out_msg += "Now start the discussion: (type 'FIN' to finish)\n-----------------------------------\n"
                    elif peer_msg["round"] == "end":
                        self.out_msg += peer_msg["message"]
                        self.state = S_LOGGEDIN
                        self.disconnect()
                        self.peer = ''
                    elif peer_msg["round"] == "poison":
                        if self.get_role() == peer_msg["role"]:
                            self.set_gaming_state("action")
                            self.out_msg += peer_msg["message"]
                            if self.get_role() == "witch":
                                mysend(self.s, json.dumps({"action":"checkWitch"}))
                                send_back = json.loads(myrecv(self.s))
                                if send_back["cure"] == 1:
                                    death = send_back["death"]
                                    self.out_msg += death + '\n'
                                    self.out_msg += '"CURE" + player\'s name to cure a player ("SKIPC" to skip).\n-----------------------------------\n'
                                else:
                                    self.out_msg += "You have used up your cure.\nNow go back to sleep.\n-----------------------------------\n."
                                    mysend(self.s, json.dumps({"action":"gaming", "round":"cure", "role":self.role, \
                                                "from":"[" + self.me + "]", "message":"useup"}))
                                    self.set_gaming_state("asleep")
                    
                        
            elif self.gaming_state == "asleep":
                if len(my_msg) > 0:
                    self.out_msg += "You are not allowed to talk right now!"
                if len(peer_msg) > 0:
                    peer_msg = json.loads(peer_msg)
                    if peer_msg["round"] == "action":
                         if self.get_role() == peer_msg["role"]:
                            self.out_msg += peer_msg["message"]
                            if self.get_role() == "prophet":
                                self.out_msg += "Choose a player to see his/her role (type the name of the player): \n"
                                mysend(self.s, json.dumps({"action":"listAlive"}))
                                logged_in = json.loads(myrecv(self.s))["results"]
                                self.out_msg += "Now gaming: " + logged_in + '\n'
                                self.out_msg += 'Type "CHECK" + player\'s name to check their identity.\n-----------------------------------\n'
                                self.set_gaming_state("action")
                            if self.get_role() == "witch":
                                mysend(self.s, json.dumps({"action":"checkWitch"}))
                                logged_in = json.loads(myrecv(self.s))
                                self.out_msg += "Now gaming: " + logged_in["results"] + '\n'
                                if logged_in["poison"] == 1:
                                    self.out_msg += '"POISON" + player\'s name to poison a player ("SKIPP" to skip).\n-----------------------------------\n'
                                    self.set_gaming_state("action")
                                else:
                                    self.out_msg += "You have used up your poison.\n"
                                    if logged_in["cure"] == 1:
                                        self.out_msg += logged_in["death"] + '\n'
                                        self.out_msg += '"CURE" + player\'s name to cure a player ("SKIPC" to skip).\n-----------------------------------\n'
                                        self.set_gaming_state("action")
                                    else:
                                        self.out_msg += "You have used up your cure.\nNow go back to sleep.\n-----------------------------------\n"
                                        mysend(self.s, json.dumps({"action":"gaming", "round":"cure", "role":self.role, \
                                                "from":"[" + self.me + "]", "message":"useup"}))
                    elif peer_msg["round"] == "discuss":
                        self.set_gaming_state("discussion")
                        mysend(self.s, json.dumps({"action":"gaming", "round":"discussion","from":"[" + self.me + "]", "message":""}))
                        self.out_msg += peer_msg["message"]
                        self.out_msg += "Now start the discussion: (type 'FIN' to finish)\n-----------------------------------\n"
                    elif peer_msg["round"] == "end":
                        self.out_msg += peer_msg["message"]
                        self.state = S_LOGGEDIN
                        self.disconnect()
                        self.peer = ''
                    elif peer_msg["round"] == "asleep":
                        self.out_msg += peer_msg["message"]
                        self.set_gaming_state("asleep")
                        

            elif self.gaming_state == "discussion":
                if len(my_msg) > 0:
                    if my_msg == "FIN":
                        #self.gaming_state = "poll"
                        mysend(self.s, json.dumps({"action":"gaming", "round":"poll",\
                                               "from":"[" + self.me + "]", "message":my_msg}))
                    else:
                        mysend(self.s, json.dumps({"action":"gaming", "round":"discussion",\
                                               "from":"[" + self.me + "]", "message":my_msg}))
                    
                        
                if len(peer_msg) > 0:
                    peer_msg = json.loads(peer_msg)
                    if peer_msg["round"] == "end":
                        self.out_msg += peer_msg["message"]
                        self.state = S_LOGGEDIN
                        self.disconnect()
                        self.peer = ''
                    #POLL
                    elif peer_msg["round"] == "poll":
         
                        self.set_gaming_state("poll")
                        #self.gaming_state = "poll"
                        self.out_msg += "Now comes the poll!\n----------------------------------------------\n"
                        logged_in = peer_msg["result"]
                        self.out_msg += "Now alive: " + logged_in + '\n'
                        self.out_msg += "Please type the player name here:"
                        mysend(self.s, json.dumps({"action":"gaming", "round":"poll",\
                                               "from":"[" + self.me + "]", "message":my_msg}))
                      
    
                    elif peer_msg["round"] == "vote_result":
                        if peer_msg["round"] == "vote_result":
                            self.out_msg += peer_msg["message"]
                            self.out_msg += "Night is coming, please close your eyes...\n"
                        if self.get_role() == "wolf":
                            mysend(self.s, json.dumps({"action":"checkAlive"}))
                            result = json.loads(myrecv(self.s))
                            if result["results"] == "alive":
                                self.set_gaming_state("action")
                                mysend(self.s, json.dumps({"action":"checkPartner"}))
                                back = json.loads(myrecv(self.s))
                                self.out_msg += back["message"]
                                if back["result"] == "group":
                                    self.out_msg += "Now please chat with your partners and decide a player to kill.\n"
                                elif back["result"] == "alone":
                                    self.out_msg += "Now please decide a player to kill.\n"
                                mysend(self.s, json.dumps({"action":"listAlive"}))
                                logged_in = json.loads(myrecv(self.s))["results"]
                                self.out_msg += "Now gaming: " + logged_in + '\n'
                                self.out_msg += '''To kill a player, type "KILL" + player's name.\n'''
                        else:
                            self.set_gaming_state("asleep")
                    elif peer_msg["round"] == "asleep":
                        self.out_msg += peer_msg["message"]
                        self.set_gaming_state("asleep")
                    else:
                        self.out_msg += peer_msg["from"] + peer_msg["message"]
            elif self.gaming_state == "poll":
                if len(my_msg) > 0:
                    mysend(self.s, json.dumps({"action":"gaming", "round":"poll",\
                                               "from":"[" + self.me + "]", "message":my_msg}))
                if len(peer_msg) > 0:
                    peer_msg = json.loads(peer_msg)
                    if peer_msg["round"] == "vote_result":
                        self.out_msg += peer_msg["message"]
                        self.out_msg += "Night is coming, please close your eyes...\n----------------------------------------\n"
                        if self.get_role() == "wolf":
                            mysend(self.s, json.dumps({"action":"checkAlive"}))
                            result = json.loads(myrecv(self.s))
                            if result["results"] == "alive":
                                self.set_gaming_state("action")
                                mysend(self.s, json.dumps({"action":"checkPartner"}))
                                back = json.loads(myrecv(self.s))
                                self.out_msg += back["message"]
                                if back["result"] == "group":
                                    self.out_msg += "Now please chat with your partners and decide a player to kill.\n"
                                elif back["result"] == "alone":
                                    self.out_msg += "Now please decide a player to kill.\n"
                                mysend(self.s, json.dumps({"action":"listAlive"}))
                                logged_in = json.loads(myrecv(self.s))["results"]
                                self.out_msg += "Now gaming: " + logged_in + '\n'
                                self.out_msg += '''To kill a player, type "KILL" + player's name.\n----------------------------------------\n'''
                            else:
                                self.out_msg += "The dead are not allowed to execute.\n----------------------------------------\n"
                                self.set_gaming_state("asleep")
                        else:
                            self.set_gaming_state("asleep")
                    elif peer_msg["round"] == "repoll":
                        self.set_gaming_state("poll")
                        self.out_msg += peer_msg["message"] + "\n----------------------------------------------\n"
                        self.out_msg += "Now alive: " + peer_msg["result"] + '\n'
                        self.out_msg += "Please type the player name here:"
                        mysend(self.s, json.dumps({"action":"gaming", "round":"poll",\
                                               "from":"[" + self.me + "]", "message":my_msg}))
                    elif peer_msg["round"] == "asleep":
                        self.out_msg += peer_msg["message"]
                        self.set_gaming_state("asleep")
                    elif peer_msg["round"] == "end":
                        self.out_msg += peer_msg["message"]
                        self.state = S_LOGGEDIN
                        self.disconnect()
                        self.peer = ''
                    else:
                        self.out_msg += peer_msg["message"]
            
            else:        
                if len(peer_msg) > 0:    # peer's stuff, coming in
                    peer_msg = json.loads(peer_msg)
                    if peer_msg["action"] == "connect":
                        self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                    elif peer_msg["action"] == "disconnect":
                        self.state = S_LOGGEDIN
                    elif peer_msg["action"]== "gaming":
                        self.out_msg += peer_msg["from"] + peer_msg["message"]
                    elif peer_msg["round"] == "end":
                        self.out_msg += peer_msg["message"]
                        self.state = S_LOGGEDIN
                        self.disconnect()
                        self.peer = ''
                
                


            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
