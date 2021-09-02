from tkinter import *
from paho.mqtt import client as mqtt_client
import random
import json
from enum import Enum
from datetime import datetime
import statistics
import sqlite3
import place
from config import broker, username, password

port = 1883
topic_from_place = "macherdaach/queue/messageFromPlace"
topic_from_controller = "macherdaach/queue/messageFromController"
client_id = f'python-mqtt-{random.randint(0,1000)}'

numberOfPlaces = 8




# Initialize list_of_places
list_of_places = []
for i in range(numberOfPlaces):
    list_of_places.append(place.Place())

# list_of_ticket_numbers is only used if ticket number could not be registered to a place
list_of_ticket_numbers = []

list_of_processing_times = []

# Not used yet
# database = "database.db"
# connection = sqlite3.connect(database)

window = Tk()
window.geometry("1680x1050")
window.title("Macherddach Badge Queue")

# Initialize columns of layout
window.columnconfigure(0, weight=2)  # Number of even places
window.columnconfigure(1, weight=1)  # Shows if occupied and ticket number
window.columnconfigure(2, weight=1)  # Empty
window.columnconfigure(3, weight=2)  # Number of odd places
window.columnconfigure(4, weight=1)  # Shows if occupied and ticket number
window.columnconfigure(5, weight=1)  # Shows next couple of ticket numbers

# Initialize rows of layout
for place in range(numberOfPlaces+1):
    window.rowconfigure(place, weight=1)

list_of_labels_to_display_ticket_number = []
list_of_labels_to_display_place_number = []
list_of_labels_to_display_queue = []

# Initialize labels
for place in range(numberOfPlaces):
    label_to_display_ticket_number = Label(window, text=" Frei ")
    label_to_display_ticket_number.config(font=("Courier", 44))
    label_to_display_ticket_number.grid(
        row=((place//2)*2)+1, column=((place % 2)*3)+1)
    list_of_labels_to_display_ticket_number.append(
        label_to_display_ticket_number)

    label_to_display_place_number = Label(
        window, text="Platz " + str(place+1), bg="green")
    label_to_display_place_number.config(font=("Courier", 44))
    label_to_display_place_number.grid(
        row=((place//2)*2)+1, column=((place % 2)*3))
    list_of_labels_to_display_place_number.append(
        label_to_display_place_number)

for i in range(numberOfPlaces):
    element = Label(window, text="--")
    element.config(font=("Courier", 20))
    element.grid(row=i+1, column=5)
    list_of_labels_to_display_queue.append(element)

headline = Label(window, text="Macherdaach Badge Lötplatz-Zuweisungssystem")
headline.config(font=("Courier", 32))
headline.grid(row=0, column=0, columnspan=5)

queue_headline = Label(window, text="Queue")
queue_headline.config(font=("Courier", 32))
queue_headline.grid(row=0, column=5)


def connect_mqtt() -> mqtt_client:
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


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from {msg.topic}` topic")
        try:
            mqtt_decoded = str(msg.payload.decode("utf-8", "ignore"))
            json_loaded = json.loads(mqtt_decoded)
            if(msg.topic == topic_from_place):
                # message received from place
                if (json_loaded["place_occupied"] == True):
                    # Place was taken by the owner of the ticket_number
                    # Place number in MQTT-Message starts with 1 and must be decremented
                    place_number = json_loaded["place_number"] - 1
                    if(list_of_places[place_number].state == PlaceState.REGISTERED):
                        print("Occupied: " + str(place_number))
                        list_of_places[place_number].occupyPlace()
                        list_of_labels_to_display_place_number[place_number].config(
                            bg="red")
                        list_of_labels_to_display_ticket_number[place_number].config(
                            text="Belegt")
                        list_of_places[place_number].setstarttime(datetime.now(
                            tz=None))
                    else:
                        print(
                            "Not occupied - there is no ticket registered to this place")
                else:
                    # Place was given up by owner
                    print("Released: " +
                          str(json_loaded["place_number"]))
                    place_number = json_loaded["place_number"] - 1

                    if (list_of_places[place_number].state != PlaceState.OCCUPIED):
                        print("Place is not in state OCCUPIED - can not be released")

                    else:
                        processing_time = datetime.now(
                            tz=None) - list_of_places[place_number].start_time
                        list_of_places[place_number] = Place(place_number)

                        list_of_labels_to_display_place_number[place_number].config(
                            bg="green")
                        list_of_labels_to_display_ticket_number[place_number].config(
                            text="--")
                        # Save processing time in
                        print("Processing time: " + str(processing_time))
                        list_of_processing_times.append(processing_time)
                        # Search for a new number in list_of_ticket_numbers to be registered to the released place
                        if list_of_ticket_numbers:
                            # ticket list is not empty - register number from ticket list to place
                            # Take first element of list_of_ticket_numbers and register the number to the current place and display it
                            ticket_number = list_of_ticket_numbers.pop(0)
                            list_of_places[place_number].ticket_number = ticket_number
                            list_of_places[place_number].state = PlaceState.REGISTERED
                            list_of_labels_to_display_ticket_number[place_number].config(
                                text="%6d" % ticket_number)
                            update_queue()

            elif (msg.topic == topic_from_controller):
                # message received from controller
                new_number = json_loaded["new_number"]
                print("Received new ticket number from controller: " +
                      str(new_number))
                # Check if new number is already in use
                for place in list_of_places:
                    if place.ticket_number == new_number:
                        print("New number " + str(new_number) +
                              " already registered")
                        return
                if new_number in list_of_ticket_numbers:
                    print("New number " + str(new_number) +
                          "already in ticket number list")
                    return
                for count, place in enumerate(list_of_places):
                    # Search an empty place
                    if (place.state == PlaceState.FREE):
                        # Found one - register ticket number to place
                        print("Register ticket: " +
                              str(new_number) + " to free place")

                        place.state = PlaceState.REGISTERED
                        place.ticket_number = new_number
                        list_of_labels_to_display_place_number[count].config(
                            bg="green")
                        list_of_labels_to_display_ticket_number[count].config(
                            text=place.ticket_number)
                        break
                    if (place == list_of_places[-1]):
                        # Found no vacant place - put number in queue
                        print("New number " + str(new_number))
                        list_of_ticket_numbers.append(new_number)
                        update_queue()
        except Exception as e:
            print(str(e))
            print("Something went wrong on mqtt reception")

    client.subscribe(topic_from_place)
    client.subscribe(topic_from_controller)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)

    client.loop_start()
    window.after(0, update_processing_time)
    window.mainloop()


def update_queue():
    print("Update Queue")

    sorted_list_of_start_time = sorted(
        list_of_places, key=lambda x: x.start_time or datetime.now(tz=None))
    for i in list_of_places:
        print(i.start_time)
    for i in sorted_list_of_start_time:
        print(i.start_time)
    try:
        median_processing_time = statistics.median(list_of_processing_times)
    except:
        median_processing_time = 0
    print("Median processing time: " + str(median_processing_time))
    print("Now: " + str(datetime.now(tz=None)))

    for count, element in enumerate(list_of_labels_to_display_queue):
        print("Count " + str(count))
        if count < len(list_of_ticket_numbers):
            print("Count " + str(count) + " < " +
                  "len(ticket_numbers): " + str(len(list_of_ticket_numbers)))
            print("Number " + str(list_of_ticket_numbers[count]))
            print(str(datetime.now(tz=None)) + " - " +
                  str(sorted_list_of_start_time[count].start_time))
            try:
                current_processing_time = datetime.now(
                    tz=None) - sorted_list_of_start_time[count].start_time
            except:
                current_processing_time = 0
            print("time difference: " + str(current_processing_time))
            if (median_processing_time == 0 or current_processing_time == 0):
                element.config(
                    text=str(list_of_ticket_numbers[count]) + "(???)")
            else:
                estimated_processing_time = median_processing_time - current_processing_time
                element.config(text=str(list_of_ticket_numbers[count]) + "(" + str(
                    int(estimated_processing_time.total_seconds()/60)) + " min)")
        else:
            element.config(text="--")


def update_processing_time():
    window.after(60000, update_processing_time)
    update_queue()


if __name__ == '__main__':
    run()
