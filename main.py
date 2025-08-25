from pynput import keyboard
import json
import time
import random
import datetime
import threading
import os
from termcolor import colored

# // Load data --
# // Print data -- 
# // Generate Scramble --
# // Wait for keyboard input --
# // Save data

solve_file = "august.json"
session_num = 21
session = f"session{session_num}"
events = ["3x3", "2x2", "4x4", "5x5", "6x6", "7x7", "skewb", "pyra"]
solving = False
starting = False
time_stats = []
times = []
formatted_times = [time / 100 for time in times] if times else []
scramble = None
event = "3x3"

def save_data(time_stats):
    global solve_file
    try:
        with open(solve_file) as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = {}

    print(data)
    
    if session not in data:
        data[session] = []

    data[session].append(time_stats)

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
        print(f"Loaded {len(solves)} solves")
        times = [solve[0][1] for solve in solves]
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
    time_stats = [[0, int(result * 100)], [" ".join(scramble.copy())], "", int(datetime.datetime.now().timestamp())]

    scramble = gen_scramble()
    solve_check(time_stats, result)

def solve_check(time_stats, result):
    global times
    os.system('cls' if os.name == 'nt' else 'clear')

    print(round(result, 3))
    print("2 -> +2 Penalty")
    print("3 -> DNF")
    print("Enter -> Continue")

    choice = input("").strip()

    if choice == "2":
        time_stats[0][1] += 200
    elif choice == "3":
        time_stats[0][0] = -1
    else:
        pass 
    
    save_data(time_stats)

    times.append(time_stats[0][1])

    print_data()

def on_press(key):
    global solving, starting
    if key == keyboard.Key.space:
        if not solving:
            starting = True
            print(colored("0.000", 'green'), end="\r")
            return
        else:
            solving = False 
            
def on_release(key):
    global solving, starting
    if key == keyboard.Key.space:
        if starting and not solving:
            solving = True
            threading.Thread(target=timer_start).start()
            starting = False

def print_data():
    global scramble, formatted_times
    os.system('cls' if os.name == 'nt' else 'clear')
    formatted_times = [time / 100 for time in times] if times else []


    single = None
    ao5 = None
    ao12 = None
    prev_solve = None

    if formatted_times:
        single = min(formatted_times)
        prev_solve = formatted_times[-1]
    if len(formatted_times) >= 5:
        last5 = formatted_times[-5:]
        ao5 = ((sum(last5) - min(last5) - max(last5)) / 3)
        ao5 = round(ao5, 3)
    if len(formatted_times) >= 12:
        last12 = formatted_times[-12:]
        last12 = ((sum(last12) - min(last12) - min(last12) / 10))
        last12 = round(last12, 3)

    print(f"----------------- {colored(session, 'red')} -------------------")
    print(f"{colored("Previous", 'red')} - {prev_solve}    {colored("PB", 'blue')} - {single}    {colored("Ao5", 'blue')} - {ao5}    {colored("Ao12", 'blue')} - {ao12}")
    print(f"---------------------------------------------")

    scramble = gen_scramble()
    print(" ".join(scramble))
    print("0.000", end="\r")

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