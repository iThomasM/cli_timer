import json
import time
import keyboard
import os
import random
import datetime

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    try:
        ao5, ao12 = load_data()
        print(f"Ao5: {ao5} seconds")
        print(f"Ao12: {ao12} seconds")
    except json.decoder.JSONDecodeError:
        pass
    scramble = generate_scramble()
    print(" ".join(scramble))
    keyboard.wait('space')
    while keyboard.is_pressed('space'):
        time.sleep(0.01)
    prefinal_time = timer_startandstop()
    final_time = solve_check(prefinal_time)

    solve_data = {"scramble": scramble,
                  "date": str(datetime.datetime.now()),
                  "time": final_time}
    
    save_data(solve_data)

def load_data():
    try:
        with open("solves.json", "r") as f:
            all_solves = json.load(f)
    except FileNotFoundError:
        all_solves = []

    print(f"Loaded {len(all_solves)} solves")

    times = [solve["time"] for solve in all_solves if solve["time"] != -1]

    ao5, ao12 = "N/A", "N/A"

    if len(times) >= 5:
        last5 = times[-5:]
        ao5 = (round((sum(last5) - max(last5) - min(last5)) / 3, 2))
    if len(times) >= 12:
        last12 = times[-12:]
        ao12 = (round((sum(last12) - max(last12) - min(last12)) / 10, 2))
    
    return ao5, ao12

def save_data(data):
    try:
        with open("solves.json", "r") as f:
            all_solves = json.load(f)
    except FileNotFoundError:
        all_solves = []
    except json.decoder.JSONDecodeError:
        all_solves = []
    
    all_solves.append(data)
    with open("solves.json", "w") as f:
        json.dump(all_solves, f, indent=4)
    
def solve_check(time):
    os.system('cls' if os.name == 'nt' else 'clear')

    print(f"{time}")
    print(f"+2 -> press 2")
    print(f"DNF -> press 3")
    print(f"OK -> press Enter")

    while True:
        key = keyboard.read_key()
        if key == '2':
            time += 2
            print("+2 added")
            return time
        elif key == '3':
            time = -1
            print("Marked as DNF")
            return time
        elif key == 'enter':
            print("+2s don't count at home")
            return time

def timer_startandstop():
    start_time = time.time()
    end_time = timing(start_time)
    print(end_time)
    return end_time

def generate_scramble():
    moves = ["R", "L", "F", "B", "D", "U"]
    modes = ["'", "2", ""]
    scramble_len = 25
    scramble = []
    last_move = None

    for _ in range(scramble_len):
        move = random.choice(moves)
        while move == last_move:
            move = random.choice(moves)

        mode = random.choice(modes)
        scramble.append(move + mode)
        last_move = move
    
    return scramble

def timing(start_time):
    keyboard_presses = 1
    while True:
        current_time = time.time()
        elapsed = round(current_time - start_time, 3)
        print(elapsed, end="\r") 
        time.sleep(0.05)
        if keyboard.is_pressed('space'):
            if keyboard_presses == 1:
                keyboard_presses += 1
            else:
                break

    return (round(current_time - start_time, 3))

if __name__ == "__main__":
    while True:
        main()