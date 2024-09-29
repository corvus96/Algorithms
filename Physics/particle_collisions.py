import pygame

class Particle:
    def __init__(self, x: list, y: list, color, radius, surface, bbox) -> None:
        self.x = x # [p_xo, v_xo, a_xo]
        self.y = y # [p_yo, v_yo, a_yo]
        self.color = color
        self.radius = radius
        self.surface = surface
        self.bbox = bbox # [left, right, up, down]
    def draw(self):
        pygame.draw.circle(self.surface, self.color, (self.x[0], self.y[0]), self.radius)
    
    def update(self, dt):
        #self.x[1] = self.x[1] + self.x[2] * dt
        self.x[0] = self.x[0] + self.x[1] * dt
        self.y[1] = self.y[1] + self.y[2] * dt
        self.y[0] = self.y[0] + self.y[1] * dt
        self.handle_box_collision()

    def handle_box_collision(self):
        b_particle = [self.x[0] - self.radius, 
                      self.x[0] + self.radius, 
                      self.y[0] - self.radius,
                      self.y[0] + self.radius] # [left, right, up, down]
        if b_particle[0] <= self.bbox[0] or b_particle[1] >= self.bbox[1]:
            self.x[1] = - self.x[1]
        if b_particle[2] <= self.bbox[2] or b_particle[3] >= self.bbox[3]:
            self.y[1] = - self.y[1]

if __name__ == "__main__":
    # Initialize Pygame
    pygame.init()
    # Create a 600x600 window
    window_width, window_height = 600, 600
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Collisions")
    # Define the rectangle's dimensions and position
    rect_width, rect_height = 580, 580
    thickness = 2
    x1 = window_width - rect_width
    y1 = window_height - rect_height
    # Main loop
    clock = pygame.time.Clock()
    dt = 0
    running = True
    bbox = [x1 + thickness, rect_width - thickness, y1 + thickness, rect_height - thickness]
    particle = Particle([200, -20, 0], [200, 43, 9.81], (255, 0, 0), 10, screen, bbox)
    particle.draw()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the window with white
        screen.fill((0, 0, 0))


        # Draw the blue rectangle
        rectangle = pygame.draw.polygon(screen, (0, 0, 255), [(x1,y1), (x1, rect_height), (rect_width, rect_height), (rect_width,y1)], thickness)
        particle.draw()
        # Update the display
        pygame.display.flip()
        dt = clock.tick(60) / 200
        particle.update(dt)
    # Quit Pygame
    pygame.quit()