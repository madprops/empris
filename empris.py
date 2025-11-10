from __future__ import annotations

import os
import sys
import time
import subprocess


class Rofi:
    def __init__(self, args: str) -> None:
        self.args = args

    def select(self, prompt: str, options: list[str], selected: int) -> int:
        items = "\n".join(options)

        ans = (
            os.popen(f"echo '{items}' | rofi -dmenu -p '{prompt}' -format i \
            -selected-row {selected} -me-select-entry ''\
            -me-accept-entry 'MousePrimary' {self.args}")
            .read()
            .strip()
        )

        if ans == "":
            return -1

        return int(ans)


class PlayerList:
    def __init__(self) -> None:
        self.icon = "☢️"
        self.players: list[Player] = []

    def add_player(self, player: Player) -> None:
        self.players.append(player)

    def labels(self) -> list[str]:
        return [f"{self.icon} {p.label}" for p in self.players]

    def playing(self) -> list[int]:
        playing = []

        for i, player in enumerate(self.players):
            if player.playing:
                playing.append(i)

        return playing

    def name(self, index: int) -> str:
        return self.players[index].name

    def index(self, name: str) -> int:
        for i, player in enumerate(self.players):
            if name == player.name:
                return i

        return -1

    def empty(self) -> None:
        self.players = []


playerlist = PlayerList()


class Player:
    def __init__(self, name: str) -> None:
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


def get_players() -> None:
    playerlist.empty()
    splist = os.popen("playerctl --list-all").read().strip().split("\n")
    splist.sort()

    for name in splist:
        playerlist.add_player(Player(name))


def show_menu() -> None:
    rofi = Rofi("-font 'sans-serif 16' -theme-str 'window { width: 600px; }'")

    options = []
    options += playerlist.labels()
    options.append("Pause All")
    options.append("Next Track")
    options.append("Prev Track")

    selected = 0
    playing = playerlist.playing()

    if len(playing) > 0:
        selected = playing[0]

    index = rofi.select("Select Player", options, selected)

    if index == -1:
        return

    if index < len(playerlist.players):
        pause_all_except(index)
        toggleplay(index)
    elif options[index] == "Pause All":
        pause_all()
    elif options[index] == "Next Track":
        go_next()
    elif options[index] == "Prev Track":
        go_prev()


def toggleplay(index: int) -> None:
    player = playerlist.players[index]

    if player.playing:
        pause(index)
    else:
        play(index)


def play(index: int) -> None:
    player = playerlist.players[index]

    if not player.playing:
        os.popen(f"playerctl -p {playerlist.name(index)} play").read()


def pause(index: int) -> None:
    player = playerlist.players[index]

    if player.playing:
        os.popen(f"playerctl -p {playerlist.name(index)} pause").read()


def pause_all_except(index: int) -> None:
    for i, _ in enumerate(playerlist.players):
        if i != index:
            pause(i)


def pause_all() -> None:
    for i, _ in enumerate(playerlist.players):
        pause(i)


def go_next() -> None:
    for player in playerlist.players:
        if player.playing:
            os.popen(f"playerctl -p {player.name} next").read()
            return


def go_prev() -> None:
    for player in playerlist.players:
        if player.playing:
            os.popen(f"playerctl -p {player.name} previous").read()
            return


def start_autopause() -> None:
    p = subprocess.Popen(
        [
            "playerctl",
            "status",
            "--follow",
            "-f",
            "autopause - {{playerInstance}} - {{status}}",
        ],
        stdout=subprocess.PIPE,
    )

    if (not p) or (not p.stdout):
        return

    for line in iter(p.stdout.readline, ""):
        item = line.decode("UTF-8").strip()

        if item.startswith("autopause - "):
            split = item.split(" - ")
            name = split[1]
            status = split[2]

            if status == "Playing":
                # This sleep is to avoid conflict
                # When changing players through empris manually
                time.sleep(0.25)
                get_players()
                index = playerlist.index(name)

                if index >= 0:
                    player = playerlist.players[index]

                    if player.playing:
                        pause_all_except(index)


def main() -> None:
    mode = ""

    if len(sys.argv) > 1:
        mode = sys.argv[1]

    if mode == "autopause":
        try:
            start_autopause()
        except KeyboardInterrupt:
            pass
    else:
        get_players()

        if mode == "pauseall":
            pause_all()
        elif mode == "next":
            go_next()
        elif mode == "prev":
            go_prev()
        else:
            show_menu()


if __name__ == "__main__":
    main()
