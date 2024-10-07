import pygame
import numpy as np

class Particle:
    def __init__(self, pos, vel, acc ,color, radius, surface) -> None:
        self.pos = pos 
        self.vel = vel 
        self.acc = acc
        self.color = color
        self.radius = radius
        self.surface = surface
        self.mass = np.pi * self.radius**2

    def draw(self):
        pygame.draw.circle(self.surface, self.color, (self.pos[0], self.pos[1]), self.radius)
    
    def update(self, dt):
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
    def euler_distance(self, p):
        return np.sqrt((p[0].x[0] - p[1].x[0])**2 + (p[0].y[0] - p[1].y[0])**2)
    def update_particle(self, p, dt, f_bbox):
        p.update(dt)
        bbox = p.get_bb()
        self.handle_frame_collision(p, bbox, f_bbox)
    
    def handle_frame_collision(self, particle, p_bbox, f_bbox):
        if p_bbox[0] <= f_bbox[0] or p_bbox[1] >= f_bbox[1]:
            particle.vel[0] = - particle.vel[0]
        if p_bbox[2] <= f_bbox[2] or p_bbox[3] >= f_bbox[3]:
            particle.vel[1] = - particle.vel[1]

    def update_dynamics(self, particles, dt, frame):
        '''particles is list of objects where each element is a Particle instance,
        pairs_p is a list of lists with the following shape [[x1, y1, radius, mass, v1]]'''
        ps = self._stragegy.handle_collisions(particles)
        for i in range(len(ps)): 
            self.update_particle(ps[i], dt, frame)
        # if self.euler_distance(pairs_p) * 0.98 <= particles[0].radius + particles[1].radius:
        #     sum_mass = particles[0].mass + particles[1].mass
        #     diff_mass = particles[0].mass - particles[1].mass
        #     particles[0].x[1] = ((diff_mass) * particles[0].x[1] + 2 * particles[1].mass * particles[1].x[1]) / sum_mass
        #     particles[0].y[1] = ((diff_mass) * particles[0].y[1] + 2 * particles[1].mass * particles[1].y[1]) / sum_mass
        #     particles[1].x[1] = (-(diff_mass) * particles[1].x[1] + 2 * particles[0].mass * particles[0].x[1]) / sum_mass
        #     particles[1].y[1] = (-(diff_mass) * particles[1].y[1] + 2 * particles[0].mass * particles[0].y[1]) / sum_mass

class SweepPrune(CollisionMethod):
    def handle_collisions(self, data):
        return data

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
    particle = Particle(np.array([410, 200]), np.array([-20, 0]), np.array([0, 5]), (255, 0, 0), 40, screen)
    particle2 = Particle(np.array([400, 200]), np.array([20, 0]), np.array([0, 5]), (0, 0, 255), 40, screen)
    particle.draw()
    particle2.draw()
    particles_array = [particle, particle2]
    p_coll = ParticleCollisions(SweepPrune())
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the window with white
        screen.fill((0, 0, 0))


        # Draw the blue rectangle
        rectangle = pygame.draw.polygon(screen, (0, 0, 255), [(x1,y1), (x1, rect_height), (rect_width, rect_height), (rect_width,y1)], thickness)
        particle.draw()
        particle2.draw()
        # Update the display
        pygame.display.flip()
        dt = clock.tick(60) / 200
        p_coll.update_dynamics(particles_array, dt, f_bbox)
    # Quit Pygame
    pygame.quit()