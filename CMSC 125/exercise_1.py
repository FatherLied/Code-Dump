from threading import Semaphore, Thread, active_count
import time
import logging
import random
import os

from Queue import Queue

logging.basicConfig(format="[%(threadName)-13s]: %(message)s", level=logging.DEBUG)
logging.basicConfig(format="%(message)s", level=logging.INFO)

class Resource(Thread):
    """
    Resource:
        holds availability value
        holds status
        hold current user
        # for future iterations should be able to hold buffers
    """
    count = 1
    debug = False

    refresh_rate = 1

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

    # Requires Synchronized Queue
    def __init__(self, queue):
        Thread.__init__(self)

        self.name = "Resource({})".format(self.count)
        self.increment()

        # Synchronized Queue
        self.sync_queue = queue

        # List of Users waiting to be processed
        self.local_queue = []

        self.current_user = None
        self.busy = False
        self.task_timer = 0

    def run(self):
        """
        Sorts local queue before starting

        Nested Loop:
            while local queue isn't empty
                loop for n secs
        """


        exit = False
        while not exit:
            try:
                item = self.queue.get(timeout=3)
            except:
                exit = True

            if item[0].name == self.name:
                self.local_queue.append((item[1],item[2]))
            else:
                self.queue.put(item)


        self.log()

        self.local_queue = sorted(self.local_queue, key=lambda user: user[0])

        while len(self.local_queue) > 0:
            """
            User processing logic here
            """
            self.log()

            self.current_user = self.local_queue.pop(0)
            self.busy = True

            self.task_timer = self.current_user[1]
            while self.task_timer > 0:
                self.log()
                time.sleep(self.refresh_rate)
                self.task_timer-=1

            self.sync_queue.task_done()
            self.busy = False

            


    def log(self):
        if self.busy:
            logging.debug("Working on {} ({}s), {} user(s) in waiting".format(self.current_user, self.task_timer, len(self.local_queue)))
            # return ("Working on {} ({}s), {} user(s) in waiting".format(self.current_user, self.task_timer, len(self.local_queue)))
        else:
            if len(self.local_queue) > 0:
                logging.debug("Loading next user")
                # return ("Loading next user")
            else:
                logging.debug("Currently idle")
                # return ("Currently idle")

    def list(self):
        for item in self.local_queue:
            print item

    def receive_item(self, item):
        self.local_queue.append(item)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

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
    """
    DisplayThread

    Console status display
    """
    running = True
    refresh_rate = 0.5

    def __init__(self, resource_pool):
        Thread.__init__(self)
        self.resources = resource_pool
        self.running = True

    def shut_down(self):
        self.running = False

    def run(self):
        """ Test start """

        # for i in range(0,5):
        #     os.system('cls' if os.name == 'nt' else 'clear')
        #     print "Done in {}".format(i+1)
        #     time.sleep(0.5)

        """ Test end """

        while self.running:
            os.system('cls' if os.name == 'nt' else 'clear')
            """
            Main display here
            """

            for resource in self.resources:
                print resource.log()

            print "\nNo. of Active Threads: {}".format(active_count())

            time.sleep(self.refresh_rate)




def main():
    # display_lock = Semaphore()
    # holder = display_lock.acquire()
    logging.debug("test")

    task_list = Queue()

    no_of_users = random.randint(1,30)
    no_of_resources = random.randint(1,30)

    resource_pool = []
    user_pool = []

    for i in range(0, no_of_resources):
        resource_pool.append(Resource(task_list))

    for i in range(0, no_of_users):
        user_pool.append(User(resource_pool))

    # Collecting requests
    for user in user_pool:
        for request in user.request_list():
            task_list.put(request, block=False)

    # tasks = []

    # exit = False
    # while not exit:
    #     try:
    #         item = task_list.get(block=False)
    #     except:
    #         exit = True

    #     tasks.append(item)

    # for item in tasks:
    #     print item

    # logging.debug("Testing")
    # logging.info("\nNo. of Tasks: {}".format(len(tasks)))

    # print "\nNo. of Tasks: {}".format(len(tasks))


    # for item in tasks:
    #     index = int(str(item[0])[9:-1])
    #     new_item = (item[1], item[2])
    #     resource_pool[index-1].receive_item(new_item)

    # for resource in resource_pool:
    #     print ""
    #     print "{}:".format(resource.name)
    #     resource.list()

    for resource in resource_pool:
        resource.start()

    # for resource in resource_pool:
        # logging.info(resource.log())


    """ Use splice [9:-1] to separate the '1' from Resource(1)"""

    # display = DisplayThread(resource_pool)
    # display.start()

    task_list.join()

    # display.shut_down()

    # holder = display_lock.release()

    # display.join()

    print "\nAll Tasks Completed"

# =========================== END OF MAIN =========================== #

main()








def test():
    sample = Queue()

    print "Hello"
    print sample.empty()

    try:
        sample.get(False)
    except:
        print "Queue is Empty"

    resource_pool = []

    for i in range(0,5):
        resource_pool.append(Resource(sample))


    # num = 0
    # for item in resource_pool:
    #     print item
    #     print item == resource_pool[num]
    #     num+=1

    sample_pool = random.sample(resource_pool, 3)

    print ""

    tup = (str(sample_pool[random.randint(1, len(sample_pool) - 1)]), random.randint(1, 3) , "User1")

    print tup

    print ""

    test_user = User(resource_pool)

    print test_user.list_requests()

    """

    monitor = DisplayThread()
    monitor.start()

    monitor.join()

    """

    # for item in sample_pool:
        # print str(item)

    print ""

    test_resource = Resource(sample)

    test_resource.receive_item(("User(4)", 15))
    test_resource.receive_item(("User(1)", 10))
    test_resource.receive_item(("User(2)", 5))

    print sorted(test_resource.local_queue, key=lambda user: user[0])

# test()