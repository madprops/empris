import os
import sys

class PlayerList:
  def __init__(self):
    self.players = []
  
  def add_player(self, player):
    self.players.append(player)   

  def get_labels(self):
    return [p.label for p in self.players]
  
  def get_playing(self):
    playing = []
    for i, player in enumerate(self.players):
      if player.playing:
        playing.append(i)
    return playing
  
  def name(self, index):
    return self.players[index].name

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
  splist = os.popen("playerctl --list-all") \
    .read().strip().split("\n")

  for name in splist:
    playerlist.add_player(Player(name))

def show_menu():
  options = []
  options += playerlist.get_labels()
  options.append("---------")
  options.append("Pause All")
  options.append("Next Track")
  options.append("Prev Track")
  items = "\n".join(options)

  selected = 0
  playing = playerlist.get_playing()
  if len(playing) > 0:
    selected = playing[0]

  prompt = "Select Player"
  ans = os.popen(f"echo '{items}' | rofi -dmenu -p '{prompt}' -format i \
                -selected-row {selected} -me-select-entry ''\
                -me-accept-entry 'MousePrimary'").read().strip()
  
  if ans == "":
    return
  
  index = int(ans)

  if index < len(playerlist.players):
    pause_all_except(index)
  else:
    if options[index] == "Pause All":
      pause_all()
    elif options[index] == "Next Track":
      go_next()
    elif options[index] == "Prev Track":
      go_prev()

def toggleplay(index):
  player = playerlist.players[index]
  if player.playing:
    pause(index)
  else:
    play(index)

def play(index):
  player = playerlist.players[index]
  if not player.playing:
    os.popen(f"playerctl -p {playerlist.name(index)} play").read()

def pause(index):
  player = playerlist.players[index]
  if player.playing:
    os.popen(f"playerctl -p {playerlist.name(index)} pause").read()

def pause_all_except(index):
  player = playerlist.players[index]
  playing = playerlist.get_playing()

  for i, _ in enumerate(playerlist.players):
    if i != index:
      pause(i)

  if len(playing) > 1:
    if not player.playing:
      play(index)
  else:
    toggleplay(index)
      
def pause_all():
  for i, _ in enumerate(playerlist.players):
    pause(i)

def go_next():
  for player in playerlist.players:
    if player.playing:
      os.popen(f"playerctl -p {player.name} next").read()
      return

def go_prev():
  for player in playerlist.players:
    if player.playing:
      os.popen(f"playerctl -p {player.name} previous").read()
      return

if (__name__ == "__main__"):
  playerlist = PlayerList()

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