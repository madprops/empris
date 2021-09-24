import os
import time
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
  index, key = r.select("Which player to play-pause", labels)
  
  if (key == 0):
    play_pause(index)
    time.sleep(0.1)
    get_players()
    pick_player()

def play_pause(index):
  os.popen(f"playerctl -p {names[index]} play-pause")

if (__name__ == "__main__"):
  get_players()
  pick_player()