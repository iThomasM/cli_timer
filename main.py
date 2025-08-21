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
        self.solve_list = []
        self.in_menu = False

    def convert(self, time):
        try:
            time = float(time)
        except:
            return time
        mins = 0
        seconds = time
        while time > 59:
            if time >= 60: 
                if seconds - 60 < 0: 
                    break
                else:
                    seconds -= 60 
                mins += 1 
        if mins == 0:
            return time
        
        return f"{mins}:{round(seconds, 3)}"
    
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
        self.solve_list = times

        ao5, ao12, pb = "N/A", "N/A", "N/A"
        try:
            pb = min(times)
        except ValueError:
            pass

        if len(times) >= 5:
            last5 = times[-5:]
            ao5 = (round((sum(last5) - max(last5) - min(last5)) / 3, 3))
        if len(times) >= 12:
            last12 = times[-12:]
            ao12 = (round((sum(last12) - max(last12) - min(last12)) / 10, 3))

        return ao5, ao12, pb
    
    def generate_scramble(self, event):
        moves = {"3x3": ["R", "L", "F", "B", "D", "U"],
                 "2x2": ["R", "L", "F", "B", "D", "U"],
                 "skewb": ["R", "L", "F", "B", "D", "U"],
                 "pyra": ["R", "L", "B", "F", "U", "D", "r", "l", "b", "f", "u", "d"],
                 "4x4": ["R", "L", "B", "F", "U", "D", "r", "l", "b", "f", "u", "d"],
                 "5x5": ["R", "L", "B", "F", "U", "D", "r", "l", "b", "f", "u", "d"],
                 "6x6": ["R", "L", "B", "F", "U", "D", "r", "l", "b", "f", "u", "d", "r2w", "l2w", "b2w", "f2w", "u2w", "d2w"],
                 "7x7": ["R", "L", "B", "F", "U", "D", "r", "l", "b", "f", "u", "d", "r2w", "l2w", "b2w", "f2w", "u2w", "d2w"]}
        modes = ["'", "2", ""]
        scramble_len = {"3x3": 25, "2x2": 12, "pyra": 12, "4x4": 35, "5x5": 42, "6x6": 50, "7x7": 60, "skewb": 12}
        scramble = []
        last_move = []

        for _ in range(scramble_len[event]):
            if len(last_move) > 2:
                last_move.pop(0)
            move = random.choice(moves[event])
            while move in last_move:
                move = random.choice(moves[event])

            mode = random.choice(modes)
            scramble.append(move + mode)
            last_move.append(move)

        return scramble
    
    def timing(self, start_time):
        keyboard_presses = 1
        move_cursor = True
        while True:
            current_time = time.time()
            elapsed = round(current_time - start_time, 3)
            if move_cursor:
                print(f"\033[F{self.convert(elapsed)}", end="\r")
                move_cursor = False
            print(f"{self.convert(elapsed)}", end="\r")
            
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
        print(f"{self.convert(solve_time)}")
        print(f"+2 -> press 2")
        print(f"DNF -> press 3")
        print(f"Delete -> Del")
        print(f"OK -> press Enter")

        while True:
            key = keyboard.read_key()
            if key == '2':
                solve_time += 2
                return solve_time
            elif key == '3':
                return -1
            elif key == 'enter':
                return solve_time
            elif key == 'delete':
                return False
    
    def _change_index(self, amnt):
        try:
            self.index += amnt
            self.event = self.events[self.index]
        except IndexError:
            self.index = 0
        os.system('cls' if os.name == 'nt' else 'clear')
        self._print()

    def _print_solves(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        if not self.solve_list:
            print("No data.")
        else:
            for i, s in enumerate(self.solve_list):
                print(f"{i+1}) {self.convert(s)}")
        
        print("\ne -> Return")
        
        while True:
            if keyboard.is_pressed('e'):
                break
        self._print()

    def _print(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        ao5, ao12, pb = self.load_stats()
        print(f"PB: {self.convert(pb)}s", end="    ")
        print(f"Ao5: {self.convert(ao5)} seconds", end="    ")
        print(f"Ao12: {self.convert(ao12)} seconds", end="    ")

        scramble = self.generate_scramble(self.event)

        print("\n")
        print(" ".join(scramble))
        print("\nq -> View Solve List", end="\r")
            
    def main(self):
        self.keyboard_events()

        scramble = self._print()

        keyboard.wait('space')
        while keyboard.is_pressed('space'):
            time.sleep(0.01)

        prefinal_time = self.timer_startandstop()
        final_time = self.solve_check(prefinal_time)
        if not final_time:
            return

        solve_data = {"scramble": scramble,
                      "date": str(datetime.datetime.now()),
                      "time": final_time}

        self.save_data(solve_data)


    def keyboard_events(self):
        keyboard.on_press_key("right", lambda _: self._change_index(1))
        keyboard.on_press_key("left", lambda _: self._change_index(-1))
        keyboard.on_press_key("q", lambda _: self._print_solves())

if __name__ == "__main__":
    timer = Timer()
    while True:
        timer.main()