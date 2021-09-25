import os
import sys
from pyrofi import Rofi

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

def get_playing():
  playing = []

  for i, player in enumerate(players):
    if player.playing:
      playing.append(i)
      
  return playing

def show_menu():
  options = []
  options += labels
  options.append("---------")
  options.append("Pause All")
  options.append("Next Track")
  options.append("Prev Track")

  selected = 0
  playing = get_playing()
  if len(playing) > 0:
    selected = playing[0]

  header = "Which player to play-pause"
  index, key = r.select(header, options, select = selected, singleclick = True)

  if (key == 0):
    if index < len(labels):
      pause_all_except(index)
    else:
      if options[index] == "Pause All":
        pause_all()
      elif options[index] == "Next Track":
        go_next()
      elif options[index] == "Prev Track":
        go_prev()

def play_pause(index):
  os.popen(f"playerctl -p {names[index]} play-pause")

def pause(index):
  player = players[index]
  if player.playing:
    os.popen(f"playerctl -p {names[index]} pause")

def pause_all_except(current):
  playing = get_playing()
  pause_current = True

  if len(playing) > 0:
    for i in playing:
      if i != current:
        pause(i)

    if players[current].playing:
      pause_current = False

  if pause_current:
    play_pause(current)

def pause_all():
  for i, player in enumerate(players):
    pause(i)

def go_next():
  for player in players:
    if player.playing:
      os.popen(f"playerctl -p {player.name} next")
      return

def go_prev():
  for player in players:
    if player.playing:
      os.popen(f"playerctl -p {player.name} previous")
      return

if (__name__ == "__main__"):
  mode = ""
  if len(sys.argv) > 1:
    mode = sys.argv[1]

  get_players()
  if mode == "pauseall":
    pause_all()
  elif mode == "next":
    go_next()
  elif mode == "prev":
    go_prev()
  else:
    show_menu()