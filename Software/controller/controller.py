from libs.paho.mqtt import client as mqtt_client
import random
import json
from datetime import datetime
import statistics
from config import broker, username, password
from model.model import Model
from model.place import PlaceState
from view.view import View

port = 1883
topic_from_place = "macherdaach/queue/messageFromPlace"
topic_from_controller = "macherdaach/queue/messageFromController"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

numberOfPlaces = 8


class Controller(object):
    def __init__(self):

        self.client = self.connect_mqtt()
        self.model = Model(numberOfPlaces)
        self.view = View(numberOfPlaces)
        self.view.initView(self.model.list_of_labels_to_display_ticket_number,
                           self.model.list_of_labels_to_display_place_number,
                           self.model.list_of_labels_to_display_in_queue)

    def startup_controller(self):

        self.subscribe(self.client)
        self.client.loop_start()
        self.view.window.after(0, self.update_processing_time)
        self.view.window.mainloop()

    def update_queue(self, list_of_processing_times, list_of_labels_to_display_in_queue, list_of_ticket_numbers):
        print("Update Queue")

        self.model.sorted_list_of_start_time = sorted(
            self.model.list_of_places, key=lambda x: x.start_time or datetime.now(tz=None))
        for i in self.model.list_of_places:
            print(i.start_time)
        for i in self.model.sorted_list_of_start_time:
            print(i.start_time)
        try:
            median_processing_time = statistics.median(list_of_processing_times)
        except:
            median_processing_time = 0
        print("Median processing time: " + str(median_processing_time))
        print("Now: " + str(datetime.now(tz=None)))

        for count, element in enumerate(list_of_labels_to_display_in_queue):
            print("Count " + str(count))
            if count < len(self.model.list_of_ticket_numbers):
                print("Count " + str(count) + " < " +
                      "len(ticket_numbers): " + str(len(list_of_ticket_numbers)))
                print("Number " + str(list_of_ticket_numbers[count]))
                print(str(datetime.now(tz=None)) + " - " +
                      str(self.model.sorted_list_of_start_time[count].start_time))
                try:
                    current_processing_time = datetime.now(
                        tz=None) - self.model.sorted_list_of_start_time[count].start_time
                except:
                    current_processing_time = 0
                print("time difference: " + str(current_processing_time))
                if (median_processing_time == 0 or current_processing_time == 0):
                    element.config(
                        text=str(list_of_ticket_numbers[count]) + "(???)")
                else:
                    estimated_processing_time = median_processing_time - current_processing_time
                    element.config(text=str(list_of_ticket_numbers[count]) + "(" + str(
                        int(estimated_processing_time.total_seconds() / 60)) + " min)")
            else:
                element.config(text="--")

    def update_processing_time(self):
        self.view.window.after(60000, self.update_processing_time)
        self.update_queue(self.model.list_of_processing_times, self.model.list_of_labels_to_display_in_queue,
                          self.model.list_of_ticket_numbers)

    def subscribe(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from {msg.topic}` topic")
            try:
                mqtt_decoded = str(msg.payload.decode("utf-8", "ignore"))
                json_loaded = json.loads(mqtt_decoded)
                if msg.topic == topic_from_place:
                    self.handle_message_from_place(json_loaded)
                elif msg.topic == topic_from_controller:
                    self.handle_message_from_controller(json_loaded)
            except Exception as e:
                print(str(e))
                print("Something went wrong on mqtt reception")
            self.update_queue(self.model.list_of_processing_times, self.model.list_of_labels_to_display_in_queue,
                              self.model.list_of_ticket_numbers)

        client.subscribe(topic_from_place)
        client.subscribe(topic_from_controller)
        client.on_message = on_message

    def handle_message_from_controller(self, json_loaded):
        new_number = json_loaded["new_number"]
        print("Received new ticket number from controller: " +
              str(new_number))
        if new_number < 0:
            raise Exception('New ticket number must be positive!')
        # Check if new number is already in use
        for placeInList in self.model.list_of_places:
            if placeInList.ticket_number == new_number:
                raise Exception("New number " + str(new_number) +
                      " already registered")
                return
        if new_number in self.model.list_of_ticket_numbers:
            print("New number " + str(new_number) +
                  "already in ticket number list")
            return
        for count, placeInList in enumerate(self.model.list_of_places):
            # Search an empty place
            if placeInList.is_free():
                # Found one - register ticket number to place
                print("Register ticket: " +
                      str(new_number) + " to free place " + str(count + 1))
                self.reservePlaceForTicketNumber(count, new_number)
                break
            if placeInList == self.model.list_of_places[-1]:
                # Found no vacant place - put number in queue
                print("New number " + str(new_number))
                self.model.list_of_ticket_numbers.append(new_number)

    def handle_message_from_place(self, json_loaded):
        if type(json_loaded["place_occupied"]) != bool:
            raise Exception('Key "place_occupied" is of wrong type! Must be boolean!')
        # Place number in MQTT-Message starts with 1 and must be decremented
        place_number = json_loaded["place_number"] - 1
        if place_number > numberOfPlaces or place_number < 0:
            raise Exception('Received place_number ' + str(place_number) + ' refers to not existing place!')
        if json_loaded["place_occupied"] == True:
            # Place was taken by the owner of the ticket_number
            if self.model.list_of_places[place_number].state == PlaceState.REGISTERED:
                self.occupyPlace(place_number)
            else:
                raise Exception("Not occupied - there is no ticket registered to this place")
        if json_loaded["place_occupied"] == False:
            # Place was given up by owner
            print("Released: " +
                  str(json_loaded["place_number"]))
            if self.model.list_of_places[place_number].state != PlaceState.OCCUPIED:
                raise Exception("Not occupied - there is no ticket registered to this place")
            else:
                processing_time = datetime.now(
                    tz=None) - self.model.list_of_places[place_number].start_time
                self.model.list_of_places[place_number].clear_place()
                self.model.list_of_labels_to_display_place_number[place_number].config(bg="green")
                self.model.list_of_labels_to_display_ticket_number[place_number].config(
                    text="Frei")
                # Save processing time in
                print("Processing time: " + str(processing_time))
                self.model.list_of_processing_times.append(processing_time)
                # Search for a new number in list_of_ticket_numbers to be registered to the released place
                if self.model.list_of_ticket_numbers:
                    # ticket list is not empty - register number from ticket list to place
                    # Take first element of list_of_ticket_numbers and register the number to the current place and display it
                    ticket_number = self.model.list_of_ticket_numbers.pop(0)
                    self.reservePlaceForTicketNumber(place_number, ticket_number)

    def occupyPlace(self, place_number):
        self.model.list_of_places[place_number].set_place_state_to_occupied()
        self.model.list_of_labels_to_display_place_number[place_number].config(
            bg="red")
        self.model.list_of_labels_to_display_ticket_number[place_number].config(
            text="Belegt")
        self.model.list_of_places[place_number].setstarttime(datetime.now(
            tz=None))
        print("Occupied: " + str(place_number))
        return self.model.list_of_places[place_number]

    def reservePlaceForTicketNumber(self, place_number, ticket_number):
        self.model.list_of_places[place_number].set_place_state_to_reserved()
        self.model.list_of_places[place_number].set_ticket_number(ticket_number)
        self.model.list_of_labels_to_display_place_number[place_number].config(
            bg="green")
        self.model.list_of_labels_to_display_ticket_number[place_number].config(
            text=ticket_number)
        return self.model.list_of_places[place_number]

    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Faild to connect, return code %d\n", rc)

        client = mqtt_client.Client(client_id)
        client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(broker, port)
        return client
