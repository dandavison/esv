from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

from manim import (
    DOWN,
    UR,
    Animation,
    Arrow,
    FadeIn,
    FadeOut,
    SurroundingRectangle,
    Tex,
    VGroup,
    VMobject,
    Wait,
)

if TYPE_CHECKING:
    from esv import Entity


@dataclass
class Explanation:
    target: "Entity"
    latex: str
    width: str = "20em"
    font_family: str = r"\sffamily"
    justification: str = r"\raggedright"
    background_color: str = "#2F2F2F"

    def render(self) -> VMobject:
        text = f"{{{self.width}}} {self.font_family} {self.justification} {self.latex}"
        tex = Tex(text, tex_environment="minipage", font_size=16)
        rect = SurroundingRectangle(
            tex,
            buff=0.2,
            color=self.background_color,
            corner_radius=0.2,
            fill_opacity=1,
        )
        box = VGroup(rect, tex).to_corner(UR)
        arrow = Arrow(
            start=box.get_boundary_point(DOWN),
            buff=0,
            end=self.target.mobj.get_boundary_point(UR),
            color=self.background_color,
            max_tip_length_to_length_ratio=0.05,
        )
        return VGroup(box, arrow)

    def animate(self) -> Iterable[Animation]:
        yield Wait(0.5)
        mobj = self.render()
        yield FadeIn(mobj)
        yield Wait(4)
        yield FadeOut(mobj)


def tex_escape(s: str) -> str:
    return s.replace("_", r"\_")
