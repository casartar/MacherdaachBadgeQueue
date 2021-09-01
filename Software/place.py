class PlaceState():
    FREE = 1  # This place is not used and there is no ticket number to register
    REGISTERED = 2  # A ticket number was registered to this place but the owner has not started yet
    OCCUPIED = 3  # The owner of the ticket number has started


class RegistrationError:
    pass


class Place:
    def __init__(self, state=PlaceState.FREE, ticket_number=0, start_time=None):
        self.state = state
        self.ticket_number = ticket_number  # registered ticket number
        self.start_time = start_time

    def setstarttime (self, start_time):
        self.start_time = start_time

    def clearplace(self):

        self.state = PlaceState.FREE
        self.ticket_number = 0

    def occupyPlace(self):
        # Todo: occupy only possible, when place has status registered and user has same ticket number as reservation
        self.state = PlaceState.OCCUPIED

    def registerTicket(self, ticketNumber):
        if (self.state != PlaceState.FREE):
            self.state = PlaceState.REGISTERED
            self.ticket_number = ticketNumber
        else:
            raise RegistrationError('Can only register to free place')
