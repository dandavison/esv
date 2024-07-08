import logging
import sys
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import Callable, ClassVar, Iterable, Optional

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

    def _apply_to_tree(self, event: Event):
        """
        Recurse to children, then handle it at this node and update the scene.
        """
        for child in self.children.values():
            child._apply_to_tree(event)
        print(f"          {self}")
        self.handle(event)
        self._update_scene()

    # def _get_mobject(self) -> manim.VMobject:
    #     mobj = self.render()
    #     mobj.add(*(c._get_mobject() for c in self.children.values()))
    #     return mobj

    @abstractmethod
    def render(self) -> manim.VMobject:
        """VMobject for this entity, without its children."""
        ...

    def explain(self, latex: str, target: Optional["Entity"] = None):
        self.animations.append(
            lambda: Explanation(target=target or self, latex=latex).animate()
        )

    def _update_scene(self, **kwargs):
        """
        Mutate `self.mobj` so that it represents the current state of `entity` and play any enqueued animations.
        """
        self.mobj.become(self.render(**kwargs).move_to(self.mobj))
        while self.animations:
            print(f"playing animations for {self}")
            for anim in self.animations.popleft()():
                self.scene.play(anim)

    def __str__(self) -> str:
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
                entity._apply_to_tree(event)
            self.wait(2)

    def construct(self):
        try:
            self._construct()
        except Exception as err:
            print(f"{err.__class__.__name__}({err})", file=sys.stderr)
            import pdb

            pdb.post_mortem()
            exit(1)
