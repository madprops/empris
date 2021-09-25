import os
from rofi import Rofi

r = Rofi()
players = []
names = []
labels = []

class Player:
  def __init__(self, name):
    self.name = name
    label = name.split(".")[0]
    status = os.popen(f"playerctl status -p {name}").read().strip()
    if status == "Playing":
      self.playing = True
    else:
      self.playing = False
    if self.playing:
      label += " (Playing)"      
    self.label = label

def get_players():
  global players
  global names
  global labels

  players = []
  names = []
  labels = []

  result = os.popen("playerctl --list-all").read().strip()
  namelist = result.split("\n")
  
  for name in namelist:
    players.append(Player(name))  
  
  names = [p.name for p in players]
  labels = [p.label for p in players]

def pick_player():
  options = []
  options += labels
  options.append("---------")
  options.append("Pause All")
  index, key = r.select("Which player to play-pause", options)
  if (key == 0):
    if index < len(labels):
      pause_all_except(index)
    else:
      if options[index] == "Pause All":
        pause_all()

def play_pause(index):
  os.popen(f"playerctl -p {names[index]} play-pause")

def pause(index):
  os.popen(f"playerctl -p {names[index]} pause")  

def pause_all_except(current):
  playing = []
  pause_current = True

  for i, player in enumerate(players):
    if i != current:
      if player.playing:
        playing.append(i)
  
  if len(playing) > 0:
    for i in playing:
      pause(i)  
    
    if players[current].playing:
      pause_current = False
  
  if pause_current:
    play_pause(current)

def pause_all():
  for i, player in enumerate(players):
    pause(i)
  
if (__name__ == "__main__"):
  get_players()
  pick_player()