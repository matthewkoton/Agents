class elevator():
    def __init__(self, environment):
        '''
        environment is dictionary of floors and whether or not they are requested {1: Flase, 2:True, 3:False} 
        note that we our agent can only tell if the current floor is requested
        current floor is the floor the elevator is currently on, the min floor is 0 and the max floor is the max found in the environment
        direction is the direction the elevator is currentltly moving 1 means up -1 means down
        '''
        self.environment = environment 
        self.curr_floor = 0  
        self.direction = 1    


    def get_percept(self):
        '''
        return if the current floor is requested and whether or not we at max or min floor
        '''
        if self.curr_floor == max(self.environment.keys()) and self.direction == 1:
            at_max_min = True
        elif self.curr_floor == 0 and self.direction == -1:
            at_max_min = True
        else:
            at_max_min = False
        if self.environment[self.curr_floor] == True:
            return True, at_max_min
        else:
            return False, at_max_min

    def move(self, at_max_min):
        if at_max_min:
            self.direction *= -1
            print("changing direction")
        print(f"moving {( 'up 1' if self.direction == +1 else 'down 1' )} floor")
        self.curr_floor += self.direction

    def act(self, percept):
        curr_floor_requested, at_max_min, = percept
        if curr_floor_requested == True:
            print(f"stopping on floor {self.curr_floor}")
            self.environment[self.curr_floor] = False
        self.move(at_max_min)

if __name__ == "__main__":
    environment = {0: False, 1: True, 2: False, 3: False, 4: True, 5: True, 6: False, 7: True}
    my_elevator = elevator(environment)
    for i in range(15):
        percepts = my_elevator.get_percept()
        my_elevator.act(percepts)
    
