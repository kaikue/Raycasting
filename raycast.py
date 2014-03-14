'''
Created on Apr 26, 2013

@author: Kai
'''
import pygame, os, sys, math

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0, 255)
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
TRANSPARENT = (255, 0, 255)

def quadrant(angle):
    while angle < 0:
        angle += 2 * math.pi
    while angle > 2 * math.pi:
        angle -= 2 * math.pi
    
    if 0 <= angle <= math.pi / 2:
        return 4
    if math.pi / 2 <= angle <= math.pi:
        return 3
    if math.pi <= angle <= math.pi * 3 / 2:
        return 2
    if math.pi * 3 / 2 <= angle <= math.pi * 2:
        return 1

def origin_quadrant(origin, point):
    if origin[0] <= point[0] and origin[1] <= point[1]:
        return 4
    if origin[0] >= point[0] and origin[1] <= point[1]:
        return 3
    if origin[0] >= point[0] and origin[1] >= point[1]:
        return 2
    if origin[0] <= point[0] and origin[1] >= point[1]:
        return 1

class Game:
    def __init__(self):
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))#.convert_alpha()
        pygame.display.set_caption("Hello Pygame")
        self.clock = pygame.time.Clock()
        self.horiz_scale = SCREEN_WIDTH / 5
        self.vert_scale = SCREEN_HEIGHT / 5
        self.world = [[1, 0, 0, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0]]
        self.build_lines()
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = SCREEN_HEIGHT / 2
        self.end_x = self.end_y = None
    
    def build_lines(self):
        self.lines = []
        self.lines.append(Line((0, 0), (SCREEN_WIDTH, 0)))
        self.lines.append(Line((0, 0), (0, SCREEN_HEIGHT)))
        self.lines.append(Line((SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT)))
        self.lines.append(Line((0, SCREEN_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT)))
        for y in range(len(self.world)):
            for x in range(len(self.world[y])):
                if self.world[y][x] == 1:
                    self.lines.append(Line((x * self.horiz_scale, y * self.vert_scale), ((x+1) * self.horiz_scale, y * self.vert_scale)))
                    self.lines.append(Line((x * self.horiz_scale, y * self.vert_scale), (x * self.horiz_scale, (y+1) * self.vert_scale)))
                    self.lines.append(Line((x * self.horiz_scale, (y+1) * self.vert_scale), ((x+1) * self.horiz_scale, (y+1) * self.vert_scale)))
                    self.lines.append(Line(((x+1) * self.horiz_scale, y * self.vert_scale), ((x+1) * self.horiz_scale, (y+1) * self.vert_scale)))
        for line in self.lines:
            print(line)
    
    def run(self):
        while True:
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                sys.exit(0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
            self.clock.tick()
            self.update()
            self.render()
            pygame.time.wait(1)
    
    def update(self):
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.center_x -= 5
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.center_x += 5
        if pygame.key.get_pressed()[pygame.K_UP]:
            self.center_y -= 5
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            self.center_y += 5
        #make list of vertices
        #loop around vertices in a circle
        #ignore vertex, raycast past it- first raycast? (need to pass corners)
        #draw triangle between previous point and that one
        #raycast to that vertex, or maybe that one should be first
        self.tris = []
        angle = 0
        start_pos = (self.center_x, self.center_y)
        prev_pos = (self.center_x, self.center_y)
        while angle <= 2 * math.pi:
            min_distance = -1
            for line in self.lines:
                #mouse_end = (mouse_x, mouse_y)
                #mouse_angle = math.atan2(mouse_y - self.center_y, mouse_x - self.center_x)
                intersection = self.intersection(Ray(start_pos, angle), line)
                if intersection is not None:
                    #find shortest one
                    this_distance = ((self.center_x - intersection[0]) ** 2 + (self.center_y - intersection[1]) ** 2) ** 0.5
                    if min_distance < 0 or this_distance < min_distance:
                        min_distance = this_distance
                        end_pos = intersection
            self.tris.append((start_pos, prev_pos, end_pos))
            prev_pos = end_pos
            angle += math.pi / 96
        #find tiles between mouse and center
        #http://lifc.univ-fcomte.fr/~dedu/projects/bresenham/index.html
        #http://www.redblobgames.com/articles/visibility/
        self.render()
    
    def intersection(self, mouse_ray, wall_line):
        m1 = mouse_ray.slope
        m2 = wall_line.slope
        b1 = mouse_ray.intercept
        b2 = wall_line.intercept
        
        if m1 == m2:
            return None
        if m2 == None:
            x = wall_line.start_pos[0]
            y = m1 * x + b1
        elif m1 == None:
            x = mouse_ray.start_pos[0]
            y = m2 * x + b2
        else:
            x = (b2 - b1) / (m1 - m2)
            y = m1 * x + b1
        #make sure mouse is pointing towards intersection: mouse_x between center_x and x
        if wall_line.start_pos[0] <= x <= wall_line.end_pos[0] and \
            wall_line.start_pos[1] <= y <= wall_line.end_pos[1] and \
            quadrant(mouse_ray.angle) == origin_quadrant((self.center_x, self.center_y), (x, y)):
            #and \
            #((self.center_x < mouse_line.end_pos[0] and self.center_x < x) or (self.center_x > mouse_line.end_pos[0] and self.center_x > x)) and \
            #((self.center_y < mouse_line.end_pos[1] and self.center_y < y) or (self.center_y > mouse_line.end_pos[1] and self.center_y > y))
            #print("WALLSTART: " + str(wall_line.start_pos), " END: " + str(wall_line.end_pos), x, y)
            #((0 <= mouse_ray.angle <= math.pi / 2 and x > self.center_x and y < self.center_y) or \
            # (math.pi / 2 <= mouse_ray.angle <= math.pi and x < self.center_x and y < self.center_y) or \
            # (math.pi <= mouse_ray.angle <= math.pi * 3 / 2 and x < self.center_x and y > self.center_y) or \
            # (math.pi * 3 / 2 <= mouse_ray.angle <= math.pi * 2 and x > self.center_x and y > self.center_y)):
            return (x, y)
        #print("none: out of bounds", quadrant(mouse_ray.angle), origin_quadrant((self.center_x, self.center_y), (x, y)))
        return None
    
    def render(self):
        self.screen.fill(WHITE)
        for y in range(len(self.world)):
            for x in range(len(self.world[y])):
                if self.world[y][x] == 1:
                    pygame.draw.rect(self.screen, BLACK, (x * self.horiz_scale, y * self.vert_scale, self.horiz_scale, self.vert_scale))
        #if self.end_x is not None and self.end_y is not None:
            #pygame.draw.line(self.screen, BLUE, (self.center_x, self.center_y), (self.end_x, self.end_y))
        for tri in self.tris:
            #if random.random() > 0.75:
            pygame.draw.polygon(self.screen, BLUE, tri)
        #print(self.clock.get_fps())
        pygame.display.update()

class Line(object):
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos
        if self.start_pos[0] == self.end_pos[0]:
            self.slope = None
            self.intercept = None
        else:
            self.slope = (self.end_pos[1] - self.start_pos[1]) / (self.end_pos[0] - self.start_pos[0])
            self.intercept = -self.start_pos[0] * self.slope + self.start_pos[1]
    
    def __str__(self):
        return "Line at " + str(self.start_pos) + " to " + str(self.end_pos) + " with slope = " + str(self.slope)

class Ray(object):
    def __init__(self, start_pos, angle):
        self.start_pos = start_pos
        self.angle = angle
        if (self.angle / (math.pi / 2)) % 2 == 1:
            self.slope = None
            self.intercept = None
        else:
            self.slope = math.tan(self.angle)
            self.intercept = -self.start_pos[0] * self.slope + self.start_pos[1]
    
    def __str__(self):
        return "Ray at " + str(self.start_pos) + " with angle = " + str(self.angle)

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()