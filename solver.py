from parse import read_input_file, write_output_file
import os

def solve(tasks):
    """
    Args:
        tasks: list[Task], list of igloos to polish
    Returns:
        output: list of igloos in order of polishing
    """
    pass

def naiveSolver(tasks):
    """Sort the list of tasks by deadline, then pick the best task that is near
    the time that we are at."""
    final_output = []
    tasks = sorted(tasks, key=lambda task: (task.get_deadline() + task.get_duration() - task.get_max_benefit()))
    current_time = 0
    naive_score = 0


    while current_time < 1440:
        if current_time + tasks[0].get_duration() < tasks[0].get_deadline():
            final_output.append(tasks[0].get_task_id())
            current_time += tasks[0].get_duration()
            naive_score += tasks[0].get_max_benefit()
        tasks.pop(0)
        if len(tasks) == 0:
            break

    return final_output, naive_score


def solver2(tasks, num_possibilities):
    "Look for the best task within a range of the current index and and do that task"
    final_output = []
    current_time = 0
    score = 0

    while current_time < 1440:
        tasks = sorted(tasks, key=lambda task: 1 / find_efficiency(task, current_time))
        current_index = 0
        min_deadline = 1440
        if len(tasks) <= current_index:
            break
        best_task = tasks[current_index]
        for i in range(num_possibilities):
            if min_deadline > tasks[current_index].get_deadline() and ((tasks[current_index].get_duration() + current_time) <= 1440):
                min_deadline = tasks[current_index].get_deadline()
                best_task = tasks[current_index]
            current_index += 1
            if len(tasks) <= current_index:
                break
        if min_deadline == 1440:
            break;
        current_time += best_task.get_duration()
        if current_time < 1440:
            tasks.remove(best_task)
            final_output.append(best_task.get_task_id())
            score += best_task.get_late_benefit(best_task.get_deadline() - best_task.get_duration() - current_time)
    return final_output, score

def dpSolver(tasks):
    "DP algorithm that considers different starting points"
    tasks = sorted(tasks, key=lambda task: task.get_deadline())
    storage = {}
    for i in range(len(tasks) + 1):
        for t in range(1440):
            storage[(i, t)] = [0, []] #first element represents the score, second is the tasks
    for i in range(1, len(tasks)): #why not +1?
        for time in range(0, 1440):
            newT = min(time, tasks[i].get_deadline()) - tasks[i].get_duration()
            if newT < 0:
                storage[(i, time)] = storage[(i-1, time)].copy()
            else:
                if storage[(i-1, time)][0] < tasks[i].get_max_benefit() + storage[(i-1, newT)][0]:
                    storage[(i, time)][0] = tasks[i].get_max_benefit() + storage[(i-1, newT)][0]
                    storage[(i, time)][1] = storage[(i-1, newT)][1].copy()
                    storage[(i, time)][1].append(tasks[i].get_task_id())
                else:
                    storage[(i, time)][0] = storage[(i-1, time)][0]
                    storage[(i, time)][1] = storage[(i-1, time)][1].copy()

    return storage[(len(tasks)-1, 1439)]

def bestSolver(tasks):
    "Take each solver, calculate each value for that solver, and return the best one"
    final_output, best_score = naiveSolver(tasks)
    addtasks_answer = addtasks(tasks, final_output, best_score)
    if addtasks_answer[0] > best_score:
        best_score = addtasks_answer[0]
        final_output = addtasks_answer[1]

    solver2_best_score = 0
    solver2_output = []
    for i in range(3, 15):
        potential_output, potential_score = solver2(tasks, i)
        if potential_score > solver2_best_score:
            solver2_best_score = potential_score
            solver2_output = potential_output
    addtasks_answer = addtasks(tasks, solver2_output, solver2_best_score)
    if addtasks_answer[0] > best_score:
        best_score = addtasks_answer[0]
        final_output = addtasks_answer[1]


    DP_answer = dpSolver(tasks)
    addtasks_answer = addtasks(tasks, DP_answer[1], DP_answer[0])
    if addtasks_answer[0] > best_score:
        best_score = addtasks_answer[0]
        final_output = addtasks_answer[1]


    return final_output

def addtasks(tasks, tasks_completed, score):
    "If there is time remaining, run the best late tasks possible"
    current_time = 0
    final_score = score
    final_output = tasks_completed.copy()
    tasks = sorted(tasks, key=lambda task: task.get_task_id())
    for task_id in tasks_completed:
        current_time += tasks[task_id - 1].get_duration()
    tasks = [task for task in tasks if task.get_task_id() not in tasks_completed] #remove all tasks completed
    while current_time < 1440:
        tasks = sorted(tasks, key=lambda task: 1 / task.get_late_benefit(current_time - task.get_deadline()))
        if len(tasks) == 0:
            break
        if tasks[0].get_duration() + current_time < 1440:
            current_time += tasks[0].get_duration()
            final_score += tasks[0].get_late_benefit(current_time - tasks[0].get_deadline())
            final_output.append(tasks[0].get_task_id())
        tasks.pop(0)
    return [final_score, final_output]




def find_efficiency(task, current_time):
    return task.get_late_benefit(task.get_duration() + current_time - task.get_deadline()) / task.get_duration()


def deadline_check(task, current_time):
    return current_time + task.get_duration() < task.get_deadline();


####################################################
#######    TO RUN THE CODE ON ALL INPUTS    ########
####################################################

if __name__ == '__main__':
    for size in os.listdir('inputs/'):
        if size not in ['small', 'medium', 'large']:
            continue
        for input_file in os.listdir('inputs/{}/'.format(size)):
            if size not in input_file:
                continue
            input_path = 'inputs/{}/{}'.format(size, input_file)
            output_path = 'outputs/{}/{}.out'.format(size, input_file[:-3])
            print(input_path, output_path)
            tasks = read_input_file(input_path)
            output = bestSolver(tasks)
            write_output_file(output_path, output)

########################################################


########################################################
######  TO RUN THE CODE ON A SPECIFIC FILEPATH   #######
########################################################

#x = "REPLACE WITH FILEPATH"
#bestSolver(read_input_file(x))

########################################################








# naiveSolver(read_input_file("samples/200.in"))
# #solver2(read_input_file("samples/200.in"))
#bestSolver(read_input_file("samples/100.in"))
#dpSolver(read_input_file("samples/200.in"))


#Here's an example of how to run your solver.
# if __name__ == '__main__':

    # for input_path in os.listdir('inputs/large/'):
    #     output_path = 'outputs/large/' + input_path[:-3] + '.out'
    #     tasks = read_input_file(input_path)
    #     output = naiveSolver(tasks)
    #     write_output_file(output_path, output)
    #
    # for input_path in os.listdir('inputs/medium/'):
    #     output_path = 'outputs/medium/' + input_path[:-3] + '.out'
    #     tasks = read_input_file(input_path)
    #     output = naiveSolver(tasks)
    #     write_output_file(output_path, output)
    #
    # for input_path in os.listdir('inputs/small/'):
    #     output_path = 'outputs/small/' + input_path[:-3] + '.out'
    #     tasks = read_input_file(input_path)
    #     output = naiveSolver(tasks)
    #     write_output_file(output_path, output)


# one = Task(1, 557, 26, 54.191)
# two = Task(2, 862, 24, 36.515)
# three = Task(3, 822, 24, 2.488)
# four = Task(4, 786, 60, 22.003)
#
# tasks = [one,two,three,four]
# tasks = read_input_file("samples/150.in")
