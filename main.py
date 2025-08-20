import json
import time
import keyboard
import os
import random
import datetime

class Timer():
    def __init__(self, solve_file="solves.json"):
        self.solve_file = solve_file
        self.index = 0
        self.events = ["3x3", "2x2", "4x4", "5x5", "6x6", "7x7", "skewb", "pyra"]
        self.event = self.events[self.index]

        keyboard.on_press_key("right", lambda _: self._change_index(1))
        keyboard.on_press_key("left", lambda _: self._change_index(-1))

    def save_data(self, data):
        try:
            with open(self.solve_file, "r") as f:
                all_data = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            all_data = {}

        if self.event not in all_data:
            all_data[self.event] = []

        all_data[self.event].append(data)

        with open(self.solve_file, "w") as f:
            json.dump(all_data, f, indent=4)
        
    def load_stats(self):
        try:
            with open(self.solve_file, "r") as f:
                all_data = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            all_data = {}

        solves = all_data.get(self.event, [])

        print(f"Loaded {len(solves)} {self.event} solves", end="    ")

        times = [solve["time"] for solve in solves if solve["time"] != -1]

        ao5, ao12 = "N/A", "N/A"

        if len(times) >= 5:
            last5 = times[-5:]
            ao5 = (round((sum(last5) - max(last5) - min(last5)) / 3, 2))
        if len(times) >= 12:
            last12 = times[-12:]
            ao12 = (round((sum(last12) - max(last12) - min(last12)) / 10, 2))

        return ao5, ao12
    
    def generate_scramble(self, event):
        moves = {"3x3": ["R", "L", "F", "B", "D", "U"],
                 "2x2": ["R", "L", "F", "B", "D", "U"],
                 "pyra": ["R", "L", "B", "F", "U", "D", "r", "l", "b", "f", "u", "d"],
                 "4x4": ["R", "L", "B", "F", "U", "D", "r", "l", "b", "f", "u", "d"],
                 "5x5": ["R", "L", "B", "F", "U", "D", "r", "l", "b", "f", "u", "d"],
                 "6x6": ["R", "L", "B", "F", "U", "D", "r", "l", "b", "f", "u", "d", "r2w, l2w, b2w, f2w, u2w, d2w"],
                 "7x7": ["R", "L", "B", "F", "U", "D", "r", "l", "b", "f", "u", "d", "r2w, l2w, b2w, f2w, u2w, d2w"]}
        modes = ["'", "2", ""]
        scramble_len = {"3x3": 25, "2x2": 12, "pyra": 12, "4x4": 35, "5x5": 42, "6x6": 50, "7x7": 60}
        scramble = []
        last_move = None

        for _ in range(scramble_len[event]):
            move = random.choice(moves[event])
            while move == last_move:
                move = random.choice(moves[event])

            mode = random.choice(modes)
            scramble.append(move + mode)
            last_move = move

        return scramble
    
    def timing(self, start_time):
        keyboard_presses = 1
        while True:
            current_time = time.time()
            elapsed = round(current_time - start_time, 3)
            print(elapsed, end="\r") 
            time.sleep(0.01)
            if keyboard.is_pressed('space'):
                if keyboard_presses == 1:
                    keyboard_presses += 1
                else:
                    break

        return (round(current_time - start_time, 3))
    
    def timer_startandstop(self):
        start_time = time.time()
        end_time = self.timing(start_time)
        print(end_time)
        return end_time
    

    def solve_check(self, solve_time):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{solve_time}")
        print(f"+2 -> press 2")
        print(f"DNF -> press 3")
        print(f"OK -> press Enter")

        while True:
            key = keyboard.read_key()
            if key == '2':
                solve_time += 2
                print("+2 added")
                return solve_time
            elif key == '3':
                print("Marked as DNF")
                return -1
            elif key == 'enter':
                return solve_time
    
    def _change_index(self, amnt):
            self.index += amnt
            self.event = self.events[self.index]
            os.system('cls' if os.name == 'nt' else 'clear')

            ao5, ao12 = self.load_stats()
            print(f"Ao5: {ao5} seconds", end="    ")
            print(f"Ao12: {ao12} seconds", end="    ")

            scramble = self.generate_scramble(self.event)
            print("\n")
            print(" ".join(scramble))
            
    def main(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        ao5, ao12 = self.load_stats()
        print(f"Ao5: {ao5} seconds", end="    ")
        print(f"Ao12: {ao12} seconds", end="    ")

        scramble = self.generate_scramble(self.event)
        print("\n")
        print(" ".join(scramble))

        keyboard.wait('space')
        while keyboard.is_pressed('space'):
            time.sleep(0.01)


        prefinal_time = self.timer_startandstop()
        final_time = self.solve_check(prefinal_time)

        solve_data = {"scramble": scramble,
                      "date": str(datetime.datetime.now()),
                      "time": final_time}

        self.save_data(solve_data)

if __name__ == "__main__":
    timer = Timer()
    while True:
        timer.main()