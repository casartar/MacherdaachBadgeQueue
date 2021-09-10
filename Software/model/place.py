class PlaceState():
    FREE = 1  # This place is not used and there is no ticket number to register
    REGISTERED = 2  # A ticket number was registered to this place but the owner has not started yet
    OCCUPIED = 3  # The owner of the ticket number has started


class RegistrationError(Exception):
    pass


class Place:
    def __init__(self, state=PlaceState.FREE, ticket_number=0, start_time=None):
        self.state = state
        self.ticket_number = ticket_number  # registered ticket number
        self.start_time = start_time

    def setstarttime(self, start_time):
        self.start_time = start_time

    def clear_place(self):

        self.state = PlaceState.FREE
        self.ticket_number = 0

    def set_place_state_to_reserved(self):
        self.state = PlaceState.REGISTERED

    def set_place_state_to_occupied(self):
        if self.state == PlaceState.FREE:
            self.state = PlaceState.OCCUPIED
        else:
            raise Exception('Can only occupy free place.')

    def register_ticket(self, ticket_number):
        if self.state != PlaceState.FREE:
            self.state = PlaceState.REGISTERED
            self.ticket_number = ticket_number
        else:
            raise RegistrationError('Can only register to free place')

    def is_free(self):
        if self.state == PlaceState.FREE:
            return True
        else:
            return False

    def set_ticket_number(self, ticket_number):
        self.ticket_number = ticket_number;
