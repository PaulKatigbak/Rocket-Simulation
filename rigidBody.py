import numpy as np
from scipy.integrate import ode

class RigidBody:
    def __init__(self, force, torque):
        self.paused = False    # initially running

        # 5000 kg mass for good results
        self.mass = 5000                                  # mass of rocket
        self.Ibody = np.identity(3)                       # inertia tensor
        self.IbodyInv = np.linalg.inv(self.Ibody)         # inverse of inertia tensor
        self.v = np.zeros(3)                              # linear velocity
        self.omega = np.zeros(3)                          # angular velocity

        self.state = np.zeros(19)
        self.state[0:3] = np.zeros(3)                     # position
        self.state[3:12] = np.identity(3).reshape([1,9])  # rotation
        self.state[12:15] = self.mass * self.v            # linear momentum
        self.state[15:18] = np.zeros(3)                   # angular momentum

        # Computed quantities
        self.force = force
        self.torque = torque

        # Setting up the rk4 solver
        self.solver = ode(self.f)
        self.solver.set_integrator('dop853')
        self.solver.set_f_params(self.force, self.torque, self.IbodyInv)

        # Gravitational constant
        self.G = 6.67430e-11 
         
        # Mass and radius of Earth
        self.earth_mass = 5.972e24  # Mass of Earth in kg
        self.earth_radius = 6.371e6  # Radius of Earth in meters

        
        # Flag to control thrust in each direction
        self.thrust = False
        self.left_thrust = False
        self.right_thrust = False

        # to control drag on rocket
        self.drag_coefficient = 0.1 
        self.air_resistance = False

    # to pause or play the simulation
    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    # gets the direction of the thrust (if rocket is tilted, this is needed)
    def get_thrust_direction_body(self):
        _R = self.get_rot()
        thrust_direction_world = np.array([0, 500, 0]) 
        thrust_direction_body = np.dot(_R.T, thrust_direction_world)
        return thrust_direction_body

    # function to compute and update everything
    def f(self, t, state, force, torque, IbodyInv):
        rate = np.zeros(19)
        rate[0:3] = state[12:15] / self.mass  # dv = dx/dt

        _R = state[3:12].reshape([3,3])
        _R = self.orthonormalize(_R)
        Iinv = np.dot(_R, np.dot(IbodyInv, _R.T))
        _L = state[15:18]
        omega = np.dot(Iinv, _L)

        rate[3:12] = np.dot(self.star(omega), _R).reshape([1,9])

        # Calculate distance from the center of the Earth
        distance_to_earth = np.linalg.norm(state[0:3])

        # Calculate gravitational force
        gravitational_force = ((-self.G * self.earth_mass * self.mass)/ ((distance_to_earth + self.earth_radius)**2))/self.mass

        # Add gravitational force to the existing forces
        total_force = [force[0], force[1] + gravitational_force, force[2]]

        # Apply thrust force if the thrust flag is set
        if self.thrust:
            thrust_direction_world = np.array([0, 500, 0])  # thrust along the y-axis since rocket starts off vertically at rest

            # Transform thrust direction to body-fixed coordinates using the updated rotation matrix _R
            thrust_direction_body = np.dot(_R.T, thrust_direction_world)

            # Apply thrust force in direction
            total_force += thrust_direction_body

        # if no thrust, gravity will take over and pull rocket down as long as rocket it not at rest
        elif not self.thrust:
            if distance_to_earth == 0:
                total_force = np.array([0, 0, 0])  
            else:
                total_force = np.array([0, gravitational_force, 0])  

        # Apply torque to tilt the rocket to the right if the left_thrust flag is set (to not spin when on the ground)
        if self.left_thrust and state[1] > 0:
            total_torque = np.array([0, 0, -0.1]) 

        # Apply torque to tilt the rocket to the right if the left_thrust flag is set
        elif self.right_thrust and state[1] > 0:
            total_torque = np.array([0, 0, 0.1])  
        else:
            total_torque = torque

        # for drag (which is optional)  
        if self.air_resistance:

            drag_force_x = -self.drag_coefficient * state[12]  # Drag force in x-direction (-k*v(in x-dir))
            drag_force_y = -self.drag_coefficient * state[13]  # Drag force in y-direction
            total_force[0] += drag_force_x  
            total_force[1] += drag_force_y  
    
        rate[12:15] = total_force
        rate[15:18] = total_torque
        # print(total_force/self.mass)
        return rate

    def star(self, v):
        vs = np.zeros([3,3])
        vs[0][0] = 0
        vs[1][0] = v[2]
        vs[2][0] = -v[1]
        vs[0][1] = -v[2]
        vs[1][1] = 0
        vs[2][1] = v[0]
        vs[0][2] = v[1] 
        vs[1][2] = -v[0]
        vs[2][2] = 0
        return vs;       

    # to orthonormalize 
    def orthonormalize(self, m):
        mo = np.zeros([3,3])
        r0 = m[0,:]
        r1 = m[1,:]
        r2 = m[2,:]
        
        r0new = r0 / np.linalg.norm(r0)
        
        r2new = np.cross(r0new, r1)
        r2new = r2new / np.linalg.norm(r2new)

        r1new = np.cross(r2new, r0new)
        r1new = r1new / np.linalg.norm(r1new)

        mo[0,:] = r0new
        mo[1,:] = r1new
        mo[2,:] = r2new
        return mo

    def get_pos(self):
        return self.state[0:3]

    def get_rot(self):
        return self.state[3:12].reshape([3,3])

    def get_angle_2d(self):
        v1 = [1,0,0]
        v2 = np.dot(self.state[3:12].reshape([3,3]), v1)
        cosang = np.dot(v1, v2)
        axis = np.cross(v1, v2)
        return np.degrees(np.arccos(cosang)), axis

    def prn_state(self):
        print('Pos', self.state[0:3])
        print('Rot', self.state[3:12].reshape([3,3]))
        print('P', self.state[12:15])
        print('L', self.state[15:18])
