
# https://gist.github.com/benrules2/220d56ea6fe9a85a4d762128b11adfba

import math

import random
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class point:
    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z

class body:
    def __init__(self, location, mass, radius, velocity, name = ""):
        self.location = location
        self.mass = mass
        self.radius = radius
        self.velocity = velocity
        self.name = name

def calculate_single_body_acceleration(bodies, body_index):
    G_const = 6.67408e-11 #m3 kg-1 s-2
    acceleration = point(0,0,0)
    target_body = bodies[body_index]
    for index, external_body in enumerate(bodies):
        if index != body_index:
            r = (target_body.location.x - external_body.location.x)**2 + \
                (target_body.location.y - external_body.location.y)**2 + \
                (target_body.location.z - external_body.location.z)**2
            r = math.sqrt(r)
            tmp = G_const * external_body.mass / r**3
            acceleration.x += tmp * (external_body.location.x - target_body.location.x)
            acceleration.y += tmp * (external_body.location.y - target_body.location.y)
            acceleration.z += tmp * (external_body.location.z - target_body.location.z)

    return acceleration

def compute_velocity(bodies, time_step = 1):
    for body_index, target_body in enumerate(bodies):
        acceleration = calculate_single_body_acceleration(bodies, body_index)

        target_body.velocity.x += acceleration.x * time_step
        target_body.velocity.y += acceleration.y * time_step
        target_body.velocity.z += acceleration.z * time_step 


def update_location(bodies, time_step = 1):
    for target_body in bodies:
        target_body.location.x += target_body.velocity.x * time_step
        target_body.location.y += target_body.velocity.y * time_step
        target_body.location.z += target_body.velocity.z * time_step

def compute_gravity_step(bodies, time_step = 1):
    compute_velocity(bodies, time_step = time_step)
    update_location(bodies, time_step = time_step)

def plot_output(bodies, outfile = None):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1, projection='3d')
    max_range = 0
    for current_body in bodies: 
        max_dim = max(max(np.abs(current_body["x"])),max(np.abs(current_body["y"])),max(np.abs(current_body["z"])))
        if max_dim > max_range:
            max_range = max_dim
        ax.plot(current_body["x"], current_body["y"], current_body["z"], c = None, label = current_body["name"])    

        # plot sphere
        u, v = np.linspace(0, np.pi, 13), np.linspace(0, 2 * np.pi, 13)
        x = current_body["x"][-1] + current_body["radius"] * np.outer(np.cos(u), np.sin(v))
        y = current_body["y"][-1] + current_body["radius"] * np.outer(np.sin(u), np.sin(v))
        z = current_body["z"][-1] + current_body["radius"] * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_wireframe(x, y, z, color='k')
    
    ax.set_xlim([-max_range,max_range])    
    ax.set_ylim([-max_range,max_range])
    ax.set_zlim([-max_range,max_range])
    ax.legend()
    
    ax.view_init(elev=90, azim=0)

    if outfile:
        plt.savefig(outfile)
    else:
        plt.show()

def run_simulation(bodies, names = None, time_step = 1, number_of_steps = 10000):

    #create output container for each body
    body_locations_hist = []
    for current_body in bodies:
        body_locations_hist.append({"x":[], "y":[], "z":[], "name":current_body.name, "radius":current_body.radius})
        
    for i in range(1,number_of_steps):
        compute_gravity_step(bodies, time_step = time_step)            
        
        for index, body_location in enumerate(body_locations_hist):
            body_location["x"].append(bodies[index].location.x)
            body_location["y"].append(bodies[index].location.y)           
            body_location["z"].append(bodies[index].location.z)       

    return body_locations_hist

if __name__ == "__main__":
    
    #build list of planets in the simulation, or create your own
    #planet data (location (m), mass (kg), velocity (m/s)
    bodies = [
        body( location = point(0,0,0), mass = 6e24, radius=6371e3, velocity = point(0,0,0), name = "earth"),
        body( location = point(418e3+6371e3,0,0), mass = 4.5e5, radius = 50, velocity = point(0,7.67e3,0), name = "iss"),
        body( location = point(6371e3,0,0), mass = 1e5, radius = 10, velocity = point(0,9e3,0), name = "rocket"),
        ]
    
    motions = run_simulation(bodies, time_step = 10, number_of_steps = 2000)
    plot_output(motions)