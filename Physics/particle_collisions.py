import pygame
import numpy as np
import random

class Particle:
    def __init__(self, pos, vel, acc ,color, radius, surface, id) -> None:
        self.pos = pos 
        self.vel = vel 
        self.acc = acc
        self.color = color
        self.radius = radius
        self.surface = surface
        self.mass = np.pi * self.radius**2
        self.id = id

    def draw(self):
        pygame.draw.circle(self.surface, self.color, (self.pos[0], self.pos[1]), self.radius)
    
    def update(self, dt):
        #self.acc = np.array([0, 0])
        self.vel = self.vel + self.acc * dt
        self.pos = self.pos + self.vel * dt 

    def get_bb(self):
        return np.array([self.pos[0] - self.radius, 
                      self.pos[0] + self.radius, 
                      self.pos[1] - self.radius,
                      self.pos[1] + self.radius]) # [left, right, up, down]

class CollisionMethod:
    def handle_collisions(self, data):
        pass

class ParticleCollisions:
    def __init__(self, strategy: CollisionMethod) -> None:
        self._stragegy = strategy
        self.collisions_counter = 0
    def euler_distance(self, p):
        return np.sqrt((p[0].x[0] - p[1].x[0])**2 + (p[0].y[0] - p[1].y[0])**2)
    
    def handle_frame_collision(self, particle, p_bbox, f_bbox):
        if p_bbox[0] <= f_bbox[0] or p_bbox[1] >= f_bbox[1]:
            self.collisions_counter += 1
            particle.vel[0] = - particle.vel[0]
        if p_bbox[2] <= f_bbox[2] or p_bbox[3] >= f_bbox[3]:
            self.collisions_counter += 1
            particle.vel[1] = - particle.vel[1]

    def update_dynamics(self, particles, dt, frame):
        '''particles is list of objects where each element is a Particle instance,
        pairs_p is a list of lists with the following shape [[x1, y1, radius, mass, v1]]'''
        #p_filtered = self._stragegy.handle_collisions(particles)
        self.collisions_counter = 0
        for p in particles: 
            p.update(dt)
            bbox = p.get_bb()
            self.handle_frame_collision(p, bbox, frame)
        self.handle_particles_collisions(particles)

        print(self.collisions_counter)

    def handle_particles_collisions(self, particles):
        possible_collisions = self._stragegy.handle_collisions(particles)
        for particle, other_particle in possible_collisions:
            if other_particle.id != particle.id:
                dist = np.linalg.norm(particle.pos - other_particle.pos)
                self.collisions_counter += 1
                if dist <= (particle.radius + other_particle.radius):
                    v1, v2 = self.get_resp_vel(particle, other_particle)
                    particle.vel = v1
                    other_particle.vel = v2

    def get_resp_vel(self, p, other_p):
        v1 = p.vel
        v2 = other_p.vel
        m1 = p.mass
        m2 = other_p.mass
        x1 = p.pos
        x2 = other_p.pos

        p_resp = self.compute_velocity(v1, v2, m1, m2, x1, x2)
        other_p_resp = self.compute_velocity(v2, v1, m2, m1, x2, x1)
        return p_resp, other_p_resp

    def compute_velocity(self, v1, v2, m1, m2, x1, x2):
        return v1 - (2 * m2 / (m1 + m2)) * np.dot(v1 - v2, x1 - x2) / np.linalg.norm(x1 - x2) ** 2 * (x1 - x2)

class SweepPrune(CollisionMethod):
    def handle_collisions(self, particles):
        # implements the sort and sweep algorithm for broad phase
        # helpful reference: https://github.com/mattleibow/jitterphysics/wiki/Sweep-and-Prune
        axis_list = sorted(particles, key=lambda x: x.get_bb()[0])
        active_list = []
        possible_collisions = set()
        for particle in axis_list:
            to_remove = [p for p in active_list if particle.get_bb()[0] > p.get_bb()[1]]
            for r in to_remove:
                active_list.remove(r)
            for other_particle in active_list:
                possible_collisions.add((particle, other_particle))

            active_list.append(particle)
        
        return possible_collisions

def create_particles(n, frame_x1, frame_y1, frame_height, frame_width, max_radius, max_speed, min_speed, acc, surface):
    particles = []
    x = np.random.uniform(frame_x1 + 2 * max_radius, frame_x1 + frame_width - 2 * max_radius, n)
    y = np.random.uniform(frame_y1 + 2 * max_radius, frame_y1 + frame_height - 2 * max_radius, n)

    for i in range(n):
        vx = random.randint(min_speed, max_speed)
        vy = random.randint(min_speed, max_speed)
        color_r = random.randint(0, 255)
        color_g = random.randint(0, 255)
        color_b = random.randint(0, 255)
        radius = random.randint(5, max_radius)
        p = Particle(np.array([x[i], y[i]]), np.array([vx, vy]), np.array([0, acc]), (color_r, color_b, color_g), radius, surface, i)
        p.draw()
        particles.append(p)
    
    return particles
if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    # Create a 600x600 window
    window_width, window_height = 600, 600
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Collisions")
    # Define the rectangle's dimensions and position
    rect_width, rect_height = 580, 580
    thickness = 20
    x1 = window_width - rect_width
    y1 = window_height - rect_height
    # Main loop
    clock = pygame.time.Clock()
    dt = 0
    running = True
    f_bbox = [x1 + thickness, rect_width - thickness, y1 + thickness, rect_height - thickness]
    
    particles_array = create_particles(100, x1, y1, rect_height, rect_width, 20, 80, -80, 0, screen)
    p_coll = ParticleCollisions(SweepPrune())
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the window with white
        screen.fill((0, 0, 0))


        # Draw the blue rectangle
        rectangle = pygame.draw.polygon(screen, (0, 0, 255), [(x1,y1), (x1, rect_height), (rect_width, rect_height), (rect_width,y1)], thickness)
        for part in particles_array:
            part.draw()
        # Update the display
        pygame.display.flip()
        print(clock.tick(60))
        dt = clock.tick(60) / 1000
        p_coll.update_dynamics(particles_array, dt, f_bbox)
    # Quit Pygame
    pygame.quit()