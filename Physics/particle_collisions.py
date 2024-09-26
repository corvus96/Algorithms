import pygame

class Particle:
    def __init__(self, x, y, color, radius, surface) -> None:
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.surface = surface
    
    def draw(self):
        pygame.draw.circle(self.surface, self.color, (self.x, self.y), self.radius)

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
    running = True
    particle = Particle(200, 200, (255, 0, 0), 10, screen)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the window with white
        screen.fill((0, 0, 0))


        # Draw the blue rectangle
        pygame.draw.polygon(screen, (0, 0, 255), [(x1,y1), (x1, rect_height), (rect_width, rect_height), (rect_width,y1)], thickness)
        particle.draw()
        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()