import pygame, sys
from pygame.locals import *
from models.carbase import CarBase
from math import *
import csv


class DrawCar:
    def __init__(self, id: int) -> None:
        self.id = id
        self.x, self.y = 0,0

class Visualizer:
    def __init__(self, 
                window_width: int, 
                window_height: int, 
                track_length: float,
                lane_width: int,
                lane_count: int,
                collision_threshold: float
                ) -> None:
        pygame.init()

        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption('Traffic Visualizer')

        self.font = pygame.font.Font(None, 40)

        self.width = window_width
        self.height = window_height

        self.cars = []
        self.draw_cars = {}
        self.car_ids = []
        
        self.running = False
        self.window_active = True

        self.__i__ = 0

        self.clock = pygame.time.Clock()
        self.time_step = 0.01
        self.fps = 120
        self.fps_modifier = 12

        self.draw_scalar = window_width / track_length

        self.collision_threshold = collision_threshold

        self.track_length = track_length
        self.track_size = window_width
        self.lane_width = lane_width
        self.lane_count = lane_count

    def load(self, filename='data/run.csv'):
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for rownum, row in enumerate(reader):

                # Skip first row
                if rownum == 0:
                    continue

                # Get data from csv
                id = int(row[0])
                position = float(row[2])
                velocity = float(row[3])
                time = float(row[1])
                impatience = float(row[4])
                lane = int(row[5])


                # Make a new car if it doesn't exist
                if id not in self.car_ids:
                    self.car_ids.append(id)
                    self.cars.append(CarBase(id))
                    self.draw_cars[id] = DrawCar(id)

                # Add information to car
                self.cars[-1].pos.append(position)
                self.cars[-1].velocity.append(velocity)
                self.cars[-1].time.append(time)
                self.cars[-1].lanes.append(lane)
                self.cars[-1].impatience.append(impatience)

        # Set time step and fps so it scales appropriately with simulation data
        self.time_step = self.cars[-1].time[-1] - self.cars[-1].time[-2]
        self.fps = int(3 / self.time_step) # 3 to make it a bit sped up
        self.fps_modifier = int(self.fps / 10)

    def update_cars(self):
        # Keep parsing simulation data if we're running
        if self.running:
            self.__i__ += 1

        if self.__i__ >= self.max_time_index:
            self.running = False
            self.__i__ = 0
            return

        for c in self.cars:
            # Update position of each drawcar
            lane_start_y = int((self.height / 2) - (self.lane_width * self.lane_count / 2))
            draw_car = self.draw_cars[c.id]
            draw_car.x = int(c.pos[self.__i__] * self.draw_scalar)
            draw_car.y = int(c.lanes[self.__i__] * self.lane_width) + lane_start_y

    # ModelDriver loop
    def run(self) -> None:

        self.max_time_index = min([len(c.time) for c in self.cars])


        while self.window_active:

            # if self.__i__ >= max_time_index:
            #     self.__i__ = 0
            #     self.running = False

            # Limit frame rate
            self.clock.tick(self.fps)

            # Parse events
            for event in pygame.event.get():

                # Quit event
                if event.type == pygame.QUIT:
                    self.window_active = False

                # Key events
                if event.type == KEYDOWN:
                    # Quit
                    if event.key == K_ESCAPE:
                        self.window_active = False

                    # Increase FPS
                    elif event.key == K_UP:
                        self.fps += self.fps_modifier

                    # Decrease FPS
                    elif event.key == K_DOWN:
                        self.fps -= self.fps_modifier
                        if self.fps < self.fps_modifier:
                            self.fps = self.fps_modifier
                    # Pause
                    else:
                        self.running = not self.running

            # Update car positions if the visualization is running
            if self.running:
                self.update_cars()

            # Call draw method
            self.draw()
        
        # Exit once we've left the main loop
        self.exit()

    def draw(self) -> None:
        # Fill background
        self.screen.fill((127,127,127))

        # Draw the lanes
        lane_start_y = int((self.height / 2) - (self.lane_width * self.lane_count / 2))
        for i in range(self.lane_count):
            lane_y = lane_start_y + (i * self.lane_width)
            pygame.draw.line(self.screen, (255, 255, 255), (0, lane_y), (self.width, lane_y), 2)

        # Draw the time parameter
        t = round(self.cars[0].time[self.__i__], 2)
        t_str = "{:.2f}".format(t)
        time_text = self.font.render("t=" + t_str, True, (255, 255, 255))
        time_text_rect = time_text.get_rect(topleft=(50, 50))
        self.screen.blit(time_text, time_text_rect)

        # Draw fps
        fps_text = self.font.render("FPS: " + str(self.fps), True, (255, 255, 255))
        fps_text_rect = fps_text.get_rect(topleft=(50, 100))
        self.screen.blit(fps_text, fps_text_rect)

        # Draw cars
        for c in self.cars:
            draw_car = self.draw_cars[c.id]
            color = (min(int(c.impatience[self.__i__] * 3 * 255), 255), 0, 0)
            pygame.draw.rect(self.screen, 
                                color, 
                                (
                                    draw_car.x, draw_car.y, 
                                    int(self.collision_threshold * self.draw_scalar), int(0.25 * self.lane_width * self.draw_scalar), 
                                )
                            )
            # Draw car id in the circle
            id_text = self.font.render(str(c.id), True, color)
            id_text_rect = id_text.get_rect(center=(draw_car.x, draw_car.y))
            self.screen.blit(id_text, id_text_rect)

        # Update screen
        pygame.display.flip()

    # Exit the program
    def exit(self) -> None:
        pygame.quit()
        sys.exit()