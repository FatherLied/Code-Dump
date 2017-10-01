from threading import Thread
import time
import logging
import random
import os

logging.basicConfig(format="%(message)s", level=logging.DEBUG)

class Resource():
    """
    Resource:
        holds availability value
        holds status
        hold current user
        # for future iterations should be able to hold buffers
    """
    count = 1
    debug = False

    @classmethod
    def increment(cls):
        cls.count += 1

    @classmethod
    def toggle_debug(cls):
        if cls.debug:
            cls.debug = False
        else:
            cls.debug = True

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    # Requires list of resources
    def __init__(self):
        self.name = "Resource({})".format(self.count)
        self.increment()

        self.busy = False
        self.queue = []

        self.current_user = None
        self.task_timer = 0
    
    def start(self):
        self.queue = sorted(self.queue, key=lambda user: int(str(user[0])[5:-1]) )

    def cycle(self):
        if not self.busy:
            if len(self.queue) > 0:
                self.current_user = self.queue.pop(0)
                self.task_timer = self.current_user[1]
                self.busy = True
        else:
            if self.task_timer <= 0:
                self.current_user = None
                self.busy = False

            self.task_timer -= 1

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def status(self):
        if self.current_user is None:
            if len(self.queue) > 0:
                return "{}:  Loading next user".format(self.name)
            return "{}:  Currently idle".format(self.name)
        else:
            return "{}:  Working on {} ({}s), {} user(s) in waiting".format(self.name, self.current_user[0], self.task_timer, len(self.queue))

    def is_empty(self):
        if len(self.queue)<=0 and not self.busy:
            return True
        else:
            return False

    def enqueue(self, task):
        self.queue.append(task)

    def __str__(self):
        return self.name

class User():
    """
    User:
        holds resource wanted to use
        has timer
    """
    count = 1
    debug = False

    @classmethod
    def increment(cls):
        cls.count += 1

    @classmethod
    def toggle_debug(cls):
        if cls.debug:
            cls.debug = False
        else:
            cls.debug = True

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    # Requires list of resources
    def __init__(self, resource_pool):
        self.name = "User({})".format(self.count)
        self.increment()

        resource_list = []
        sample_size = random.randint(1, len(resource_pool))
        sample = random.sample(resource_pool, sample_size)

        for item in sample:
            resource_list.append((item.name, self.name, random.randint(1, 30)))

        self.requested_resources = resource_list

    def request_list(self):
        return self.requested_resources



    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def __str__(self):
        return self.name

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

class DisplayThread(Thread):
    running = True
    refresh_rate = 0.1

    def __init__(self, resource_pool, user_pool, task_list):
        Thread.__init__(self)
        self.resources = resource_pool
        self.users = user_pool
        self.task_list = task_list
        self.running = True

    def shut_down(self):
        self.running = False

    def inititialize(self):
        for item in self.task_list:
            index = int(str(item[0])[9:-1])
            new_item = (item[1], item[2])
            self.resources[index-1].enqueue(new_item)

        for resource in self.resources:
            resource.start()

    def run(self):
        """ Test start """

        # for i in range(0,5):
        #     os.system('cls' if os.name == 'nt' else 'clear')
        #     print "Done in {}".format(i+1)
        #     time.sleep(0.5)

        """ Test end """

        self.inititialize()

        while self.running:            
            """
            Main display here
            """

            self.refresh_screen()

            logging.info("\nWorking on {} Tasks of {} User(s) at {} Resource(s)\n".format(len(self.task_list), len(self.users), len(self.resources)))

            # logging.info("Tasks remaining: {}".format(len(self.task_list)))

            time.sleep(self.refresh_rate)
            self.global_status()

        self.refresh_screen()

    def refresh_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

        for resource in self.resources:
            logging.info(resource.status())

        for resource in self.resources:
            resource.cycle()

    def global_status(self):
        for resource in self.resources:
            if len(resource.queue)>0 or resource.current_user is not None:
                self.running = True
                return

        self.running = False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #   

if __name__ == "__main__":
    no_of_users = random.randint(1,30)
    no_of_resources = random.randint(1,30)

    resource_pool = []
    user_pool = []

    tasks = []

    for i in range(0, no_of_resources):
        resource_pool.append(Resource())

    for i in range(0, no_of_users):
        user_pool.append(User(resource_pool))

    for user in user_pool:
        for request in user.request_list():
            tasks.append(request)

    tasks = list(set(tasks))


    display = DisplayThread(resource_pool, user_pool, tasks)

    display.start()

    display.join()

    logging.info("\nAll {} Tasks Completed of {} User(s) at {} Resource(s)".format(len(tasks), len(user_pool), len(resource_pool)))