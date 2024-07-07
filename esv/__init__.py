import logging
import sys
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Callable, ClassVar, Iterable

import manim

from esv.explanation import Explanation


@dataclass
class Event:
    pass


@dataclass
class Entity(ABC):
    name: str

    scene: ClassVar[manim.Scene]

    def __post_init__(self) -> None:
        # This is the only time self.mobj is assigned to; hereafter it's mutated
        # in-place by self.render_to_screen()
        self.mobj = self.render()

        self.children = dict[str, "Entity"]()
        self.animations = deque[Callable[[], Iterable[manim.Animation]]]()

    def add_child(self, child: "Entity") -> None:
        if child.name in self.children:
            logging.warning(f"{child} is already a child of {self}")
        self.children[child.name] = child

    @abstractmethod
    def handle(self, event: Event) -> bool:
        """Return True if the event caused the entity state to change, or enqueued animations."""
        ...

        # for child in self.children.values():
        #     child.handle(event)

    # def _get_mobject(self) -> manim.VMobject:
    #     mobj = self.render()
    #     mobj.add(*(c._get_mobject() for c in self.children.values()))
    #     return mobj

    @abstractmethod
    def render(self) -> manim.VMobject:
        """VMobject for this entity, without its children."""
        ...

    def explain(self, latex: str):
        self.animations.append(lambda: Explanation(target=self, latex=latex).animate())

    def _update_scene(self, **kwargs):
        """
        Mutate `self.mobj` so that it represents the current state of `entity` and play any enqueued animations.
        """
        self.mobj.become(self.render(**kwargs).move_to(self.mobj))
        while self.animations:
            for anim in self.animations.popleft()():
                print(f"playing animation {anim} for {self}")
                self.scene.play(anim)

    def __repr__(self) -> str:
        return self.name


class Scene(manim.Scene, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert not hasattr(Entity, "scene"), "There can be only one Scene"
        Entity.scene = self
        self.entities = dict[str, Entity]()

    @abstractmethod
    def init(self) -> None:
        """
        Populate self.entities
        """

    @abstractmethod
    def events(self) -> Iterable[Event]: ...

    def _construct(self):
        self.init()
        for event in self.events():
            print(f"🟨 {event}")
            for entity in self.entities.values():
                entity.handle(event)
                entity._update_scene()
            self.wait(2)

    def construct(self):
        try:
            self._construct()
        except Exception as err:
            print(f"{err.__class__.__name__}({err})", file=sys.stderr)
            import pdb

            pdb.post_mortem()
            exit(1)
