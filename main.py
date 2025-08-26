from pynput import keyboard
import json
import time
import random
import datetime
import threading
import os
from termcolor import colored
import sys

solve_file = "august.json"
session_num = 1
session = f"session{session_num}"
events = ["3x3", "2x2", "4x4", "5x5", "6x6", "7x7", "skewb", "pyra"]
solving = False
starting = False
prev_stats = []
time_stats = []
times = []
formatted_times = [time / 1000 for time in times] if times else []
scramble = None
in_main = True
time_check = False
event = "3x3"
choice = None

def save_data(time_stats):
    global solve_file
    try:
        with open(solve_file) as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = {}

    if session not in data:
        data[session] = []

    data[session].append(time_stats)
    prev_stats.append(time_stats)

    with open(solve_file, "w") as f:
        json.dump(data, f, indent=4)

def gen_scramble():
    scramble = []
    scramble_len = random.randint(25, 28)
    last_move = []
    moves = ["R", "L", "U", "D", "F", "B"]
    dirs = ["", "2", "'"]
    for _ in range(scramble_len):
        if len(last_move) > 2:
            last_move.pop(0)
        move = random.choice(moves)
        while move in last_move:
            move = random.choice(moves)
        direction = random.choice(dirs)
        scramble.append(move + direction)
        last_move.append(move.upper())

    return scramble

def load_data(solve_file):
    global times
    try:
        with open(solve_file) as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
            data = {}
    
    solves = data.get(session)
    if solves:
        for solve in solves:
            time = solve[0][1] + solve[0][0]
            times.append(time)
            prev_stats.append(solve)
    else:
        times = []

def timer_start():
    global solving, time_stats, scramble
    start_time = time.time()
    while solving:
        current_time = time.time()
        print(round(current_time - start_time, 3), end="\r")
        time.sleep(0.01)
    result = current_time - start_time
    time_stats = [[0, int(result * 1000 / 10) * 10], [" ".join(scramble.copy())], "", int(datetime.datetime.now().timestamp())]

    solve_check(time_stats, result)

def solve_check(time_stats, result):
    global times, in_main, time_check, choice
    choice = None
    time_check = True
    in_main = False
    os.system('cls' if os.name == 'nt' else 'clear')

    print(round(result, 3))
    print("2 -> +2 Penalty")
    print("3 -> DNF")
    print("Enter -> Continue")

    while True:
        if choice in ('2', '3', ''):
            break
        time.sleep(0.01)

    if choice == "2":
        time_stats[0][0] = 2000
    elif choice == "3":
        time_stats[0][0] = -1
    else:
        pass

    time_check = False
    save_data(time_stats)

    t = get_time(time_stats)
    times.append(t)

    print_data()

def on_press(key):
    global solving, starting, time_check, choice
    if key == keyboard.Key.space:
        if in_main:
            if not solving:
                starting = True
                print(colored("0.000", 'green'), end="\r")
                return
            else:
                solving = False
    if time_check:
        if key == keyboard.Key.enter:
            choice = ''
    try:
        if key.char == 'q':
            view_stats()
        if key.char == 'e':
            print_data()
        if time_check:
            if key.char == '2':
                choice = '2'
            elif key.char == '3':
                choice = '3'
    except Exception:
        pass
   
def on_release(key):
    global solving, starting
    if key == keyboard.Key.space:
        if starting and not solving:
            solving = True
            threading.Thread(target=timer_start).start()
            starting = False

def get_time(solve):
    penalty = solve[0][0]
    base_time = solve[0][1]

    if penalty == -1:
        return None
    return base_time + penalty

def calculate_avgs(solves, n):
    last_n = solves[-n:]
    dnfs = sum(1 for time in last_n if time is None)
    if dnfs >= 2:
        return "DNF"
    
    avg = [time if time is not None else float('inf') for time in last_n]

    min_time = min(time for time in avg if time != float('inf'))
    max_time = max(avg)
    wca_avg = sum(avg) - min_time - max_time

    return round(wca_avg / (n - 2), 3)

def view_stats():
    global prev_stats, in_main
    in_main = False
    os.system('cls' if os.name == 'nt' else 'clear')
    for i, solve in enumerate(prev_stats, 1):
        time = get_time(solve)
        if time is None:
            time = "DNF"
        else:
            time = round(time / 1000, 3)
        scramble = " ".join(solve[1])
        date = datetime.datetime.fromtimestamp(solve[3]).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i}) {colored(time, 'green')} | {colored(scramble, 'yellow')} | {colored(date, 'magenta')}")
    print("\ne -> Return")

def print_data():
    global scramble, formatted_times, time_stats, in_main
    in_main = True
    os.system('cls' if os.name == 'nt' else 'clear')

    formatted_times = []

    single = None
    ao5 = None
    ao12 = None
    prev_solve = None

    for time in times:
        formatted_times.append(time / 1000 if time is not None else None)

    if formatted_times:
        prev_solve = formatted_times[-1]
        if not prev_solve:
            prev_solve = "DNF"
        try:
            single = min([time for time in formatted_times if time is not None])
        except:
            single = "DNF"

    if len(formatted_times) >= 5:
        ao5 = calculate_avgs(formatted_times, 5)
        if ao5 is None:
            ao5 = "DNF"
    if len(formatted_times) >= 12:
        ao12 = calculate_avgs(formatted_times, 12)

    print(f"----------------- {colored(session, 'red')} -------------------")
    print(f"{colored("Previous", 'grey',)} - {prev_solve}    {colored("PB", 'cyan')} - {single}    {colored("Ao5", 'blue')} - {ao5}    {colored("Ao12", 'blue')} - {ao12}")
    print(f"---------------------------------------------")

    if time_stats:
        if time_stats[0][0] == -1:
            print("dude how can you dnf a solve. smh")
        elif time_stats[0][0] == 2000:
            print("cmon really, +2s dont count at home")
        else:
            print("okay you took the +2s dont count at home seriously didnt you")

    scramble = gen_scramble()
    print()
    print(colored(" ".join(scramble), 'yellow'))
    print("\n0.000", end="\r")

if __name__ == "__main__":
    try:
        data = load_data(solve_file)
        print_data()
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        listener.join()
    except KeyboardInterrupt:
        print("Exiting..")
        os._exit(0)