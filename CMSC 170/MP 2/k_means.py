import math
import matplotlib.pyplot as plt
from random import randrange
from PIL import Image
from time import sleep
import os
import sys

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

img_extensions = [
        'PNG',
        'JPEG',
        'JPG',
        'BMP',
        'GIF'
]

custom = {
    'centroids_txt': [
        [3,3],
        [6,2],
        [8,5]
    ],
    'centroids_img': [

    ],
    'limit': 16,
    'iterate': 10,
    'custom': False
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def euclid_dist(x_feat, centroid_feat):
    if len(centroid_feat) > len(x_feat):
        raise IndexError("mismatch in features")

    total_dist = 0
    for i in range(len(x_feat)):
        total_dist += (x_feat[i] - centroid_feat[i])**2

    return math.sqrt(total_dist)

def new_centroid(c_points):
    # c_points should be a 2D Array or at least a list of tuples with all features
    centroid = []

    # k = len(c_points[0])
    # m = len(c_points)

    k = len(c_points[0])
    m = len(c_points)

    print("  k: {}, m: {}".format(k,m))   # Remove Later

    for i in range(k):
        centroid.append(0)

    for point in c_points:
        for i in range(len(point)):
            centroid[i] += point[i]

    for i in range(k):
        centroid[i] /= float(m)

    return centroid


def j_score(minimums):
    total_dist = 0
    for item in minimums:
        total_dist = float(total_dist) + item

    return total_dist / len(minimums)
    

def package(filename):
    # Packages file into a dictionary
    package = {}
    segments = filename.split('.')

    global img_extensions

    if len(segments) <= 1:
        package['type'] = "NONE"
    else:
        package['type'] = segments[len(segments) - 1].upper()

    package['file_name'] = filename

    # print(package['type']) # Remove Later

    try:
        with open(filename) as file:
            if package['type'] not in img_extensions:
                package['x_values'] = []
                package['y_values'] = []
                package['features'] = []

                data = file.read()
                lines = data.splitlines()

                for line in lines:
                    split = line.split(' ')
                    error = split
                    # print("\n\tSplit: {}\n".format(split)) # Remove Later
                    values = []
                    for item in split:
                        
                        try:
                            values.append(float(item))
                        except ValueError:
                            pass

                        if len(values) >= 2:
                            break

                    if len(values) < 2:
                        raise ValueError('cannot convert to floats: {}'.format(split))

                    # error = split[1]
                    package['x_values'].append(values[0])

                    # error = split[2]
                    package['y_values'].append(values[1])

                    package['features'].append([values[0], values[1]])
            else:
                package['image'] = Image.open(filename)

                if package['type'] == 'GIF':
                    raise ValueError("unsupported format")

                if package['image'].mode != 'RGB':
                    package['image'] = package['image'].convert('RGB')

                package['features'] = list(package['image'].getdata())
                package['size'] = package['image'].size


    except IOError:
        print("IOError: [Errno2] No such file or directory: '{}'".format(filename))
    except IndexError:
        print("IndexError: file data index invalid")
    except ValueError, e:
        if package['type'] not in img_extensions:
            print("ValueError: {}".format(str(e)))
        else:
            print("ValueError: image invalid")

    # print(package) # Remove Later

    return package

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

# Toggle variable for plotting
toggle = 0

class Cluster:
    def __init__(self, filename):
        global img_extensions

        # Data for each iteration
        self.iterations = []

        # Iteration counter
        self.iter = 0

        self.k = 0  # Number of clusters/centroids
        self.m = 0  # Number of items
        self.n = 0  # Number of features

        # self.centroids

        self.data_pack = package(filename)
        self.assign_centroids()

    def assign_centroids(self, centroids=None):
        global img_extensions
        global custom

        # self.centroids = []

        if centroids:
            self.centroids = custom
        else:
            if self.data_pack['type'] not in img_extensions:
                self.centroids = custom['centroids_txt']
            else:
                if custom['custom']:
                    self.centroids = custom['centroids_img']
                else:
                    indices = []
                    selection = []
                    items = len(self.data_pack['features'])

                    for i in range(items):
                        selection.append(i)

                    while len(indices) < custom['limit'] \
                       and len(indices) < items:
                        indices.append(selection.pop(randrange(len(selection))))

                    self.centroids = []
                    for index in indices:
                        self.centroids.append(self.data_pack['features'][index])

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def iterate(self, count=1):
        global img_extensions
        if count < 1:
            count = 1

        while count > 0:
            iterable = {}

            iterable['no'] = self.iter + 1

            if len(self.iterations) > 0:
                index = len(self.iterations) - 1
                self.centroids = self.iterations[index]['new_centroids']

            """ Feature Loop here """

            iterable['centroids'] = self.centroids

            # Centroid distance
            c_dist = []

            # Centroid assignments
            c_assign = []

            # Minimums
            minimums = []

            # Progress message
            progress = ""

            feat_count = len(self.data_pack['features'])

            for i in range(len(self.data_pack['features'])):
                # print("I: {}".format(i))    # Remove Later

                percent = (i / float(feat_count)) * 100
                label = int(math.floor(20 * (percent / 100)))


                progress = "Progress: [{:<20}] {:3.2f}%\n".format("#" * label, percent)
                progress += "  Iteration {:>2}: ({}/{})".format(iterable['no'],
                                                               i, feat_count)

                dist = []
                for centroid in self.centroids:
                    dist.append(euclid_dist(self.data_pack['features'][i], centroid))

                c_dist.append(dist)
                minimums.append(min(dist))
                c_assign.append(dist.index(minimums[i]) + 1)

            progress = "Progress: [{:<20}] {:3.2f}%\n".format("#" * 20, 100)
            progress += "  Iteration {:>2}: ({}/{})".format(iterable['no'],
                                                               feat_count, feat_count)

            iterable['c_assign'] = c_assign
            """ Feature Loop end """

            iterable['progress'] = progress

            clusters = []
            for item in self.centroids:
                clusters.append([])

            for i in range(len(self.data_pack['features'])):
                clusters[c_assign[i] - 1].append(self.data_pack['features'][i])

            print("Iteration {}:".format(iterable['no']))
            new_centroids = []
            for cluster in clusters:
                new_centroids.append(new_centroid(cluster))

            iterable['new_centroids'] = new_centroids

            iterable['j_score'] = j_score(minimums)
            if self.iter < 1:
                iterable['j_diff'] = 0
            else:
                prev = len(self.iterations) - 1
                iterable['j_diff'] = self.iterations[prev]['j_score'] - iterable['j_score']

            self.iterations.append(iterable)

            if self.data_pack['type'] not in img_extensions:
                self.write(len(self.iterations) - 1)

            self.iter += 1
            count -= 1

        # self.print_status()

    def print_all(self, query):
        if len(self.iterations) < 1:
            print("PrintException: nothing to print")
            return

        if query in self.iterations[0]:
            for i in range(len(self.iterations)):
                sample = self.iterations[i]
                print("Iteration {}:".format(i))
                print("  {} = {}".format(query.capitalize(), sample[query]))

                if i + 1 < len(self.iterations):
                    print("")
        else:
            raise KeyError("'{}': no such key".format(query))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    def write(self, index):
        current_iter = self.iterations[index]

        ca_file = "iter{}_ca.txt".format(index + 1)
        cm_file = "iter{}_cm.txt".format(index + 1)
        
        with open(ca_file, 'w+') as ca, open(cm_file, 'w+') as cm:
            ca_data = ""
            for i in range(len(current_iter['c_assign'])):
                ca_data += str(current_iter['c_assign'][i])

                if i + 1 < len(current_iter['c_assign']):
                    ca_data += "\n"

            ca.write(ca_data)

            cm_data = ""

            i = 0
            for item in current_iter['new_centroids']:
                datum = ""
                for f in range(len(item)):
                    datum += "{:.6f}".format(item[f])

                    if f + 1 < len(item):
                        datum += " "

                cm_data += datum

                if i + 1 < len(current_iter['new_centroids']):
                    cm_data += "\n"
                i += 1

            cm_data += "\nJ={:.6f}".format(current_iter['j_score'])
            cm_data += "\ndJ={:.6f}".format(current_iter['j_diff'])
            cm.write(cm_data)

    def save(self):
        global img_extensions

        if self.data_pack['type'] not in img_extensions:
            raise TypeError("data type should not be plotted")

        last = len(self.iterations) - 1
        latest_iter = self.iterations[last]

        old_centroids = latest_iter['centroids']
        new_centroids = []

        for centroid in old_centroids:
            new_centroid = ()

            for feature in centroid:
                new_centroid += (int(round(feature)),)

            new_centroids.append(new_centroid)

        new_pixels = []

        for i in range(len(self.data_pack['features'])):
            index = latest_iter['c_assign'][i] - 1
            new_pixels.append(new_centroids[index])

        image = Image.new('RGB', self.data_pack['size'])
        image.putdata(new_pixels)

        segments = self.data_pack['file_name'].split(".")
        extension = segments.pop(len(segments) - 1)

        new_file = ".".join(segments)
        path = new_file + "_compressed." + extension
        
        i = 1
        while os.path.isfile(path):
            path = new_file + "_compressed({}).".format(i) + extension
            i += 1

        image.save(path)

    def plot(self):
        """
        Plots every iteration
        """
        global img_extensions

        if self.data_pack['type'] in img_extensions:
            raise TypeError("data type should not be plotted")

        marker_size = 2
        c_marker_size = 10

        if(len(self.iterations) < 1):
            print("PlotException: nothing to plot")
            return

        def onkey(event):
            global toggle

            limit = len(self.iterations)

            if event.key == 'right':
                toggle = (toggle + 1) % limit
            elif event.key == 'left':
                toggle = (toggle - 1) % limit

            event.canvas.figure.clear()
            event.canvas.figure.gca().set_xlabel("Iteration {}".format(toggle + 1))

            current_iter = self.iterations[toggle]
            colors = [
                'red',
                'blue',
                'green'
            ]
            for i in range(len(self.data_pack['features'])):
                coords = self.data_pack['features'][i]
                event.canvas.figure.gca().plot(coords[0], coords[1],
                           marker='o', markersize=marker_size,
                           color=colors[current_iter['c_assign'][i] - 1])

            dark_colors = [
                'xkcd:dark red',
                'xkcd:dark blue',
                'xkcd:dark green'
            ]

            for i in range(len(current_iter['centroids'])):
                centroid = current_iter['centroids'][i]
                event.canvas.figure.gca().plot(centroid[0], centroid[1],
                           marker='x', markersize=c_marker_size,
                           color=dark_colors[i])

            event.canvas.draw()

        fig = plt.figure()
        fig.canvas.mpl_connect('key_press_event', onkey)

        current_iter = self.iterations[0]
        colors = [
            'red',
            'blue',
            'green'
        ]
        for i in range(len(self.data_pack['features'])):
            coords = self.data_pack['features'][i]
            plt.plot(coords[0], coords[1],
                       marker='o', markersize=marker_size,
                       color=colors[current_iter['c_assign'][i] - 1])

        dark_colors = [
            'xkcd:dark red',
            'xkcd:dark blue',
            'xkcd:dark green'
        ]

        for i in range(len(current_iter['centroids'])):
            centroid = current_iter['centroids'][i]
            plt.plot(centroid[0], centroid[1],
                       marker='x', markersize=c_marker_size,
                       color=dark_colors[i])
        
        plt.gca().set_xlabel("Iteration 1")
        plt.show()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def test():
    details = package("kmimg1.png")

    rgb_values = list(details['image'].getdata())
    print(rgb_values)

def main():
    global img_extensions
    global custom

    if len(sys.argv) < 1:
        default = "kmimg1.txt"
    else:
        default = sys.argv[1]

    sample = Cluster(default)
    sample.iterate(custom['iterate'])

    if sample.data_pack['type'] in img_extensions:
        sample.save()
    else:
        sample.plot()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

if __name__ == "__main__":
    main()
    # print(sys.argv[0])
    # test()