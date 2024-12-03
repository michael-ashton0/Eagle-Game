import random
import math
from datetime import datetime
import turtle

class Resource:
    def __init__(self, x, y, energy, duration, active=True):
        self.x = x
        self.y = y
        self.energy = energy
        self.duration = duration
        self.active = True
        
        # Visual Resource representation
        self.visual_resource = turtle.Turtle()
        self.visual_resource.penup()
        self.visual_resource.hideturtle()

        self.visual_resource.goto((x * 3), (y * 3) - 5)  # Scale positions
        self.visual_resource.pendown()
        self.visual_resource.circle(10)

    def update_position(self):
        '''Update the visual position of the resource on the screen.'''
        self.visual_resource.goto(self.x * 3, self.y * 3)  # Scale positions

    def hide_resource(self):
        '''Create a cover-up resource that hides the old resource.'''
        cover_up = turtle.Turtle()
        cover_up.hideturtle()
        cover_up.penup()
        cover_up.goto(self.x * 3, (self.y * 3) - 5)
        cover_up.pendown()
        cover_up.color("skyblue")  # Match background color
        cover_up.begin_fill()
        cover_up.circle(10)
        cover_up.end_fill()


class Territory:
    def __init__(self, length=100, width=100):
        self.length = length
        self.width = width
        self.resources = []

    def spawn_resource(self):
        '''1/4 chance to create a resource each turn at a random x, y with a random energy and duration'''
        if random.random() < 0.25:
            x = random.randint(-self.length, self.length)
            y = random.randint(-self.width, self.width)
            energy = random.randint(1, 10)
            duration = random.randint(1, 3)
            resource = Resource(x, y, energy, duration)
            self.resources.append(resource)
            print(f'Resource appeared at ({x}, {y}) with {energy} energy for {duration} rounds.')

    def update_resources(self):
        '''Updates resources, decreasing their duration and deactivating them if expired'''
        for resource in self.resources:
            if resource.active:
                resource.duration -= 1
                if resource.duration <= 0:
                    resource.active = False
                    resource.hide_resource()

class Eagle:
    def __init__(self, name, energy=250):
        self.name = name
        self.energy = energy
        self.x = 0
        self.y = 0
        self.total_distance = 0
        self.total_time = 0
        self.score = 0

        # Setting up the GUI
        self.turtle = turtle.Turtle()
        self.turtle.shape("circle")
        self.turtle.color("goldenrod")
        self.turtle.penup()
        self.turtle.goto(self.x * 3, self.y * 3)  # Scale position of eagle to match resources
        self.turtle.pendown()

    def consume_resource(self, resource):
        '''Consumes an active resource if the eagle lands on it'''
        if (self.x, self.y) == (resource.x, resource.y) and resource.active:
            self.energy += resource.energy
            resource.active = False
            resource.hide_resource()
            print(f'{self.name} consumed resource at ({resource.x}, {resource.y}) and gained {resource.energy} energy.')

    def fly_to(self, x, y, speed=1):
        '''Fly the eagle to a given x and y coordinate at a given speed'''
        distance = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2) # Finding the direct distance the eagle traveled for scoring
        time = distance / speed
        energy_burn = distance / 10 * speed

        # Scaling to better fit a larger turtle window size while maintaining the functionality of the 100x100 board
        screen_x = x * 3
        screen_y = y * 3 

        self.x, self.y = x, y
        self.energy -= energy_burn
        self.total_distance += distance
        self.total_time += time
        self.score += distance

        print(f'{self.name} flew {distance:.2f} units to ({x}, {y}) at speed {speed}. Energy left: {self.energy:.2f}')
        self.turtle.goto(screen_x, screen_y)

        return True

    def rest(self, hours):
        '''The eagle rests, regaining energy per hour rested'''
        if 1 <= hours <= 10:
            self.energy += hours
            self.total_time += hours
            print(f'{self.name} rested for {hours} hours. Energy now: {self.energy}')
        else:
            print('Resting hours should be between 1 and 10.')

    def report_status(self, day):
        '''Displays the eagle's current status'''
        print(f'Day {day}: Distance: {self.total_distance:.2f}, Time: {self.total_time:.2f}, Energy: {self.energy:.2f}')

    def is_alive(self):
        '''Checks if the eagle has energy left to continue'''
        return self.energy > 0

    def save_score(self):
        '''Saves the score to the file in sorted order by score'''
        date = datetime.now().strftime('%Y-%m-%d')
        new_score = f'{self.score:.2f}, {date}, Eagle: {self.name}, Distance: {self.total_distance:.2f}, Energy: {self.energy:.2f}\n'

        try:
            with open('eaglescores.txt', 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        lines.append(new_score)

        lines.sort(key=lambda line: float(line.split(',')[0]), reverse=True)

        with open('eaglescores.txt', 'w') as f:
            f.writelines(lines)

        print('Score saved!')

def draw_territory_box():
    '''Draw a boundary box for the territory area'''
    border = turtle.Turtle()
    border.speed(0)
    border.penup()
    border.goto(-300, 300)
    border.pendown()
    border.color("black")

    border.begin_fill()
    border.fillcolor("skyblue")

    for _ in range(2):
        border.forward(600)
        border.right(90)
        border.forward(600)
        border.right(90)

    border.end_fill()
    border.hideturtle()

def play_game():
    # Create GUI
    screen = turtle.Screen()
    screen.setup(width=700, height=700)
    screen.bgcolor("gray")
    screen.title("Eagle Simulation")
    draw_territory_box()

    print('Welcome to the Game! What would you like to name your eagle?')
    name = input().strip()
    eagle = Eagle(name)
    territory = Territory()

    print('****All inputs are case insensitive!****')

    for day in range(1, 27):
        if day == 26:
            print(f'Congratulations! You win with a score of {eagle.score:.2f}. Great job!')
            eagle.save_score()
            break

        print(f'\nDay {day}\n ---------------------------------------------------------')

        territory.spawn_resource()

        active_resources = [resource for resource in territory.resources if resource.active]  # List of currently available resources
        if active_resources:
            print('Available resources:')
            for resource in active_resources:
                print(f'  - Location: ({resource.x}, {resource.y}), Energy: {resource.energy}, Rounds left: {resource.duration}')

        action = input('Choose action: Fly or Rest\n').lower()
        if action not in ('fly', 'rest'):
            print('Invalid action! Choose from: fly or rest')
            continue

        if action == 'fly':
            destination = input('Where would you like to fly? Format input as x y speed\n').split()
            try:
                x, y, speed = map(int, destination)
                x = max(min(x, 100), -100)
                y = max(min(y, 100), -100)
                if eagle.fly_to(x, y, speed):
                    for resource in active_resources:
                        eagle.consume_resource(resource)
            except ValueError:
                print('Invalid input format. Please enter x, y, and speed as integers.')

        elif action == 'rest':
            try:
                hours = int(input('Enter the number of hours to rest (1-10): '))
                eagle.rest(hours)
            except ValueError:
                print('Invalid input. Please enter a valid number of hours.')

        eagle.report_status(day)
        if not eagle.is_alive():
            print(f'{eagle.name} has exhausted all energy and the game is over. Final score: {eagle.score:.2f}')
            eagle.save_score()
            break

        territory.update_resources()

        print(f'Current score: {eagle.score:.2f}')

play_game()
