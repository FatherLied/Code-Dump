import os
import time

from operator import methodcaller, itemgetter

class Square:
    debug = False

    options = {
        "multiplier": 10,
        "step_cost": [
            1, # (-, 0) South
            1, # (-, +) South-West
            1, # (0, +) West
            1, # (+, +) North-West
            1, # (+, 0) North
            1, # (+, -) North-East
            1, # (0, -) East
            1  # (-, -) South-East
        ],
        "solution": "Manhattan"
    }

    @classmethod
    def toggle_debug(cls):
        if cls.debug:
            cls.debug = False
        else:
            cls.debug = True

    @classmethod
    def modify_options(cls, options):
        cls.options = options

    def set_options(self):
        self.multiplier = self.options["multiplier"]
        self.step_cost = self.options["step_cost"]
        self.solution = self.options["solution"]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def __init__(self, x, y, sq_type):
        self.set_options()

        self.x = x
        self.y = y

        valid_types = {
            '%': "Wall",
            ' ': "Space",
            '.': "Goal",
            'P': "Start"
        }

        if sq_type not in valid_types:
            self.sq_type = "Wall"
        else:
            self.sq_type = valid_types[sq_type]

        self.code = self.numbering_code()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def heuristic(self, goal):
        if not isinstance(goal, Square):
            raise Exception("Square: Invalid Type")

        if self.solution is "Manhattan":
            return abs(self.x - goal.x) * self.multiplier \
                   + abs(self.y - goal.y) * self.multiplier
        else:
            dx = abs(self.x - goal.x)
            dy = abs(self.y - goal.y)
            return self.step(goal) * max(dx, dy)

    def step(self, dest):
        if not isinstance(dest, Square):
            raise Exception("Square: Invalid Type")

        diff = [self.x - dest.x, self.y - dest.y]

        if diff[0] < 0 and diff[1] == 0:
            """South"""
            return self.step_cost[0]

        elif diff[0] < 0 and diff[1] > 0:
            """South-West"""
            return self.step_cost[1]

        elif diff[0] == 0 and diff[1] > 0:
            """West"""
            return self.step_cost[2]
        
        elif diff[0] > 0 and diff[1] > 0:
            """North-West"""
            return self.step_cost[3]

        elif diff[0] > 0 and diff[1] == 0:
            """North"""
            return self.step_cost[4]

        elif diff[0] > 0 and diff[1] < 0:
            """North-East"""
            return self.step_cost[5]

        elif diff[0] == 0 and diff[1] < 0:
            """East"""
            return self.step_cost[6]

        elif diff[0] < 0 and diff[1] < 0:
            """South-East"""
            return self.step_cost[7]

        else:
            """Center"""
            return 0

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def numbering_code(self):
        code = ""

        index = self.x + 1

        while index > 0:           
            modulo = (index-1) % 26
            code += chr(modulo + 65)
            index = (index - modulo)/26

        code += str(self.y)

        return code

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def __str__(self):
        convert = {
            "Wall" : '%',
            "Space": ' ',
            "Goal" : '.',
            "Start": 'P'
        }

        return "{}".format(convert[self.sq_type])

    def __repr__(self):
        return self.code
        # return "({:>2},{:<2})".format(self.x, self.y)

class Maze:
    maze = []
    # Linked List for path?

    options = {
        "multiplier": 10,
        "step_cost": [
            1, # (-, 0) South
            1, # (-, +) South-West
            1, # (0, +) West
            1, # (+, +) North-West
            1, # (+, 0) North
            1, # (+, -) North-East
            1, # (0, -) East
            1  # (-, -) South-East
        ],
        "moves": [
            True, # North
            True, # North-East
            True, # East
            True, # South-East
            True, # South
            True, # South-West
            True, # West
            True  # North-West
        ]
    }

    debug = False

    @classmethod
    def toggle_debug(cls):
        if cls.debug:
            cls.debug = False
        else:
            cls.debug = True

    @classmethod
    def modify_options(cls, options):
        cls.options = options

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def __init__(self, file_path):
        self.set_options()

        self.start = None
        self.goal = []

        self.open_list = []
        self.closed_list = []

        self.current_goal = None

        self.parent_list = []

        # Diagnostics
        self.file_name = file_path
        self.nodes = 0
        self.path = []
        self.cost = 0

        self.to_maze(file_path)

        """ Maze Limits """
        self.x_limit = len(self.maze)
        self.y_limit = len(self.maze[0])

        self.goal = sorted(self.goal, key = methodcaller('heuristic', self.start))

    def __str__(self):
        output = ""

        for row in self.maze:
            for item in row:
                # print(item)
                output += str(item)

            output += "\n"

        return output

    def __repr__(self):
        return "Maze ({} down x {} across)".format(len(self.maze), len(self.maze[0]))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def set_options(self):
        self.multiplier = self.options["multiplier"]
        self.step_cost = self.options["step_cost"]
        self.moves = self.options["moves"]
        self.marker = self.options["marker"]

        Square.modify_options(self.options)


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def insert(self, square, cost, heu):
        for i in range(len(self.open_list)):
            if self.open_list[i][0] is square:
                if self.open_list[i][3] > cost + heu:
                    self.open_list.pop(i)
                else:
                    return

        self.open_list.append((square, cost, heu, cost + heu))

    def explore(self, origin, goal):
        """ Explores all eight sides"""

        x = origin[0].x
        y = origin[0].y

        # Origin = (Square, Cost, Heuristic, Cost+Heuristic)
        # print("{} {}".format(x - 1, y - 1))
        # Parent List -> (Parent, Child)

        # (-, 0) South
        # """North"""
        if x - 1 >= 0 and self.moves[0]:
            sq = self.maze[x - 1][y]

            if sq.sq_type is not "Wall" and sq not in self.closed_list:
                cost = origin[0].step(sq)
                self.insert(sq, origin[1] + cost, sq.heuristic(goal))

                self.parent_list.append((origin[0], sq))
        
        # (-, +) South-West
        # """North-East"""
        if x - 1 >= 0 and y + 1 < self.y_limit and self.moves[1]:
            sq = self.maze[x - 1][y + 1]

            if sq.sq_type is not "Wall" and sq not in self.closed_list:
                cost = origin[0].step(sq)
                self.insert(sq, origin[1] + cost, sq.heuristic(goal))

                self.parent_list.append((origin[0], sq))

        # (0, +) West
        # """East"""
        if y + 1 < self.y_limit and self.moves[2]:
            sq = self.maze[x][y + 1]

            if sq.sq_type is not "Wall" and sq not in self.closed_list:
                cost = origin[0].step(sq)
                self.insert(sq, origin[1] + cost, sq.heuristic(goal))

                self.parent_list.append((origin[0], sq))

        # (+, +) North-West
        # """South-East"""
        if x + 1 < self.x_limit and y + 1 < self.y_limit and self.moves[3]:
            sq = self.maze[x + 1][y + 1]

            if sq.sq_type is not "Wall" and sq not in self.closed_list:
                cost = origin[0].step(sq)
                self.insert(sq, origin[1] + cost, sq.heuristic(goal))

                self.parent_list.append((origin[0], sq))

        # (+, 0) North
        # """South"""
        if x + 1 < self.x_limit and self.moves[4]:
            sq = self.maze[x + 1][y]

            if sq.sq_type is not "Wall" and sq not in self.closed_list:
                cost = origin[0].step(sq)
                self.insert(sq, origin[1] + cost, sq.heuristic(goal))

                self.parent_list.append((origin[0], sq))

        # (+, -) North-East
        # """South-West"""
        if x + 1 < self.x_limit and y - 1 >= 0 and self.moves[5]:
            sq = self.maze[x + 1][y - 1]

            if sq.sq_type is not "Wall" and sq not in self.closed_list:
                cost = origin[0].step(sq)
                self.insert(sq, origin[1] + cost, sq.heuristic(goal))

                self.parent_list.append((origin[0], sq))

        # (0, -) East
        # """West"""
        if y - 1 >= 0 and self.moves[6]:
            sq = self.maze[x][y - 1]

            if sq.sq_type is not "Wall" and sq not in self.closed_list:
                cost = origin[0].step(sq)
                self.insert(sq, origin[1] + cost, sq.heuristic(goal))

                self.parent_list.append((origin[0], sq))

        # (-, -) South-East
        # """North-West"""
        if x - 1 >= 0 and y - 1 >= 0 and self.moves[7]:
            print("Hi")
            sq = self.maze[x - 1][y - 1]

            if sq.sq_type is not "Wall" and sq not in self.closed_list:
                cost = origin[0].step(sq)
                self.insert(sq, origin[1] + cost, sq.heuristic(goal))

                self.parent_list.append((origin[0], sq))

    def process(self):
        """
        Note: 
            Heuristic is not passed down to child, only step

            Open List (Square, )
        """
        # current = self.start

        cycle = 0
        blocked = False
        restart = False

        # Parent List -> (Parent, Child)
        self.parent_list.append((None, self.start))

        starting = self.start
        self.insert(starting, starting.step(starting), starting.heuristic(self.goal[0]))

        # self.insert(self.start, self.start.step(self.start, cost), self.start.heuristic(self.goal[0]))
        current = self.open_list.pop(0)

        while len(self.goal) > 0:
            self.goal = sorted(self.goal, key = methodcaller('heuristic', current[0]))
            current_goal = self.goal.pop(0)

            while current[0] is not current_goal and not blocked:
                self.explore(current, current_goal)

                self.open_list = sorted(self.open_list, key = itemgetter(3))
                self.closed_list.append(current[0])

                # """ Debug Block"""
                if self.debug:
                    cycle += 1

                    os.system('cls' if os.name == 'nt' else 'clear')

                    print("{}".format(self))

                    print("Open List:")
                    for item in self.open_list:
                        print("\t{} : {}".format(item, item[0].sq_type))

                    print("Closed List:")
                    for item in self.closed_list:
                        print("\t{} : {}".format(item.code, item.sq_type))

                    print("Parent List:")
                    for item in self.parent_list:
                        print("\t{}".format(item))

                    print("\nCurrent: {}".format(current))
                    print("Current Goal: {}".format(current_goal.code))
                    print("Goals Left: {}".format(self.goal))

                    print("\nCycle: {}".format(cycle))
                    print("Blocked: {}\n".format(blocked))

                    self.bugloop_1 = 0
                    self.bugloop_2 = 0

                    raw_input("Press Enter to continue...")
                # """ Debug Block"""

                try:
                    current = self.open_list.pop(0)
                except IndexError:
                    blocked = True

            if current[0] not in self.closed_list:
                self.closed_list.append(current[0])

            # Traversed nodes
            self.nodes += len(self.closed_list)

            # Overall Cost
            self.cost = current[1]

            # Parent List = (Parent, Child)
            temp = None
            for item in self.parent_list:
                # """ Debug Block"""
                if self.debug:
                    os.system('cls' if os.name == 'nt' else 'clear')

                    print("{}".format(self))
                    print("Item: {}".format(item))
                    print("Loop - {}".format(self.bugloop_1))

                    raw_input("Press Enter to continue...")
                # """ Debug Block"""

                if item[1] is current[0]:
                    temp = item

            if temp:
                temp_path = [temp[1]]
                while temp[0] is not None:
                    for item in self.parent_list:
                        # """ Debug Block"""
                        if self.debug:
                            os.system('cls' if os.name == 'nt' else 'clear')

                            print("{}".format(self))
                            print("Item: {}".format(item))
                            print("Loop - {}".format(self.bugloop_2))

                            raw_input("Press Enter to continue...")
                        # """ Debug Block"""

                        if item[1] is temp[0]:
                            temp_path.append(temp[0])
                            temp = item
                rev = temp_path[::-1]

                if restart:
                    rev.pop(0)

                self.path.extend(rev)
            else:
                raise Exception("Current is not a child in Parent List")

            restart = True

            # """ Debug Block"""
            if self.debug:
                print("\nIs blocked: {}".format(blocked))
                print("\nExit Current: {}".format(current))
                print("Current Goal: {}".format(current_goal.code))

                print("\n{} == {}: {}".format(current[0].code,
                                              current_goal.code,
                                              current[0].code is current_goal.code))
                print("Traversal Path:\n\t{}".format(self.path))

                raw_input("Press Enter to continue...")
            # """ Debug Block"""

            # Reset here
            self.parent_list = []
            self.open_list= []
            self.closed_list = []

            self.parent_list.append((None, current[0]))

            if blocked:
                break

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def diagnostics(self):
        print("# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #")
        
        border = "========="

        if len(self.file_name) > 71:
            border += "=" * 71
        else:
            border += "=" * len(self.file_name)

        print(border)
        print("Results: {}".format(self.file_name))
        print("{}\n".format(border))
        print("Traversed Nodes: {}".format(self.nodes))
        print("Overall Cost: {} units".format(self.cost))
        print("Path: ")

        path = ""
        for i in range(len(self.path)):
            path += self.path[i].code

            if i + 1 < len(self.path):
                path += " -> "

        print("\t{}".format(path))
        print("# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #")

    def write_file(self):
        output = ""

        for row in self.maze:
            for item in row:
                # print(item)
                if item in self.path and (item.sq_type is not "Start" 
                                          and item.sq_type is not "Goal"):
                    output += self.marker
                else:
                    output += str(item)

            output += "\n"

        bits = self.file_name.split('/')

        name = bits[len(bits) - 1].split('.')
        name[0] += "_solution"
        tail = name[len(name) - 1]

        bits[len(bits) - 1] = ".".join(name)

        i = 1
        while os.path.exists(os.path.join(*bits)):
            name = bits[len(bits) - 1].split('.')
            # name[0] += "_solution"
            name[len(name) - 2] = str(tail) + "({})".format(i)

            bits[len(bits) - 1] = ".".join(name)
            i += 1

        # print("Bits = {}\nName = {}".format(bits, name))

        with open(os.path.join(*bits), 'w') as file:
            file.write(output)


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def to_maze(self, file_path):
        """ Converts file to internal Maze """

        file_path = file_path.split('/')
        
        with open(os.path.join(*file_path)) as file:
            lines = file.read().splitlines()

        i = 0
        for line in lines:
            j = 0
            row = []

            for char in line:
                sqr = Square(i, j, char)
                row.append(sqr)

                if sqr.sq_type is "Start":
                    self.start = sqr

                if sqr.sq_type is "Goal":
                    self.goal.append(sqr)
                j += 1

            self.maze.append(row)
            i += 1


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def test():
    os.system('cls' if os.name == 'nt' else 'clear')

    options = {
        "multiplier": 10,
        "step_cost": [
            1, # (-, 0) South
            1, # (-, +) South-West
            1, # (0, +) West
            1, # (+, +) North-West
            1, # (+, 0) North
            1, # (+, -) North-East
            1, # (0, -) East
            1  # (-, -) South-East
        ],
        "moves": [
            True, # North
            False, # North-East
            True, # East
            False, # South-East
            True, # South
            False, # South-West
            True, # West
            False  # North-West
        ],
        "solution": "Manhattan",
        # "solution": "Straight Line",
        "marker": '+'
    }

    # sample = "mazes/bigMaze.lay.txt"
    # sample = "mazes/mediumMaze.lay.txt"
    # sample = "mazes/openMaze.lay.txt"
    sample = "mazes/trickySearch.lay.txt"
    # sample = "mazes/smallMaze.lay.txt"
    # sample = "mazes/tinyMaze.lay.txt"

    # Maze.toggle_debug()
    Maze.modify_options(options)

    test = Maze(sample)

    print(test)
    print([test])

    print("Start: {}".format(test.start.code))
    print("Goals: {}".format(test.goal))

    print("Heuristic: {}".format(test.start.heuristic(test.goal[0])))

    test.process()

    print("")

    test.diagnostics()
    test.write_file()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

if __name__ == "__main__":
    test()

    # Maze.modify_options(options)