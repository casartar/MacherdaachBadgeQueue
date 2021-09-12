from tkinter import Tk, Label


class View:
    def __init__(self, numberOfPlaces):
        self.numberOfPlaces = numberOfPlaces
        self.window = Tk()
        self.window.geometry("1680x1050")
        self.window.title("Macherddach Badge Queue")
        # Initialize columns of layout
        self.window.columnconfigure(0, weight=2)  # Number of even places
        self.window.columnconfigure(1, weight=1)  # Shows if occupied and ticket number
        self.window.columnconfigure(2, weight=1)  # Empty
        self.window.columnconfigure(3, weight=2)  # Number of odd places
        self.window.columnconfigure(4, weight=1)  # Shows if occupied and ticket number
        self.window.columnconfigure(5, weight=1)  # Shows next couple of ticket numbers

        # Initialize rows of layout
        for place in range(numberOfPlaces + 1):
            self.window.rowconfigure(place, weight=1)

    class QueueLabel(Label):
        def set_text(self, new_text):
            self.config(text=new_text)
            return self

        def set_color(self, new_color):
            self.config(bg=new_color)
            return self

    def initView(self, list_of_labels_to_display_ticket_number, list_of_labels_to_display_place_number,
                 list_of_labels_to_display_in_queue):
        # Initialize labels
        for place in range(self.numberOfPlaces):
            label_to_display_ticket_number = self.QueueLabel(self.window).set_text("Frei")
            label_to_display_ticket_number.config(font=("Courier", 44))
            label_to_display_ticket_number.grid(
                row=((place // 2) * 2) + 1, column=((place % 2) * 3) + 1)
            list_of_labels_to_display_ticket_number.append(
                label_to_display_ticket_number)

            label_to_display_place_number = self.QueueLabel(self.window).set_text("Platz " + str(place + 1)).set_color("green")
            label_to_display_place_number.config(font=("Courier", 44))
            label_to_display_place_number.grid(
                row=((place // 2) * 2) + 1, column=((place % 2) * 3))
            list_of_labels_to_display_place_number.append(
                label_to_display_place_number)

        for i in range(self.numberOfPlaces):
            element = self.QueueLabel(self.window).set_text("--")
            element.config(font=("Courier", 20))
            element.grid(row=i + 1, column=5)
            list_of_labels_to_display_in_queue.append(element)

        # Init Headline
        headline = self.QueueLabel(self.window).set_text("Macherdaach Badge Lötplatz-Zuweisungssystem")
        headline.config(font=("Courier", 32))
        headline.grid(row=0, column=0, columnspan=5)

        queue_headline = self.QueueLabel(self.window).set_text("Queue")
        queue_headline.config(font=("Courier", 32))
        queue_headline.grid(row=0, column=5)
