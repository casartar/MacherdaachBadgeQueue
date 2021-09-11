import place


class Model(object):

    def __init__(self, numberOfPlaces):
        self.numberOfPlaces = numberOfPlaces
        self.list_of_labels_to_display_ticket_number = []
        self.list_of_labels_to_display_place_number = []
        self.list_of_labels_to_display_in_queue = []
        # list_of_ticket_numbers is only used if ticket number could not be registered to a place
        self.list_of_ticket_numbers = []
        self.list_of_processing_times = []
        self.list_of_places = []
        self.sorted_list_of_start_time = []
        self.initPlaces()

    def initPlaces(self):  # Initialize list_of_places
        for i in range(self.numberOfPlaces):
            self.list_of_places.append(place.Place())
