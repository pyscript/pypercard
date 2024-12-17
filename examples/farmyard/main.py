import invent
from invent.ui import *


# Datastore ############################################################################

await invent.start_datastore()
invent.datastore["number_of_honks"] = 0
invent.datastore["number_of_oinks"] = 0


# Code #################################################################################


def navigate(message):
    print(message)
    if message.button.name == "to_lucy":
        invent.show_page("Lucy")
    elif message.button.name == "to_percy":
        invent.show_page("Percy")


def make_honk(message):
    invent.datastore["number_of_honks"] = (
        invent.datastore["number_of_honks"] + 1
    )
    # invent.play_sound(invent.media.sounds.honk.mp3)


def make_oink(message):
    invent.datastore["number_of_oinks"] = (
        invent.datastore["number_of_oinks"] + 1
    )
    # invent.play_sound(invent.media.sounds.oink.mp3)


def make_geese(number_of_honks):
    return [Label(text="🪿") for _ in range(number_of_honks)]


def make_pigs(number_of_oinks):
    return [Label(text="🐖") for _ in range(number_of_oinks)]


# Channels #############################################################################


invent.subscribe(navigate, to_channel="navigate", when_subject=["press"])
invent.subscribe(make_honk, to_channel="honk", when_subject=["press", "touch"])
invent.subscribe(make_oink, to_channel="oink", when_subject=["press", "touch"])


# User Interface #######################################################################


app = invent.App(
    name="Farmyard!",
    pages=[
        Page(
            name="Lucy",
            children=[
                Column(
                    children=[
                        Image(
                            image=invent.media.images.goose.png,
                            channel="honk",
                            horizontal_align="center",
                        ),
                        Row(
                            horizontal_align="center",
                            children=[
                                Button(
                                    name="button honk",
                                    text="HONK!",
                                    channel="honk",
                                ),
                                Button(
                                    name="to_percy",
                                    text="Visit Percy",
                                    channel="navigate",
                                ),
                            ],
                        ),
                        Row(
                            children=[
                                Label(
                                    name="number_of_honks",
                                    text=from_datastore("number_of_honks"),
                                    horizontal_align="center",
                                ),
                                Slider(
                                    value=from_datastore("number_of_honks"),
                                    name="Honk Slider",
                                    step=1,
                                    space=2,
                                ),
                            ]
                        ),
                        Row(
                            id="geese",
                            horizontal_align="center",
                            children=from_datastore(
                                "number_of_honks", with_function=make_geese
                            ),
                        ),
                    ]
                ),
            ],
        ),
        Page(
            name="Percy",
            children=[
                Column(
                    children=[
                        Image(
                            image=invent.media.images.pig.png,
                            channel="oink",
                            horizontal_align="center",
                        ),
                        Row(
                            horizontal_align="center",
                            children=[
                                Button(
                                    name="button oink",
                                    text="OINK!!",
                                    channel="oink",
                                ),
                                Button(
                                    name="to_lucy",
                                    text="Visit Lucy",
                                    channel="navigate",
                                ),
                                Label(
                                    name="number_of_oinks",
                                    text=from_datastore("number_of_oinks"),
                                    horizontal_align="center",
                                ),
                            ],
                        ),
                        Row(
                            id="pigs",
                            horizontal_align="center",
                            children=from_datastore(
                                "number_of_oinks", with_function=make_pigs
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)


# GO! ##################################################################################

invent.go()
