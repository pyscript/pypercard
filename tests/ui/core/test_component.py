import upytest
import umock
from pyscript.web import div
from invent.ui import core


def test_event():
    """
    Events have a description and key/value specifications of the
    content of the messages they send.

    class MyWidget(Widget):

        name = TextProperty()
        hold = Event(
            "When the button is held",
            duration="For how long the button was pressed.",
        )

        def _handle_hold(self, e):
            self.publish("hold", duration=e.duration)

        def render(self, container):
            self.element = pyscript.web.button("Click me")
            self.element.addEventListener("click", self._handle_hold)
    """
    ev = core.Event("This is a test", foo="A foo to handle")
    assert ev.description == "This is a test"
    assert "foo" in ev.content
    assert ev.content["foo"] == "A foo to handle"


def test_event_create_message():
    """
    An Event creates the expected message.
    """
    ev = core.Event("This is a test", foo="A foo to handle")
    # Cannot include fields that have not been specified.
    with upytest.raises(ValueError):
        ev.create_message("subject", baz="This will fail")
    # Can include all the fields.
    msg = ev.create_message("subject", foo="Foo to you")
    assert msg._subject == "subject"
    assert msg.foo == "Foo to you"
    # Cannot miss an expected field.
    with upytest.raises(ValueError):
        ev.create_message("subject")


def test_event_as_dict():
    """
    The expected dictionary definition of an Event is generated.
    """
    ev = core.Event("This is a test", foo="A foo to handle")
    assert ev.as_dict() == {
        "description": "This is a test",
        "content": {
            "foo": "A foo to handle",
        },
    }


def test_component_init_with_given_values():
    """
    Given a name and id, these are reflected in the resulting object.
    """

    class TestComponent(core.Component):

        def render(self):
            return div()

    tc = TestComponent(name="test1", id="12345", visible=False)
    assert tc.name == "test1"
    assert tc.id == "12345"
    assert tc.visible is False
    assert tc.parent is None


def test_component_init_with_no_values():
    """
    Initialisation with no defaults ensures they are generated for the user.
    """

    class TestComponent(core.Component):

        def render(self):
            return div()

    tc = TestComponent()
    assert tc.name == "TestComponent 1"
    assert tc.id is not None
    tc2 = TestComponent()
    assert tc2.name == "TestComponent 2"
    assert tc2.id is not None


def test_component_init_with_properties():
    """
    Properties can be initialized with constructor keyword arguments.
    """

    class TestComponent(core.Component):
        text = core.TextProperty(
            "A text property", default_value="test", required=True
        )
        integer = core.IntegerProperty("An integer property")
        val = core.FloatProperty("A float property", default_value=1.23)
        flag = core.BooleanProperty("A test property", default_value=False)

        def render(self):
            return div()

    tc = TestComponent(text="bar", integer=123, val=123.4, flag=True)
    assert tc.text == "bar"
    assert tc.integer == 123
    assert tc.val == 123.4
    assert tc.flag is True

    # Uninitialized properties will be set to defaults.
    tc = TestComponent()
    assert tc.text == "test"
    assert tc.integer is None
    assert tc.val == 1.23
    assert tc.flag is False

    # Cannot initialize a required property with None.
    with upytest.raises(core.ValidationError):
        TestComponent(text=None)

    # Cannot initialize a nonexistent property.
    with upytest.raises(AttributeError):
        TestComponent(no_such_prop=None)


def test_component_get_component_by_id():
    """
    Once a component is created, it's possible to retrieve it directly via id.
    """

    class TestComponent(core.Component):

        def render(self):
            return div()

    tc = TestComponent()
    assert TestComponent.get_component_by_id(tc.id) == tc


def test_component_properties():
    """
    A component's (widget's) properties are available in a dictionary.
    """

    class MyWidget(core.Widget):
        """
        A test widget.
        """

        foo = core.TextProperty("This is a foo", default_value="bar")
        numberwang = core.IntegerProperty(
            "That's numberwang!", default_value=42
        )
        favourite_colour = core.ChoiceProperty(
            "Best colour.",
            choices=[
                "black",
                "very very dark grey",
                "deeply off white",
                "coal",
            ],
        )

    properties = MyWidget.properties()

    assert isinstance(properties["foo"], core.TextProperty)
    assert isinstance(properties["numberwang"], core.IntegerProperty)
    assert isinstance(properties["favourite_colour"], core.ChoiceProperty)


def test_component_events():
    """
    A component's (widget's) events are available in a dictionary.
    """

    class MyWidget(core.Widget):
        """
        A test widget.
        """

        ping = core.Event("Send a ping.", strength="The strength of the ping.")

    mbp = MyWidget.events()
    assert isinstance(mbp["ping"], core.Event)


def test_component_definition():
    """
    A JSON serializable data structure representing the component class is
    returned. Should include the name, properties, events and icon for the
    component.
    """

    class MyWidget(core.Widget):
        """
        A test widget.
        """

        foo = core.TextProperty("This is a foo", default_value="bar")
        numberwang = core.IntegerProperty(
            "That's numberwang!", default_value=42
        )
        favourite_colour = core.ChoiceProperty(
            "Best colour.",
            default_value="black",
            choices=[
                "black",
                "very very dark grey",
                "deeply off white",
                "coal",
            ],
        )
        bloop = core.Event(
            "Bloop the blooper", strength="The strength of the bloop."
        )

        @classmethod
        def icon(cls):
            return "<button>Click me!</button>"

        def render(self):
            return div()

    result = MyWidget.definition()
    assert "properties" in result
    assert "events" in result
    assert "icon" in result
    assert result["name"] == "MyWidget"
    assert result["properties"]["name"]["property_type"] == "TextProperty"
    assert result["properties"]["name"]["default_value"] is None
    assert result["properties"]["id"]["property_type"] == "TextProperty"
    assert result["properties"]["id"]["default_value"] is None
    assert result["properties"]["channel"]["property_type"] == "TextProperty"
    assert result["properties"]["channel"]["default_value"] is None
    assert result["properties"]["foo"]["property_type"] == "TextProperty"
    assert result["properties"]["foo"]["default_value"] == "bar"
    assert (
        result["properties"]["numberwang"]["property_type"]
        == "IntegerProperty"
    )
    assert result["properties"]["numberwang"]["default_value"] == 42
    assert (
        result["properties"]["favourite_colour"]["property_type"]
        == "ChoiceProperty"
    )
    assert result["properties"]["favourite_colour"]["default_value"] == "black"
    assert result["events"]["bloop"]["description"] == "Bloop the blooper"
    assert (
        result["events"]["bloop"]["content"]["strength"]
        == "The strength of the bloop."
    )
    assert result["icon"] == "<button>Click me!</button>"


def test_component_as_dict():
    """
    Ensure the expected state of the component (widget) is returned as a Python
    dictionary.
    """

    class MyWidget(core.Component):
        """
        A test widget.
        """

        foo = core.TextProperty("This is a foo", default_value="bar")
        numberwang = core.IntegerProperty(
            "That's numberwang!", default_value=42
        )
        favourite_colour = core.ChoiceProperty(
            "Best colour.",
            default_value="black",
            choices=[
                "black",
                "very very dark grey",
                "deeply off white",
                "coal",
            ],
        )
        bloop = core.Event(
            "Bloop the blooper", strength="The strength of the bloop."
        )

        @classmethod
        def icon(cls):
            return "<button>Click me!</button>"

        def render(self):
            return div()

    mw = MyWidget(
        foo=core.from_datastore("ds_key"),
        numberwang=55,
        layout=dict(alpha="a", bravo="b"),
    )
    expected = {
        "type": "MyWidget",
        "properties": {
            "foo": "from_datastore('ds_key')",
            "numberwang": 55,
            "favourite_colour": "black",
            "id": "invent-mywidget-1",
            "name": "MyWidget 1",
            "enabled": True,
            "visible": True,
            "layout": dict(alpha="a", bravo="b"),
        },
    }
    assert mw.as_dict() == expected


def test_container_as_dict():
    """
    Ensure the expected state of a container is returned as a Python
    dictionary.
    """

    class MyLayout(core.Layout):
        layout_prop = core.TextProperty("Layout prop", "lp")

    class MyContainer(core.Container):
        layout_class = MyLayout
        container_prop = core.TextProperty("Container prop", "cp")

    class MyWidget(core.Component):
        widget_prop = core.TextProperty("Widget prop", "wp")

        def render(self):
            return div()

    mc = MyContainer()
    mc.append(MyWidget())
    expected = {
        "type": "MyContainer",
        "properties": {
            "container_prop": "cp",
            "id": "invent-mycontainer-1",
            "name": "MyContainer 1",
            "enabled": True,
            "visible": True,
            "background_color": None,
            "border_color": None,
            "border_width": None,
            "border_style": None,
            "children": [
                {
                    "type": "MyWidget",
                    "properties": {
                        "widget_prop": "wp",
                        "id": "invent-mywidget-1",
                        "name": "MyWidget 1",
                        "enabled": True,
                        "visible": True,
                        "layout": dict(layout_prop="lp"),
                    },
                }
            ],
        },
    }
    assert mc.as_dict() == expected


def test_component_update_attribute():
    """
    Ensure the referenced attribute is updated and removed as expected.
    """

    class MyWidget(core.Widget):
        """
        A test widget.
        """

        foo = core.TextProperty("This is a foo", default_value="bar")

        def render(self):
            return div()

    w = MyWidget()
    # There is no attribute called "test" on the widget's element.
    assert w.element.hasAttribute("test") is False
    # Update an attribute (add it).
    w.update_attribute("test", "yes")
    assert w.element.getAttribute("test") == "yes"
    # Update an attribute (change it).
    w.update_attribute("test", "yes2")
    assert w.element.getAttribute("test") == "yes2"
    # Update an attribute (remove it because it is false-y).
    w.update_attribute("test", "")
    assert w.element.hasAttribute("test") is False


def test_component_default_icon():
    """
    The SVG image returned by the Component's icon class method (to be
    overridden by children), is the expected default safe catch-all image.
    """

    class TestComponent(core.Component):

        def render(self):
            return div()

    assert TestComponent.icon() == core._DEFAULT_ICON


def test_widget_init_defaults():
    """
    Ensure an instance of a Widget class has default values for id, visible and
    channel.
    """

    class MyWidget(core.Widget):

        def render(self):
            return div()

    w = MyWidget(name="test")
    # There is a default id of the expected default "shape".
    assert w.id is not None
    assert w.id.startswith("invent-")
    assert len(w.id[7:]) == 10
    # The default visibility is True.
    assert w.visible is True
    # The default channel for widget related messages is the same as its id.
    assert w.channel == w.id


def test_widget_init_override():
    """
    It's possible to override the default values for id, visible and channel.
    """

    class MyWidget(core.Widget):

        def render(self):
            return div()

    w = MyWidget(name="test", id="foo", visible=False, channel="test_channel")
    assert w.id == "foo"
    assert w.visible is False
    assert w.channel == "test_channel"


def test_widget_publish():
    """
    A widget knows what channels to publish any messages to, from
    MessageBlueprints.
    """

    class MyWidget(core.Widget):

        ping = core.Event("Send a ping.", strength="Strength of ping")

        def render(self):
            return div()

    with umock.patch("invent:publish") as mock_publish:
        w = MyWidget()
        w.channel = "my_channel"
        w.publish("ping", strength=100)
        assert mock_publish.call_count == 1


def test_widget_when_with_do():
    """
    A widget's when method can be used to short-cut message subscriptions.
    """

    class TestWidget(core.Widget):

        def render(self):
            return div()

    tw = TestWidget(name="test1", id="12345")

    def my_handler(message):
        return

    # Simple case with default channel name (component's id).
    with umock.patch("invent.ui.core.component:invent.subscribe") as mock_sub:
        tw.when("push", do=my_handler)
        mock_sub.assert_called_once_with(
            handler=my_handler, to_channel="12345", when_subject="push"
        )

    # Specialised case with explicit channel name[s].
    with umock.patch("invent.ui.core.component:invent.subscribe") as mock_sub:
        tw.when("push", to_channel="test_channel", do=my_handler)
        mock_sub.assert_called_once_with(
            handler=my_handler, to_channel="test_channel", when_subject="push"
        )


def test_widget_when_as_decorator():
    """
    A widget's when method can be used to short-cut decorating handler
    functions.
    """

    class TestWidget(core.Widget):

        def render(self):
            return div()

    tw = TestWidget(name="test1", id="12345")

    # Simple case with default channel name (component's id).
    with umock.patch("invent.ui.core.component:invent.subscribe") as mock_sub:

        @tw.when("push")
        def my_first_handler(message):
            return

        assert mock_sub.call_count == 1

        mock_sub.reset_mock()

        @tw.when("push", to_channel="test_channel")
        def my_second_handler(message):
            return

        assert mock_sub.call_count == 1


def test_layout():
    """
    A component's layout property interacts correctly with its parent.
    """

    class LayoutA(core.Layout):
        alpha = core.TextProperty("Alpha", "a")

    class LayoutB(core.Layout):
        bravo = core.TextProperty("Bravo", "b")

    class ContainerA(core.Container):
        layout_class = LayoutA

    class ContainerB(core.Container):
        layout_class = LayoutB

    class TestComponent(core.Component):
        def render(self):
            return div()

    tc = TestComponent(layout=dict(alpha="apple"))
    assert tc.layout == dict(alpha="apple")

    # A Layout object is created from the dict when the widget gets a parent.
    a = ContainerA()
    a.append(tc)
    layout_a = tc.layout
    assert type(tc.layout) is LayoutA
    assert tc.layout.element is tc.element
    assert tc.layout.alpha == "apple"
    assert tc.layout.component is tc
    assert tc.layout.element is tc.element

    # Layout properties can be set like any other property.
    tc.layout.alpha = "antelope"
    assert tc.layout.alpha == "antelope"

    # Layout can be set from a dict with compatible keys.
    tc.layout = dict(alpha="avocado")
    assert tc.layout is not layout_a
    layout_a1 = tc.layout
    assert type(tc.layout) is LayoutA
    assert tc.layout.alpha == "avocado"

    with upytest.raises(AttributeError):
        tc.layout = dict(alpha="aardvark", no_such_prop=None)
    assert tc.layout is layout_a1
    assert tc.layout.alpha == "avocado"

    # Layout can be set from a layout object of the correct type.
    layout_a2 = LayoutA(tc, alpha="apple")
    tc.layout = layout_a2
    assert tc.layout is not layout_a2  # A copy has been made.
    assert type(tc.layout) is LayoutA
    assert tc.layout.alpha == "apple"

    # Layout cannot be set from any other type.
    for value in [LayoutB(tc), "a string", ["a list"]]:
        with upytest.raises(TypeError):
            tc.layout = value

    # The layout object is kept when the widget loses its parent, and can be
    # copied to another parent of the same type.
    layout_a3 = tc.layout
    a.remove(tc)
    assert tc.layout is layout_a3
    assert layout_a3.alpha == "apple"

    a2 = ContainerA()
    a2.append(tc)
    assert tc.layout is not layout_a3  # A copy has been made.
    assert layout_a3.alpha == "apple"

    # A different parent type requires a different layout type.
    a2.remove(tc)
    b = ContainerB()
    with upytest.raises(TypeError):
        b.append(tc)

    layout_b = LayoutB(tc, bravo="banana")
    tc.layout = layout_b
    assert tc.layout is layout_b
    b.append(tc)
    assert tc.layout is not layout_b  # A copy has been made.
    assert type(tc.layout) is LayoutB
    assert tc.layout.bravo == "banana"


def test_container_on_content_changed():
    """
    The children are re-rendered when the content list is changed.
    """
    pass  # TODO: Finish me.
