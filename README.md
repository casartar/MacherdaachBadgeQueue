# MacherdaachBadgeQueue

This repo houses the Lötplatz-Zuweisungssystem for the Macherdaach 2021 in Landau, hosted by [ZTL](https://ztl.space/). 

## Getting started ...

### ... with PyCharm

1. Checkout the repo via ```git clone``` 
2. Get the MQTT-config file to access the mqtt broker
   1. Contact: [Casartar](https://github.com/casartar) or [JohnnyMoonlight](https://github.com/JohnnyMoonlight)
3. Initialize with your favourite IDE
   1. Sample configuration for [PyCharm](https://www.jetbrains.com/help/pycharm/quick-start-guide.html): ![img.png](docs/img/img.png)
   2. ...

### ... on your favourite command line

This project is self-contained. You should have no trouble executing the application from the directory 'Software'

```python main.py```


## Sample MQTT Messages

### Topics

```topic_from_place = "macherdaach/queue/messageFromPlace"```

```topic_from_controller = "macherdaach/queue/messageFromController"```

### New user has arrived at place one and starts soldering

```
{
  "place_number": 1,
  "place_occupied": true
}
```

### User has finished soldering

```
{
  "place_number": 1,
  "place_occupied": false
}
```

### Place new ticket number in queue
```
{
  "new_number":1
}
```

## Properties to access view

These properties in the package view are responsible for displaying information in the gui.

![](docs/img/labels_and_arrays_ing_gui.png)