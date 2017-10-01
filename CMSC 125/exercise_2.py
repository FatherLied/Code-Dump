from threading import Thread
from operator import attrgetter
import time
import logging
import os
import random

class Job:

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def __init__(self, process, arrival, burst, priority):
        self.job_no = process             # Process [Identifier]
        self.arrival_time = arrival       # Arrival
        self.burst_time = burst           # Burst Time
        self.priority = priority          # Priority

        self.response_time = self.burst_time    # Response Time

        self.bursted_time = 0
        self.waiting_time = 0

        self.is_current = False           # For diagnostics
        self.is_completed = False         # For diagnostics

        self.queue_order = -1             # Should be set by sorter

    def __str__(self):
        return  "Job {}".format(self.job_no)

    def __repr__(self):
        return "{}: \n\t[Arrival: {}]\n\t[Burst: {}]\n\t[Priority: {}]".format(str(self),
                                                                   self.arrival_time,
                                                                   self.burst_time,
                                                                   self.priority)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def wait(self):
        if not self.is_current:
            if self.burst_time > self.bursted_time:
                self.waiting_time += 1

    def work(self):
        if self.bursted_time < self.burst_time:
            self.bursted_time += 1
            self.response_time = self.burst_time - self.bursted_time

    def is_complete(self):
        if self.bursted_time >= self.burst_time:
            self.is_completed = True
        else:
            self.is_completed = False

        return self.is_completed

    def status(self):
        # Add dying message later
        current = ""
        if self.is_current:
            current = "<< CURRENT"

        complete = ""
        if self.is_completed:
            complete = "[Complete] "

        return "{}{} : [{}s/{}s][Rem. {}][Wait:{}s] {}".format(complete, str(self), self.bursted_time, self.burst_time,
                                                               self.response_time, self.waiting_time, current)

class ProcessingUnit:

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def __init__(self):
        self.valid_modes = {
            "FCFS":self.sched_fcfs,
            "SJF":self.sched_sjf,
            "SRPT":self.sched_srpt,
            "Priority":self.sched_priority,
            "Round Robin":self.sched_roundrobin
        }

        self.file_data = None   # Data from file reading

        self.local_queue = []   # Current working queue
        self.task_list = []     # Complete task list (from input)
        self.queue = []

        self.current_job = None
        self.completed_jobs = []

        self.cycle_no = 0
        self.is_initialized = False

        self.average_waiting_time = 0
        self.total_waiting_time = 0

        self.mode = "FCFS"

        self.quantum = 4
        self.quantum_counter = 0

        self.flag = True
        self.counter = 0

        self.iterator = 0
        pass

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def sched_fcfs(self):
        if not self.is_initialized:
            # Code for initialization
            self.local_queue = sorted(self.task_list, key=attrgetter('job_no'))

            order = 1
            for item in self.local_queue:
                item.queue_order = order
                order += 1

            self.is_initialized = True
        else:
            if not self.current_job:
                self.set_current(self.local_queue.pop(0))

            # print self.current_job

            self.current_job.work()

            if self.current_job.is_complete():
                self.clear_current()
            # Waits all inactive tasks
            self.wait_tasks()
            self.cycle_no += 1

    def sched_sjf(self):
        if not self.is_initialized:
            # Code for initialization
            self.local_queue = sorted(self.task_list, key=attrgetter('burst_time'))

            order = 1
            for item in self.local_queue:
                item.queue_order = order
                order += 1

            self.is_initialized = True
        else:
            if not self.current_job:
                self.set_current(self.local_queue.pop(0))

            # print self.current_job

            self.current_job.work()

            if self.current_job.is_complete():
                self.clear_current()
            # Waits all inactive tasks

            self.wait_tasks()
            self.cycle_no += 1


    def sched_srpt(self):
        if not self.is_initialized:
            # Code for initialization
            self.queue = sorted(self.task_list, key=attrgetter('arrival_time')) # Remove Later

            self.is_initialized = True
        else:
            # new_entry = False

            if self.queue:
                self.print_pseudo_queue()
                # time.sleep(2)
                while self.queue[0].arrival_time == self.cycle_no:
                    self.local_queue.append(self.queue.pop(0))
                    # new_entry = True

                    if not self.queue:
                        break

            if self.local_queue:
                # if new_entry:
                self.clear_current()

                # self.print_queue()    # Remove Later
                # time.sleep(3)         # Remove Later

                self.local_queue = sorted(self.local_queue, key=attrgetter('job_no'))  
                self.local_queue = sorted(self.local_queue, key=attrgetter('response_time'))
                # self.local_queue = sorted(self.local_queue, key=attrgetter('burst_time'))

                order = 1
                for item in self.local_queue:
                    item.queue_order = order
                    order += 1

                if not self.current_job:
                    self.set_current(self.local_queue[0])
                
            if self.current_job:
                self.current_job.work()

                if self.current_job.is_complete():
                    self.local_queue.remove(self.current_job)
                    self.counter += 1
                    self.clear_current()

            # Waits all inactive tasks
            self.wait_tasks()
            self.cycle_no += 1

    def sched_priority(self):
        if not self.is_initialized:
            # Code for initialization
            self.local_queue = sorted(self.task_list, key=attrgetter('job_no'))
            self.local_queue = sorted(self.local_queue, key=attrgetter('priority'))

            order = 1
            for item in self.local_queue:
                item.queue_order = order
                order += 1

            self.is_initialized = True
        else:
            if not self.current_job:
                self.set_current(self.local_queue.pop(0))

            # print self.current_job

            self.current_job.work()

            if self.current_job.is_complete():
                self.clear_current()
            # Waits all inactive tasks
            self.wait_tasks()
            self.cycle_no += 1

    def sched_roundrobin(self):
        if not self.is_initialized:
            # Code for initialization
            self.task_list = sorted(self.task_list, key=attrgetter('job_no'))
            self.local_queue = sorted(self.task_list, key=attrgetter('job_no'))

            order = 1
            for item in self.local_queue:
                item.queue_order = order
                order += 1

            self.is_initialized = True
        else:
            if not self.current_job:
                index = self.iterator % len(self.task_list)
                
                self.set_current(self.task_list[index])

                while self.current_job.is_complete():
                    self.iterator+=1
                    index = self.iterator % len(self.task_list)
                    self.set_current(self.task_list[index])

            # print self.current_job

            self.current_job.work()

            self.quantum_counter += 1

            if self.current_job.is_complete():
                self.local_queue.remove(self.current_job)
                self.clear_current()
                self.quantum_counter = 0

            # Waits all inactive tasks
            self.wait_tasks()
            self.cycle_no += 1

            if self.quantum_counter >= self.quantum:
                self.clear_current()
                self.iterator += 1
                self.quantum_counter = 0

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def load_data(self, filename):
        default_directory = "Processes/"
        file_path = os.path.join(default_directory, filename)

        with open(file_path) as f:
            data = f.read().split("\n")


        # Instantiate each line into self.task_list
        skip = True
        for datum in data:
            # print datum
            if skip:
                skip = False
            else:
                info = [int(s) for s in datum.split() if s.isdigit()]
                self.task_list.append(self.create_job(info))

    def process(self):
        # Returns False if finished
        if self.is_initialized:
            if self.mode == "SRPT":
                if self.counter >= len(self.task_list) and self.current_job == None and len(self.local_queue) <= 0:
                    return False
            else:
                if len(self.local_queue) <= 0 and self.current_job == None:
                    return False

        if self.mode in self.valid_modes:
            self.valid_modes[self.mode]()
        else:
            print "Invalid Input"

        return True

    def wait_tasks(self):
        for task in self.local_queue:
            task.wait()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    # Sets the new current after clearing the old current
    def set_current(self, item):
        if self.current_job:
            self.current_job.is_current = False

        self.current_job = item
        self.current_job.is_current = True

    def clear_current(self):
        if self.current_job:
            self.current_job.is_current = False

        self.current_job = None

    # ??? load_data() does better
    def set_data(self, datum):
        self.file_data = datum

    def set_mode(self, new_mode):
        if new_mode not in self.valid_modes:
            return False

        self.mode = new_mode
        return True

    def create_job(self, info):
        # Job(self, process, arrival, burst, priority)
        return Job(info[0], info[1], info[2], info[3])


    def get_wait_times(self):
        self.total_waiting_time = 0

        for item in self.task_list:
            self.total_waiting_time += item.waiting_time

        self.average_waiting_time = self.total_waiting_time/float(len(self.task_list))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def print_task_list(self):
        print "\nTask List:"

        for task in self.task_list:
            print "\t{}".format(task.status())

    def print_queue(self):
        print "\nLocal Queue:"

        for task in self.local_queue:
            print "\t{}".format(task.status())

    def print_in_order(self):
        listing = sorted(self.task_list, key=attrgetter('queue_order'))

        for task in listing:
            if task.queue_order > 0:
                print "\t{}".format(task.status())

    def print_pseudo_queue(self):
        print "\nPseudo Queue:"

        for task in self.queue:
            print "\t{}".format(task.status())

    def display(self):
        self.print_task_list()
        # self.print_in_order()

        self.get_wait_times()

        print ""
        print "Total Waiting Time:   {}".format(self.total_waiting_time)
        print "Average Waiting Time: %.2f" % self.average_waiting_time

        print ""
        print "Remaining Jobs: {}".format(len(self.local_queue))

        print ""
        print "No. of Jobs:    {}".format(len(self.task_list))
        print "No. of Cycles:  {}".format(self.cycle_no)

        # self.print_pseudo_queue()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #  

def test():
    # default_directory = "Processes/"

    # filename = input("File Name: ")
    # file_path = os.path.join(default_directory, filename)

    # with open(file_path) as f:
    #     data = f.read().split("\n")

    # for line in data:
        # print line

    core = ProcessingUnit()

    core.load_data("process1.txt")
    core.set_mode("FCFS")
    # core.set_mode("SJF")
    # core.set_mode("SRPT")
    # core.set_mode("Priority")
    # core.set_mode("Round Robin")

    while core.process():
        os.system('cls' if os.name == 'nt' else 'clear')
        # core.print_task_list()
        core.display()
        time.sleep(0.1)

    # core.set_current(core.local_queue[0])
    # core.print_task_list()
    # core.print_queue()
    # job_list = []

    # skip = True
    # for line in data:
    #     if skip:
    #         skip = False
    #     else:
    #         skim = [int(s) for s in line.split() if s.isdigit()]
    #         job_list.append(core.create_job(skim))

    # for job in job_list:
    #     print repr(job)


# test()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #  

if __name__ == "__main__":
    valid_modes = [
            "Exit",
            "FCFS",         # 1
            "SJF",          # 2
            "SRPT",         # 3
            "Priority",     # 4
            "Round Robin"   # 5
        ]

    exit = False
    error_msg = ""

    os.system('cls' if os.name == 'nt' else 'clear')

    while not exit:
        core = ProcessingUnit()

        if error_msg is not "":
            os.system('cls' if os.name == 'nt' else 'clear')

        print "Valid Modes:"
        print "\t[1] - FCFS"
        print "\t[2] - SJF"
        print "\t[3] - SRPT"
        print "\t[4] - Priority"
        print "\t[5] - Round Robin"

        print "\n\t[0] : Exit()"

        print "\n{}\n".format(error_msg)

        error_msg = ""

        try:
            option = input("Mode: ")
            valid_modes[option]
        except :
            error_msg = "Invalid Selection."

        if error_msg is "":
            if option is 0:
                exit = True
                break

            try:
                filename = input("File: ")
                core.load_data(filename)
            except:
                error_msg = "File Error."

        if error_msg is "":
            core.set_mode(valid_modes[option])

            while core.process():
                os.system('cls' if os.name == 'nt' else 'clear')
                # core.print_task_list()
                core.display()
                time.sleep(0.1)

            print "\n"