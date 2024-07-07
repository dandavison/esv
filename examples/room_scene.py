from dataclasses import dataclass
from typing import Iterable, cast

from manim import DL, DOWN, DR, UP, Line, Text, VMobject

import esv
import esv.explanation


@dataclass
class Event(esv.Event):
    active_chair: "Chair"


@dataclass
class Object(esv.Entity):
    name: str

    def handle(self, _: esv.Event):
        pass

    def render(self) -> VMobject:
        return Text(self.name)


@dataclass
class Ray(esv.Entity):
    start: esv.Entity
    end: esv.Entity

    def handle(self, _: esv.Event):
        pass

    def render(self) -> VMobject:
        return Line(
            start=self.start.mobj.get_boundary_point(DOWN),
            end=self.end.mobj.get_boundary_point(UP),
        )


@dataclass
class Lamp(Object):
    def off(self):
        self.mobj.remove(self.children["ray"].mobj)

    def shine_on(self, object: "Object"):
        self.add_child(Ray("ray", start=self, end=object))
        self.explain(
            f"The lamp is shining on {object.name}, because the direction of the lamp intersects with its location."
            "This is roughly how lamps work."
        )


@dataclass
class Chair(Object):
    pass


@dataclass
class Person(Object):
    def handle(self, event: Event):
        self.sit(event.active_chair)

    def sit(self, chair: Chair):
        self.mobj.move_to(chair.mobj, aligned_edge=UP).shift(UP * 0.5)


class RoomScene(esv.Scene):
    def init(self) -> None:
        chair1 = Chair(name="chair 1")
        chair2 = Chair(name="chair 2")
        person = Person(name="person")
        lamp = Lamp(name="lamp")

        lamp.mobj.align_on_border(UP)
        chair1.mobj.shift(DL * 2)
        chair2.mobj.shift(DR * 2)

        self.lamp = lamp
        self.person = person
        self.chair1 = chair1
        self.chair2 = chair2

        for e in [lamp, chair1, chair2, person]:
            self.entities[e.name] = e

    def events(self) -> Iterable[Event]:
        for i in range(3):
            chair = cast(
                Chair, self.entities["chair 1"] if i % 2 else self.entities["chair 2"]
            )
            yield Event(chair)

    def handle(self, event: Event):
        self.person.handle(event)
        self.wait(1)
        self.lamp.shine_on(self.person)
        self.wait(1)
        self.lamp.off()
