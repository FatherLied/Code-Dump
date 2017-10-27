import os
import time

fps = 1

class Job:

    def __init__(self, no, time, size):
        self.job_no = no
        self.size = size

        self.burst_time = time
        self.working_time = 0

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

    def completed_at(self, time):
        self.return_time = time
        

    def status(self):
        return "Job {:>2}({:>3}/{:<3})".format(self.job_no,
                                                self.working_time,
                                                self.burst_time)


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def is_completed(self):
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

        # Bucket List
        self.buckets = []

        # Job List (All Jobs)
        self.jobs = []

        # Jobs in waiting / Queue
        self.in_waiting = []

        self.create_jobs(jobs)
        self.create_buckets(buckets)

        # Instance Mode (First Fit, Best Fit, Worst Fit)
        self.mode = None

        # Cycle Counter
        self.cycle = 0

        # Job Completion Counter
        self.done = 0

        # Average Execution/Return Time
        self.avg_return = 0

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def create_buckets(self, buckets):
        i = 1
        for bucket in buckets:
            # Bucket [bucket_no, bucket_size, stored_job]
            new_bucket = [i, bucket, None]
            self.buckets.append(new_bucket)

            i += 1

    def create_jobs(self, jobs):
        for job in jobs:
            job_object = Job(len(self.jobs) + 1,
                             job[0], # Time
                             job[1]) # Size

            self.jobs.append(job_object)
            self.in_waiting.append(job_object)

    # Only needs bucket_size
    def add_bucket(self, bucket_size):
        new_bucket = [len(self.buckets) + 1, bucket_size, None]
        self.buckets.append(new_bucket)

    # Requires a Job Tuple = (burst_time, job_size)
    def add_jobs(self, job_tuple):
        job_object = Job(len(self.jobs) + 1,
                         job_tuple[0], # Time
                         job_tuple[1]) # Size

        self.jobs.append(job_object)
        self.in_waiting.append(job_object)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def process(self):
        if self.mode is None or self.mode not in self.assign:
            return "Mode not Set Correctly."

        if self.done < len(self.jobs):
            """ 
            Main Loop 
            """

            """ Job Assignment """
            # For every item in queue, attempt to assign
            new_queue = []
            while len(self.in_waiting) > 0:
                reject = self.assign_bucket(self.in_waiting.pop(0))

                if reject:
                    new_queue.append(reject)

            self.in_waiting = new_queue

            for item in self.in_waiting:
                print item

            # for job in self.in_waiting:
            #     self.assign_bucket(job) # Does nothing on failure

            # Increments clock
            self.cycle += 1

            """ Job Process """

            # Parses each bucket
            for bucket in self.buckets:
                # Note: Bucket = [bucket_no, bucket_size, stored_job]
                current_job = bucket[2]

                if current_job is not None:
                    if current_job.is_completed():
                        # Logs Execution Time
                        current_job.completed_at(self.cycle)

                        # Increments completion counter
                        self.done += 1

                        # Empties job in bucket
                        bucket[2] = None

                        # os.system('cls' if os.name == 'nt' else 'clear') # Remove Later

                        # print("Current: {}".format(current_job)) # Remove Later

                        # print("\nOld Queue:")                 # Remove Later
                        # for item in self.in_waiting:   # Remove Later
                        #     print(item)                   # Remove Later

                        # # Removes Job from Queue
                        # self.in_waiting.remove(current_job)

                        # print("\nNew Queue:")                 # Remove Later
                        # for item in self.in_waiting:   # Remove Later
                        #     print(item)                   # Remove Later

                        # time.sleep(fps) # Remove Later
                    else:
                        current_job.work()

            trail = "."
            trail *= self.cycle % 3 + 1
            return "Processing{}".format(trail)
        else:
            return "All Tasks Complete."

    def assign_bucket(self, job):
        """
        Job Assignment Switch
        - Relies on object's current mode
        """
        self.assign[self.mode](job)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def first_fit(self, job):
        for bucket in self.buckets:

            # os.system('cls' if os.name == 'nt' else 'clear')    # Remove Later
            # print ("Old Bucket : {}".format(bucket))                # Remove Later

            if bucket[2] is None:
                if bucket[1] >= job.size:
                    bucket[2] = job
                    return None

            # print ("New Bucket : {}".format(bucket))                # Remove Later

            # time.sleep(fps)                                     # Remove Later
        
        return job

    def best_fit(self, job):
        i = 0   # Index
        b = -1  # Best Bucket
        for bucket in self.buckets:
            if bucket[2] is None:
                if bucket[1] >= job.size:
                    if bucket[1] - job_size < self.buckets[b][1] - job_size \
                     or b == -1:
                        b = i
            i += 1

        if b > -1:
            self.buckets[b][2] = job
            return True
        
        return False

    def worst_fit(self, job):
        i = 0   # Index
        b = -1  # Best Bucket
        for bucket in self.buckets:
            if bucket[2] is None:
                if bucket[2] >= job.size:
                    if bucket[1] - job_size > self.buckets[b][1] - job_size \
                     or b == -1:
                        b = i
            i += 1

        if b > -1:
            self.buckets[b][2] = job
            return True
        
        return False
        
        return False

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def set_mode(self, new_mode):
        if new_mode not in self.assign:
            return False

        self.mode = new_mode

        return True

    # Displays Current Process as a Frame
    def display(self):
        print("Buckets:")

        print("\t-----------------------------------------")

        for bucket in self.buckets:
            job = None

            if bucket[2] is not None:
                job = bucket[2].status()

            print("\t| Bucket {:<2} | {:>4}mb | {:<16} |".format(bucket[0],
                                                                 bucket[1],
                                                                 job))

        print("\t-----------------------------------------")

        self.avg_return = 0
        if self.done > 0:
            total_return = 0

            for item in self.jobs:
                if item.is_completed():
                    total_return += item.return_time

            self.avg_return = total_return / float(self.done)


        print("Average Execution Time: {:.2f}".format(self.avg_return))
        print("Cycle: {:>2}".format(self.cycle)) 

        print("{} out of {} Jobs completed.".format(self.done, len(self.jobs)))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def test(main_jobs, main_buckets):
    # MemoryManager(buckets, jobs)
    manager = MemoryManager(main_buckets, main_jobs)

    manager.set_mode("First")
    while(True):
        os.system('cls' if os.name == 'nt' else 'clear')
        manager.display()

        status = manager.process()
        print("Status: {}".format(status))

        # print("\nJob List:")
        # for job in manager.jobs:
        #     print(job)

        # print("\nBucket List:")
        # for bucket in manager.buckets:
        #     print(bucket)

        # print("\nQueue:")
        # for item in manager.in_waiting:
        #     print(item)

        time.sleep(fps)

        if status is "All Tasks Complete." or status is "Mode not Set Correctly.":
            break

    # print("\nJob List:")
    # for job in manager.jobs:
    #     print(job)

    # print("\nBucket List:")
    # for bucket in manager.buckets:
    #     print(bucket)

    # print("\nQueue:")
    # for item in manager.in_waiting:
    #     print(item)

    # print manager.jobs

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