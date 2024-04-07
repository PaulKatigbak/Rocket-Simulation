"""
Base Code: Faisal Qureshi
Alteration/Features and quality of life upgrades: Malhar Singh and Paul Gabriel Katigbak 
Rocket Simulation
April 6th 2024
"""

# importing other files
from rigidBody import RigidBody
from rocket import Rocket

# importing important packages
import pygame, sys
import matplotlib.pyplot as plt

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# function to display landing message
def display_end_screen(screen):
    font = pygame.font.SysFont(None, 50)
    text = font.render("Rocket landed successfully!", True, GREEN)
    text_rect = text.get_rect(center=(screen.get_width() // 2, (screen.get_height() // 2) - 100))
    screen.blit(text, text_rect)
    pygame.display.flip()

# function to display stats like velocity and distance
def display_stats(screen, rb):
    font = pygame.font.SysFont(None, 20)
    
    # setting up text values and positions
    if rb.get_pos()[0] != 0.0:
        velocity_textx = font.render(f'Velocity(x): {-1*(rb.state[12]/rb.mass):.2f}', True, GREEN)
        distance_textx = font.render(f'Distance(x): {-1*(rb.get_pos()[0]):.2f}', True, GREEN)
    else:
        distance_textx = font.render(f'Distance(x): {rb.get_pos()[0]:.2f}', True, GREEN)
        velocity_textx = font.render(f'Velocity(x): {rb.state[12]/rb.mass:.2f}', True, GREEN)
    
    velocity_texty = font.render(f'Velocity(y): {rb.state[13]/rb.mass:.2f}', True, GREEN)
    velocity_recty = velocity_texty.get_rect(center=(610, 70))

    distance_rectx = distance_textx.get_rect(center=(610, 90))
    velocity_rectx = velocity_textx.get_rect(center=(610, 50))

    distance_texty = font.render(f'Distance(y): {rb.get_pos()[1]:.2f}', True, GREEN)
    distance_recty = distance_texty.get_rect(center=(610, 110))
    
    # showing the text on screen
    screen.blit(velocity_textx, velocity_rectx)
    screen.blit(velocity_texty, velocity_recty)
    screen.blit(distance_textx, distance_rectx)
    screen.blit(distance_texty, distance_recty)

def main():
   # initializing pygame
    pygame.init()
    clock = pygame.time.Clock()

    # toggle button for air resistance
    air_resistance_button_rect = pygame.Rect(20, 20, 180, 40)
    air_resistance_button_color = GREEN
    air_resistance_button_text = 'Air Resistance: OFF'    # initially off

    # engine and crash sounds for rocket
    pygame.mixer.music.load('assets/sounds/engine_sound.mp3')  # using this as background music so its a smooth transition
    crash = pygame.mixer.Sound('assets/sounds/rocket_explosion.mp3')

    # setting up simulation window
    win_width = 700
    win_height = 800
    screen = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption('Rocket Simulation - Final Group Project')
    background = pygame.image.load('assets/images/background_long.png')

    # creating the rigid body (initially at rest and not rotating)
    rb = RigidBody([0,0,0], [0.0,0.0,0.0])

    # setting up rocket and explosion location
    rocket = Rocket(330, 320, win_height, 'assets/images/rocket.png', rb, 'assets/images/flame.png', scale_factor=0.3)
    rocket_exploded = Rocket(330, 320, win_height, 'assets/images/Mushroom_Cloud.png', rb, 'assets/images/flame.png', scale_factor=0.05)

    # initial time 0.0 and time step 
    cur_time = 0.0
    dt = 0.1

    rb.solver.set_initial_value(rb.state, cur_time)

    # to track explosion, sound (to play only once), and to display graph only once
    exploded = False
    crash_played = False
    graph_displayed = False

    # to plot values
    times = []
    velocitiesy = []
    distancesy = []

    while True:
        # 60 fps
        clock.tick(60)

        # to handle events by user (quit, pause, resume, left, up, right, button press)
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            pygame.quit()
            sys.exit(0)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            rb.pause()
            continue
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            rb.resume()
            continue
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            rb.thrust = True
            if not rb.left_thrust and not rb.right_thrust: 
                pygame.mixer.music.play(loops=-1)
        elif event.type == pygame.KEYUP and event.key == pygame.K_UP:
            rb.thrust = False
            if not rb.left_thrust and not rb.right_thrust: 
                pygame.mixer.music.stop()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            rb.left_thrust = True
            if rb.state[13] > 0:
                pygame.mixer.music.play(loops=-1)
        elif event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
            rb.left_thrust = False
            if not rb.thrust:  
                pygame.mixer.music.stop()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            rb.right_thrust = True
            if rb.state[13] > 0:
                pygame.mixer.music.play(loops=-1)
        elif event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
            rb.right_thrust = False
            if not rb.thrust:
                pygame.mixer.music.stop()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                
                # Check if the mouse click is inside the air resistance button
                if air_resistance_button_rect.collidepoint(event.pos):
                    
                    # Toggle air resistance on or off
                    rb.air_resistance = not rb.air_resistance
                    if rb.air_resistance:
                        air_resistance_button_text = 'Air Resistance: ON'
                    else:
                        air_resistance_button_text = 'Air Resistance: OFF'

        # to continue simulation
        if not exploded and not rb.paused:
            rb.state = rb.solver.integrate(cur_time)
            cur_time += dt

            # get position and angle
            angle, axis = rb.get_angle_2d()
            if axis[2] < 0:
                angle *= -1.
            pos = rb.get_pos()

            # for plotting
            times.append(cur_time)
            velocitiesy.append(rb.state[13]/rb.mass)
            distancesy.append(rb.state[1])

        # moves rocket to start from bottom of screen
        screen.blit(background, (pos[0] - 615, pos[1] - win_height - 1130))
        display_stats(screen, rb)        # had to draw this after background to avoid flickering

        # if (position(y) is <= 0 and velocity is > 2) or (position(y) is <= 0 and rocket is tilted too much) it will explode
        if (rb.state[1] <= 0 and abs(rb.state[13]/rb.mass) > 1.20) or ((rb.get_thrust_direction_body()[1]) <= 400 and rb.state[1] <= 0):
            exploded = True

            # to play crash sound only once
            if not crash_played:
                crash.set_volume(0.1)
                crash.play()
                crash_played = True

            rocket_exploded.draw(screen)
            rb.pause()
            # if not graph_displayed:

            #     # Plot velocity vs. time
            #     graph_displayed = True
            #     plt.figure(1)
            #     plt.plot(times, velocitiesy, color='blue')
            #     plt.xlabel('Time')
            #     plt.ylabel('Velocity (y)')
            #     plt.title('Velocity y-dir vs. Time')
            #     plt.grid(True)

            #     # Plot distance vs. time
            #     plt.figure(2)
            #     plt.plot(times, distancesy, color='red')
            #     plt.xlabel('Time')
            #     plt.ylabel('Distance (y)')
            #     plt.title('Distance y-dir vs. Time')
            #     plt.grid(True)
            #     plt.show()

        # if rocket hits the ground with not enough velocity, it will land and not explode
        elif rb.state[1] <= 0 and abs(rb.state[13]/rb.mass) < 1.20 and abs(rb.state[13]/rb.mass) != 0:
            rocket.draw(screen)
            display_end_screen(screen)
            rb.pause()
            # if not graph_displayed:
            #     # Plot velocity vs. time
            #     graph_displayed = True
            #     plt.figure(1)
            #     plt.plot(times, velocitiesy, color='blue')
            #     plt.xlabel('Time')
            #     plt.ylabel('Velocity')
            #     plt.title('Velocity vs. Time')
            #     plt.grid(True)

            #     # Plot distance vs. time
            #     plt.figure(2)
            #     plt.plot(times, distancesy, color='red')
            #     plt.xlabel('Time')
            #     plt.ylabel('Distance (y)')
            #     plt.title('Distance y-dir vs. Time')
            #     plt.grid(True)
            #     plt.show()
        else:
            rocket.rotate(angle)
            rocket.draw(screen)
        
        # Draw the air resistance button
        pygame.draw.rect(screen, air_resistance_button_color, air_resistance_button_rect)
        font = pygame.font.SysFont(None, 25)
        text_surface = font.render(air_resistance_button_text, True, BLACK)
        text_rect = text_surface.get_rect(center=air_resistance_button_rect.center)
        screen.blit(text_surface, text_rect)

        pygame.display.update()

if __name__ == '__main__':
    main()