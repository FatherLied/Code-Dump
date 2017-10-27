import os
import time

fps = 0.1

class Job:

    def __init__(self, no, time, size):
        self.job_no = no
        self.size = size

        self.burst_time = time
        self.working_time = 0
        self.waiting_time = 0

        # Diagnostics
        self.return_time = -1


    def __str__(self):
        return "| Job {:<2} | {:>3} | {:>5} |".format(self.job_no,
                                                  self.burst_time,
                                                  self.size)

    def __repr__(self):
        # return "(Job {}, {}, {})".format(self.job_no,
        #                                           self.burst_time,
        #                                           self.size)
        return self.status()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def work(self):
        if self.working_time < self.burst_time:
            self.working_time += 1

    def wait(self):
        self.waiting_time += 1

    def completed_at(self, time):
        self.return_time = time

    def status(self):
        return "Job {:>2}({:>3}/{:<3})".format(self.job_no,
                                                self.working_time,
                                                self.burst_time)


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def is_complete(self):
        if self.working_time >= self.burst_time:
            return True
        else:
            return False

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def copy(self):
        dupe = Job(no = self.no,
                   time = self.burst_time,
                   size = self.size)

        return dupe

class MemoryManager:

    def __init__(self, buckets, jobs):
        self.assign = {
            "First": self.first_fit,
            "Best" : self.best_fit,
            "Worst": self.worst_fit
        }

        # Buckets
        self.buckets = []
        self.size = []

        # Histogram
        self.histogram = {}
        self.utility = []

        # Jobs
        self.jobs = []

        # Instance Mode (First Fit, Best Fit, Worst Fit)
        self.mode = "First"

        # Cycle Counter
        self.cycle = 0

        # Job Completion Counter
        self.done = 0

        # Impossible Jobs
        self.oversized = 0

        # Average Execution/Return Time
        self.avg_return = 0
        self.avg_waiting = 0
        self.max_queue = 0

        self.fragmentation = 0
        self.insertions = 0

        self.mem_cap = 0

        self.create_buckets(buckets)
        self.create_jobs(jobs)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def create_buckets(self, buckets):
        for bucket in buckets:
            if bucket > self.mem_cap:
                self.mem_cap = bucket

            self.histogram[len(self.buckets)] = 0
            self.size.append(bucket)
            self.buckets.append(None)
            self.utility.append(0)

    def create_jobs(self, jobs):
        for job in jobs:
            job_object = Job(len(self.jobs) + 1,
                             job[0], # Time
                             job[1]) # Size

            self.jobs.append(job_object)

    # Only needs bucket_size
    def add_bucket(self, bucket_size):
        if bucket_size > self.mem_cap:
            self.mem_cap = bucket_size
        self.histogram[len(self.buckets)] = 0

        self.size.append(bucket_size)
        self.bucket.append(None)
        self.utility.append(0)

    # Requires a Job Tuple = (burst_time, job_size)
    def add_jobs(self, job_tuple):
        job_object = Job(len(self.jobs) + 1,
                             job_tuple[0], # Time
                             job_tuple[1]) # Size
        self.jobs.append(job_object)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def process(self):
        if self.done < len(self.jobs):
            for job in self.jobs:
                if not job.is_complete() and job not in self.buckets:
                    self.assign_bucket(job)

        for job in self.buckets:
            if job:
                job.work()

        self.cycle += 1

        for i in range(len(self.buckets)):
            job = self.buckets[i]

            if job is not None and job.is_complete():
                job.completed_at(self.cycle)
                self.done += 1
                self.buckets[i] = None

        i = 0
        for job in self.jobs:
            if job not in self.buckets:
                job.wait()

            if job is not None and job.size > self.mem_cap:
                i += 1
        self.oversized = i


    def assign_bucket(self, job):
        """
        Job Assignment Switch
        - Relies on object's current mode
        """
        self.assign[self.mode](job)

    def is_complete(self):
        return self.done + self.oversized >= len(self.jobs)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def first_fit(self, job):
        for i in range(len(self.buckets)):
            if not self.buckets[i] and self.size[i] >= job.size:
                self.fragmentation += self.size[i] - job.size
                self.insertions += 1

                self.buckets[i] = job
                self.histogram[i] += 1
                break

    def best_fit(self, job):
        best = -1

        for i in range(len(self.buckets)):
            if not self.buckets[i] and self.size[i] >= job.size:  
                if best < 0:
                    best = i
                else:
                    if self.size[i] - job.size < self.size[best] - job.size:
                        best = i

        if best >= 0:
            self.fragmentation += self.size[best] - job.size
            self.insertions += 1

            self.buckets[best] = job
            self.histogram[best] += 1


    def worst_fit(self, job):
        worst = -1

        for i in range(len(self.buckets)):
            if not self.buckets[i] and self.size[i] >= job.size: 
                if worst < 0:
                    worst = i
                else:
                    if self.size[i] - job.size > self.size[worst] - job.size:
                        worst = i

        if worst >= 0:
            self.fragmentation += self.size[worst] - job.size
            self.insertions += 1

            self.buckets[worst] = job
            self.histogram[worst] += 1

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def total(self):
        mass = 0

        for k in self.histogram:
            mass += self.histogram[k]

        return mass

    def avg_return_time(self):
        self.avg_return = 0
        if self.done > 0:
            total_return = 0

            for item in self.jobs:
                if item:
                    if item.is_complete():
                        total_return += item.return_time

            self.avg_return = total_return / float(self.done)

        return self.avg_return

    def avg_waiting_time(self):
        if self.cycle <= 0:
            self.avg_waiting = float(0)
        else:
            count = 0
            for job in self.jobs:
                count += job.waiting_time

            self.avg_waiting = count / float(self.cycle)

        return self.avg_waiting

    def max_queue_length(self):
        if self.cycle <= 0:
            self.max_queue = 0
        else:
            c = 0
            for job in self.jobs:
                if job not in self.buckets and not job.is_complete():
                    c += 1
            
            if c > self.max_queue:
                self.max_queue = c

        return self.max_queue

    def avg_fragmentation(self):
        if self.insertions <= 0:
            return 0
        else:
            return self.fragmentation / self.insertions

     # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def set_mode(self, new_mode):
        if new_mode not in self.assign:
            return False

        self.mode = new_mode

        return True

    # Displays Current Process as a Frame
    def display(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        print("Buckets: {}-Fit".format(self.mode))

        print("\t--------------------------------------------------")

        for i in range(len(self.buckets)):
            if self.buckets[i]:
                status = self.buckets[i].status()
            else:
                status = None

            if self.total() <= 0:
                self.utility[i] = float(0)
            else:
                self.utility[i] = (self.histogram[i] / float(self.total())) * 100
            
            print("\t| Bucket {:<2} | {:>4}mb | {:<16} | {:>5.1f}% |".format(
                    i + 1, self.size[i], status, self.utility[i]
                ))

        print("\t--------------------------------------------------")

        print("Average Execution Time: {:.2f}".format(self.avg_return_time()))
        print("Average Waiting Time: {:.2f}".format(self.avg_waiting_time()))

        print("\nMax Queue Length: {}".format(self.max_queue_length()))
        print("Average Internal Fragmentation: {}mb".format(self.avg_fragmentation()))

        print("\nCycle: {:>2}".format(self.cycle)) 

        print("\n{} out of {} Jobs completed.".format(self.done, len(self.jobs)))
        print("{} oversized jobs.".format(self.oversized))

        # self.print_jobs()

    def print_jobs(self):
        print("\nJobs:")
        print("-------------------------------------")
        for job in self.jobs:
            print("| {:<16} | {:>4}mb | {:>5} |".format(job.status(),
                                                job.size,
                                                str(job.is_complete())))
        print("-------------------------------------\n")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def test(main_jobs, main_buckets):
    # MemoryManager(buckets, jobs)
    manager = MemoryManager(main_buckets, main_jobs)

    if not manager.set_mode("First"):
    # if not manager.set_mode("Best"):
    # if not manager.set_mode("Worst"):
        raise Exception("Invalid Mode")

    manager.display()

    # for key, value in manager.histogram.items():
        # print("{}: {}".format(key, value))

    while not manager.is_complete():
        manager.process()
        manager.display()
        # raw_input("Press Enter to continue...")
        time.sleep(fps)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

if __name__ == "__main__":
    jobs = [
        # Job = (burst_time, job_size)
        (  5 , 5760 ),  # 1
        (  4 , 4190 ),  # 2
        (  8 , 3290 ),  # 3
        (  2 , 2030 ),  # 4
        (  2 , 2550 ),  # 5
        (  6 , 6990 ),  # 6
        (  8 , 8940 ),  # 7
        ( 10 , 740  ),  # 8
        (  7 , 3930 ),  # 9
        (  6 , 6890 ),  # 10
        (  5 , 6580 ),  # 11
        (  8 , 3820 ),  # 12
        (  9 , 9140 ),  # 13
        ( 10 , 420  ),  # 14
        ( 10 , 220  ),  # 15
        (  7 , 7540 ),  # 16
        (  3 , 3210 ),  # 17
        (  1 , 1380 ),  # 18
        (  9 , 9850 ),  # 19
        (  3 , 3610 ),  # 20
        (  7 , 7540 ),  # 21
        (  2 , 2710 ),  # 22
        (  8 , 8390 ),  # 23
        (  5 , 5950 ),  # 24
        ( 10 , 760  )   # 25
    ]

    buckets = [
        9500,
        7000,
        4500,
        8500,
        3000,
        9000,
        1000,
        5500,
        1500,
         500
    ]

    test(jobs, buckets) # Remove Later


"""
V2 Improvement Notes:
    - Use Indexing instead of relying on the Python List functions
      (Check if task is compeleted before trying to fit it in a bucket)
    - Implement a fit() and remainder() functions for Job Class
      (Or combine both into 1, if results is < 0 then it can be said that it can't fit.)
"""