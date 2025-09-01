from pynput import keyboard
import json
import time
import random
import datetime
import threading
import os
from termcolor import colored

solve_file = "solves.json"
session_num = 1
session = f"session{session_num}"
solving = False
starting = False
prev_stats = []
time_stats = []
times = []
formatted_times = [time / 1000 for time in times] if times else []
EVENTS = [None, "222so", "444wca", "555wca", "666wca", "777wca", "mgmp", "pyrso", "skbso", "sqrs"]
event_index = 0
scramble = None
in_main = True
time_check = False
event = None
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


def load_data(solve_file):
    global times, event
    try:
        with open(solve_file) as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
            data = {}
    
    try:
        session_data_str = data["properties"]["sessionData"]
        session_data = json.loads(session_data_str)
        session_info = session_data[str(session_num)]
        event = session_info["opt"]["scrType"]
        if not event:
            event = None
    except Exception:
        event = None
        # // mos perto add a fucking feature to create these stats bitch

    solves = data.get(session)
    if solves:
        for solve in solves:
            time = solve[0][1] + solve[0][0]
            times.append(time)
            prev_stats.append(solve)
    else:
        times = []

def properties(data):
    if "properties" not in data:
        data["properties"] = {}
    if "sessionData" not in data["properties"]:
        data["properties"]["sessionData"] = json.dumps({})

    try:
        session_data = json.loads(data["properties"]["sessionData"])
    except Exception:
        session_data = {}
    
    if str(session_num) not in session_data:
        session_data[str(session_num)] = {"opt": {"scrType": ""}}
    elif "opt" not in session_data[str(session_num)]:
        session_data[str(session_num)] = {"opt": {"scrType": ""}}
    elif "scrType" not in session_data[str(session_num)]["opt"]:
        session_data[str(session_num)]["opt"]["scrType"] = ""

    return session_data

def gen_scramble():
    global event
    scramble = []
    last_move = []
    dirs = ["", "2", "'"]
    if event == None:
        moves = ["R", "L", "U", "D", "F", "B"]
        scramble_len = random.randint(25, 28)
        for _ in range(scramble_len):
            if len(last_move) > 2:
                last_move.pop(0)
            move = random.choice(moves)
            while move in last_move:
                move = random.choice(moves)
            direction = random.choice(dirs)
            scramble.append(move + direction)
            last_move.append(move.upper())
            
    elif event == "222so":
        moves = ["R", "L", "U", "D", "F"]
        scramble_len = 12
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

    if key == keyboard.Key.right:
        change_sess(1)
    elif key == keyboard.Key.left:
        change_sess(-1)

    if key == keyboard.Key.up:
        change_event(1)
    elif key == keyboard.Key.down:
        change_event(-1)

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


def change_sess(n):
    global session, session_num, EVENTS, event_index, session_num, solve_file
    i = session_num + n
    if i < 1:
        return
    session_num = i
    session = f"session{session_num}"
    load_data(solve_file)
    print_data()

def change_event(n):
    global EVENTS, event_index, event
    event_index += n
    event = EVENTS[event_index]

    try:
        with open(solve_file) as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = {}

    session_data = properties(data)
    session_data[str(session_num)]["opt"]["scrType"] = "" if event is None else event
    data["properties"]["sessionData"] = json.dumps(session_data)

    with open(solve_file, "w") as f:
        json.dump(data, f, indent=4)

    print_data()

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

    print(f"----------------- {colored(session, 'red')} === {colored(event, 'blue')} -------------------")
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