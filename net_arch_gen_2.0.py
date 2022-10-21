import random
import math
import sys
import traceback

padding_len = 13
FLOOR_ENTRIES = [
    ["File DV6", "Passw. DV6", "Passw. DV8", "Skunk", "Wisp", "Killer"],  # lobby
    [
        "Hellh.", "Sabert.", "Raven x2", "Hellh.", "Wisp", "Raven", "Passw. DV6", "File DV6",
        "CNode.DV6", "Passw. DV6", "Skunk", "Asp", "Scorpion", "Killer,Skunk", "Wisp x3", "Liche"
    ],  # basic
    [
        "Hellh. x2", "Hellh. Killer", "Skunk x2", "Sabert.", "Scorpion", "Hellh.",
        "Passw. DV8", "File DV8", "CNode.DV8", "Passw.DV8", "Asp", "Killer", "Liche", "Asp",
        "Raven x3", "Liche, Raven"
    ],  # standard
    [
        "Kraken", "Hellh.Scorp.", "Hellh. Killer", "Raven x2", "Sabert.", "Hellh.",
        "Passw.DV10", "File DV10", "CNode.DV10", "Passw.DV10", "Killer", "Liche", "Dragon",
        "Asp, Raven", "Dragon, Wisp", "Giant"
    ],  # uncommon
    [
        "Hellh. x3", "Asp x2", "Hellh., Liche", "Wisp x3", "Hellh.Sabert.", "Kraken",
        "Passw.DV12", "File DV12", "CNode. DV12", "Passw.DV12", "Giant", "Dragon", "Scorp.Killer",
        "Kraken", "Hellh.Rav.Wisp", "Dragon x2"
    ]  # advanced
]

print(
    [
        max(
            [
                (floor, len(floor), indx) for indx, floor in enumerate(entry)
            ],
            key=lambda t: len(t[0])
        )
        for listindx, entry in enumerate(FLOOR_ENTRIES)
    ]
)


def get_floor_options(difficulty: int):
    return FLOOR_ENTRIES[difficulty]


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def roll_dice(sided: int, multiple: int = 1):
    erg = 0
    for i in range(0, multiple):
        erg += random.randint(1, sided)
    return erg


def roll_branches(floor_amount):
    max_branches = -1
    if floor_amount < 7:
        return 1
    else:
        max_branches = 1 + int((floor_amount - 5) / 2)
    erg = 1
    perc = 4 if floor_amount < 7 else 6 if floor_amount < 10 else 7
    while roll_dice(10) <= perc and floor_amount > 3 + erg * 2 and erg < max_branches:
        erg += 1
        perc -= 1 if floor_amount < 9 else 2
    return erg


def generate_architecture(branch_count, branch_list, floor_count):
    def generate_main_branch(floors: int, branch_count: int, branch_list: list):
        min_main_floors = 3 + math.ceil((floors - 3) / branch_count)
        modifier = 0
        if 1 < branch_count < 5 and floors >= 10:
            modifier = 1 if floors < 14 else 2
        max_main_floors = floors - (branch_count - 1) * 2
        if max_main_floors - modifier >= min_main_floors:
            max_main_floors -= modifier
        size = random.randint(min_main_floors, max_main_floors)
        branch_list.append(Branch(size))
        return size

    def assign_parent_branch(branch, branch_list, subtree_perc):
        main_branch_len = len(branch_list[0])
        branch.pos = random.randint(2, main_branch_len - branch.size - 1)
        branch.parent_branch = 0
        new_perc = subtree_perc + 1

        if roll_dice(10) > subtree_perc:  # branch isnt a subtree
            return new_perc

        possible_parents = []
        # checks whether a parent is high up enough to have the branch attach without overtaking the main branch
        for poss_index in range(1, len(branch_list)):
            parent = branch_list[poss_index]
            maximum_pos = min(main_branch_len - branch.size - 1, parent.pos + branch.size - 1)
            if len(parent) == 1 or parent.pos + branch.size >= main_branch_len or maximum_pos < parent.pos + 1:
                continue
            else:
                possible_parents.append((poss_index, maximum_pos, parent))
        if len(possible_parents) > 0:
            parent_index, maximum_pos, parent = possible_parents[random.randint(0, len(possible_parents) - 1)]
            # if this part is reached, then it is a successful subtree and will break the loop
            branch.pos = random.randint(parent.pos + 1, maximum_pos)
            branch.parent_branch = parent_index
            new_perc = subtree_perc - 1
        return new_perc

    def generate_single_secondary_branch(branch_count: int, branch_list: list, subtree_perc, floors_left_count):
        max_branch_space = len(branch_list[0]) - 3
        remaining_branches = branch_count - len(branch_list) - 1
        max_floors = min(
            max_branch_space,
            floors_left_count - remaining_branches * 2  # max size cut off due to other branches
        )
        min_floors = max(2, floors_left_count - remaining_branches * max_branch_space)
        if min_floors > max_floors:
            Exception(
                f"Secondary branch is required to take {min_floors} but only has space for {max_floors}")
        if floors_left_count < 2:
            Exception(f"Not enough floors to fill a branch")

        branch = Branch(random.randint(min_floors, max_floors))
        subtree_perc = assign_parent_branch(branch, branch_list, subtree_perc)
        # this code is only executed if no suitable branch was found
        branch_list.append(branch)
        return floors_left_count - branch.size, subtree_perc

    def generate_secondary_branches(floor_size: int, branch_count: int, branch_list: list):
        for tries in range(0,200):
            try:
                subtree_perc = 0  # we start at 0, the first is always a subtree of main
                for _ in range(1, branch_count):
                    if len(branch_list) == 2:
                        subtree_perc = 4
                    floor_size, subtree_perc = generate_single_secondary_branch(branch_count, branch_list, subtree_perc, floor_size)
                return

            except Exception as e:
                eprint("generate_sec_failed: ", e)
                traceback.print_exc()
                for i in range(1, len(branch_list)):
                    eprint("ERROR", branch_list[i].floors, branch_list[i].size)
                    del branch_list[i]
        raise Exception("generate_secondary_branches ran 200 times without concluding, something is wrong here")

    main_branch_size = generate_main_branch(floor_count, branch_count, branch_list)
    if branch_count > 1 and main_branch_size <= 2 + (floor_count - main_branch_size) / (branch_count - 1):
        raise Exception(f"Irregular numbers, this should not happen"
                        f"{floor_count}, {branch_count}, {main_branch_size}")
    generate_secondary_branches(floor_count - main_branch_size, branch_count, branch_list)
    check = sum([branch.size for branch in branch_list])
    if not check == floor_count:
        raise Exception(f"Irregular size in branches, this should not happen"
                        f"{floor_count}, {branch_count}, {check}, {main_branch_size}")
    return main_branch_size


def print_inbetween(index, active_columns: list[list[bool]]):
    global padding_len
    ret_str = ""
    padding = padding_len + 1
    padding_front = int(padding / 2)
    padding_back = padding - padding_front
    empty_space = " " * (padding_len + 2)
    full_space = " " * padding_front + "|" + " " * padding_back
    for i in range(0, len(active_columns[index])):
        active = active_columns[index][i]
        ret_str += (full_space if active else empty_space) + "  "
    return ret_str


def print_floor(testFloor):
    global padding_len
    padding = padding_len - len(testFloor)
    padding_front = int(padding / 2)
    padding_back = padding - padding_front
    ret_str = "|" + " " * padding_front + testFloor + " " * padding_back + "|"
    return ret_str


def print_branch(branch, index, info_matrix):
    global padding_len
    padding_back_full = int((padding_len - 1) / 2)
    padding_front_full = padding_len - padding_back_full
    empty_space = " " * (padding_len + 4)
    full_space = " " * padding_front_full + "|" + " " * (padding_back_full + 3)
    enter_space = " " * padding_front_full + "\\" + "-" * (padding_back_full + 3)
    ret_str = ""
    ret_str_exit = ""
    if index > 0:
        for i in range(0, branch.pos):
            if i < branch.pos - 1:
                ret_str += full_space if info_matrix[index - 1][i] else empty_space
            elif i == branch.pos - 1 and not branch.parent_branch == -1:
                ret_str += enter_space
        for i in range(branch.pos + branch.size, len(info_matrix[index - 1])):
            ret_str_exit += full_space if info_matrix[index - 1][i] else empty_space

    return ret_str + str(branch) + ret_str_exit


def fill_floors(branch, used_set, fill_list: list, main_branch=False):
    index = 0
    if main_branch:
        used_base = {-1}
        while index < 2:
            nr = roll_dice(6)
            if not used_base.__contains__(nr):
                used_base.add(nr)
                branch.add_floor(get_floor_options(0)[nr - 1])
                index += 1
    tries = 0
    while index < branch.size:
        nr = roll_dice(6, 3)
        if not used_set.__contains__(nr):
            if len(fill_list) <= nr - 3 <= -1:
                raise Exception(f"rolled a floortype number that wasn't possible {nr - 3}/{len(fill_list)}")
            used_set.add(nr)
            branch.add_floor(fill_list[nr - 3])
            index += 1
        else:
            tries += 1
        if tries > 20 and index < branch.size:
            found = False
            for i in range(3,18):
                if not used_set.__contains__(i):
                    if len(fill_list) <= i - 3 <= -1:
                        raise Exception(f"rolled a floortype number that wasn't possible {i - 3}/{len(fill_list)}")
                    used_set.add(i)
                    branch.add_floor(fill_list[i - 3])
                    index += 1
                    found = True
                    break
            if not found:
                raise Exception(f"seems like I ran out of content to put into rooms, a plan of illegal size was built")


def fill_branches(branches: list, used_set: dict[int], fill_list: list):
    fill_floors(branches[0], used_set, fill_list, True)
    for index in range(1, len(branches)):
        fill_floors(branches[index], used_set, fill_list, False)


class Branch:
    def __init__(self, size: int, pos: int = -1, parent_branch: int = -1):
        self.floors = []
        self.size = size
        self.pos = pos
        self.parent_branch = parent_branch

    def __len__(self):
        return self.size

    def __str__(self):
        #  if not self.size == len(self.floors):
        #      raise Exception(f"ERROR: BRANCH HAS AN INCORRECT AMOUNT OF FLOORS.\n"
        #                      f"parent_branch:{self.parent_branch}\n"
        #                      f"and pos:{self.pos}\n")
        return "--".join(print_floor(floor) for floor in self.floors)

    def add_floor(self, floor):
        if len(self.floors) == self.size:
            raise Exception(f"ERROR: ADDITIONAL FLOOR ADDED TO COMPLETE BRANCH\n"
                            f"parent_branch:{self.parent_branch}\n"
                            f"and pos:{self.pos}\n")
        self.floors.append(floor)

    def value(self):
        return -self.pos * 20 - self.size


def get_int(min_int, max_int):
    num = -1
    non_valid_size = True
    while non_valid_size:
        try:
            num = int(input())
            if min_int <= num <= max_int:
                non_valid_size = False
            else:
                raise Exception("")
        except Exception:
            print(f"Please enter a number between {min_int} and {max_int}.\n")
    return num


def get_size(test_size=-1):
    def get_size_logic(arch_size=-1):
        min_floor = 3 + 3 * (arch_size - 1)
        max_floor = 16 if arch_size == 4 else 5 + 3 * (arch_size - 1)
        return random.randint(min_floor, max_floor)

    if not test_size == -1:
        return get_size_logic(test_size)
    print(
        "Please select difficulty\n"
        "1-Small         | 3 - 5 floors\n"
        "2-Corp          | 6 - 8 floors\n"
        "3-Gigantic      | 9 - 11 floors\n"
        "4-Megastructure | 12 - 16 floors\n"
        "Size:"
    )
    return get_size_logic(get_int(1, 4))


def get_difficulty(test_difficulty=-1):
    if not test_difficulty == -1:
        return test_difficulty
    print(
        "Please select difficulty\n"
        "Nr | Difficulty  | DV   | recomm. interface | potentially deadly interface\n"
        "--------------------------------------------------------------------------\n"
        "1  | Basic       | DV6  |         2         | interface <= N/A\n"
        "2  | Standard    | DV8  |         4         | interface <= 2\n"
        "3  | Uncommon    | DV10 |         6         | interface <= 4\n"
        "4  | Advanced    | DV12 |         8         | interface <= 6\n"
        "Difficulty:"
    )
    return get_int(1, 4)


def recursive_sort(new_branch_list, old_branch_list, current_index):
    new_branch_list.append(old_branch_list[current_index])
    sorted_children = sorted(filter(
        lambda b: b[1].parent_branch == current_index,
        [(index, branch) for index, branch in enumerate(old_branch_list)],
    ), key=lambda b: b[1].value()
    )
    for child_index, _ in sorted_children:
        recursive_sort(new_branch_list, old_branch_list, child_index)


def populate_floors(branch_count, branch_list, difficulty, floor_count):
    used = {-1}  # tracks which floor entries have been used already
    floor_fill_list = get_floor_options(difficulty)
    fill_floors(branch_list[0], used, floor_fill_list, True)
    print("\nfloors:", floor_count, "branches:", branch_count)
    for i in range(1, len(branch_list)):
        branch = branch_list[i]
        fill_floors(branch, used, floor_fill_list, False)
        if not len(branch.floors) == branch.size:
            eprint("ERROR", branch.floors, branch.size)


def create_output_matrix(branch_count, branch_list, main_branch_size):
    enabled_matrix = [[False for _ in range(0, main_branch_size)] for _ in range(1, branch_count)]
    for index in range(1, len(branch_list) + 1):
        branch = branch_list[len(branch_list) - index]
        for i in range(index, len(enabled_matrix) + 1):
            if not index == len(branch_list):
                upper_branch = branch_list[len(branch_list) - i - 1]
                enabled_matrix[len(enabled_matrix) - i][branch.pos - 1] = True
                if upper_branch.pos <= branch.pos - 1 <= upper_branch.pos + upper_branch.size:
                    break
    return enabled_matrix


def main(test_sample: int, test_size=-1, test_difficulty=-1):
    exit_cond = False
    if not test_size == -1 and 4 < test_size < 1:
        raise Exception("Illegal size test data")
    if not test_difficulty == -1 and 4 < test_difficulty < 1:
        raise Exception("Illegal difficulty test data")
    while not exit_cond:
        for _ in range(0, test_sample):
            floor_count = get_size(test_size)
            difficulty = get_difficulty(test_difficulty)

            branch_list = []
            branch_count = roll_branches(floor_count)
            try:
                main_branch_size = generate_architecture(branch_count, branch_list, floor_count)

                populate_floors(branch_count, branch_list, difficulty, floor_count)

                sorted_branch_list = []
                recursive_sort(sorted_branch_list, branch_list, 0)
                del branch_list

                enabled_matrix = create_output_matrix(branch_count, sorted_branch_list, main_branch_size)

                for index in range(0, len(sorted_branch_list)):
                    branch = sorted_branch_list[index]
                    print(print_branch(branch, index, enabled_matrix))
                    if not index == len(sorted_branch_list) - 1:
                        print(print_inbetween(index, enabled_matrix))

            except Exception as e:
                eprint("There was an error generating this NET-Arch. Please retry")
                traceback.print_exc()
                eprint(e)

        if not test_sample == 1:
            break
        elif input("\nInput \"q\" to exit. Input anything else for another NET-Arch\n") == "q":
            exit_cond = True


main(1)
