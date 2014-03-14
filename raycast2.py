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
        self.build_vertices()
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
    
    def build_vertices(self):
        self.vertices = []
        for line in self.lines:
            for vertex in (line.start_pos, line.end_pos):
                if vertex not in self.vertices:
                    self.vertices.append(vertex)
    
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
        start_pos = (self.center_x, self.center_y)
        
        self.intersections = []
        angles = []
        for vertex in self.vertices:
            #set vertex's angle to angle
            angle = math.atan2(vertex[1] - self.center_y, vertex[0] - self.center_x)
            angles.append(angle - 0.00001)
            angles.append(angle)
            angles.append(angle + 0.00001)
        
        for angle in angles:
            closest_intersection = None
            for line in self.lines:
                dx = math.cos(angle)
                dy = math.sin(angle)
                intersection = self.intersection(Line(start_pos, (self.center_x + dx, self.center_y + dy)), line, angle)
                if intersection is not None:
                    if closest_intersection is None or intersection.distance < closest_intersection.distance:
                        closest_intersection = intersection
            self.intersections.append(closest_intersection)
        self.intersections.sort(key=lambda k: k.angle)
        for i in self.intersections:
            print(i, end=" ")
        print()
        self.render()
    
    def intersection(self, ray, segment, angle):
        ray_px = ray.start_pos[0]
        ray_py = ray.start_pos[1]
        ray_dx = ray.end_pos[0] - ray_px
        ray_dy = ray.end_pos[1] - ray_py
        
        seg_px = segment.start_pos[0]
        seg_py = segment.start_pos[1]
        seg_dx = segment.end_pos[0] - seg_px
        seg_dy = segment.end_pos[1] - seg_py
        
        ray_mag = (ray_dx ** 2 + ray_dy ** 2) ** 0.5
        seg_mag = (seg_dx ** 2 + seg_dy ** 2) ** 0.5
        if ray_dx / ray_mag == seg_dx / seg_mag and ray_dy / ray_mag == seg_dy / seg_mag:
            return None
        
        T2 = (ray_dx * (seg_py - ray_py) + ray_dy * (ray_px - seg_px)) / (seg_dx * ray_dy - seg_dy * ray_dx)
        T1 = (seg_px + seg_dx * T2 - ray_px) / ray_dx
        
        if T1 < 0:
            return None
        if T2 < 0 or T2 > 1:
            return None
        
        return Intersection(ray_px + ray_dx * T1, ray_py + ray_dy * T1, T1, angle)
    
    def render(self):
        self.screen.fill(WHITE)
        for y in range(len(self.world)):
            for x in range(len(self.world[y])):
                if self.world[y][x] == 1:
                    pygame.draw.rect(self.screen, BLACK, (x * self.horiz_scale, y * self.vert_scale, self.horiz_scale, self.vert_scale))
        prev = self.intersections[0]
        for nxt in self.intersections:
            pygame.draw.polygon(self.screen, BLUE, ((self.center_x, self.center_y), (prev.x, prev.y), (nxt.x, nxt.y)))
            prev = nxt
        nxt = self.intersections[0]
        pygame.draw.polygon(self.screen, BLUE, ((self.center_x, self.center_y), (prev.x, prev.y), (nxt.x, nxt.y)))
        pygame.display.update()

class Line(object):
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos

class Intersection(object):
    def __init__(self, x, y, distance, angle):
        self.x = x
        self.y = y
        self.distance = distance
        self.angle = angle
    
    def __str__(self):
        return str(self.angle)

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()