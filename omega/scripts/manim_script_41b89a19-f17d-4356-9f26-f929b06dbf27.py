from manim import *

class CircleAreaRelation(Scene):
    def construct(self):
        # Introduction text
        intro_text = Text("Relationship between Area and Diameter of a Circle", font_size=36)
        self.play(Write(intro_text))
        self.wait(2)
        self.play(FadeOut(intro_text))

        # Create a circle
        circle = Circle(radius=2, color=BLUE)
        self.play(Create(circle))

        # Label the center of the circle
        center_dot = Dot(circle.get_center(), color=RED)
        center_label = Tex("Center", color=RED).next_to(center_dot, DR)
        self.play(Create(center_dot), Write(center_label))

        # Create a diameter line
        diameter_line = Line(circle.get_left(), circle.get_right(), color=GREEN)
        diameter_label = Tex("Diameter", color=GREEN).next_to(diameter_line, DOWN)
        self.play(Create(diameter_line), Write(diameter_label))
        self.wait(1)

        # Show the radius
        radius_line = Line(circle.get_center(), circle.get_right(), color=YELLOW)
        radius_label = Tex("Radius", color=YELLOW).next_to(radius_line, UP)
        self.play(Create(radius_line), Write(radius_label))
        self.wait(1)

        # State the relationship between diameter and radius
        relation_text = Tex("Diameter = 2 x Radius").to_edge(UP)
        self.play(Write(relation_text))
        self.wait(2)

        # Show the area of the circle
        area_text = Tex("Area = $\\pi$ x Radius$^2$").next_to(relation_text, DOWN)
        self.play(Write(area_text))
        self.wait(2)

        # Substitute radius in terms of diameter
        diameter_area_text = Tex("Area = $\\pi$ x (Diameter/2)$^2$").next_to(area_text, DOWN)
        self.play(Write(diameter_area_text))
        self.wait(2)

        # Simplify
        simplified_area_text = Tex("Area = $\\frac{\\pi}{4}$ x Diameter$^2$").next_to(diameter_area_text, DOWN)
        self.play(Write(simplified_area_text))
        self.wait(3)

        # Example
        example_text = Tex("Example: If Diameter = 4, Area = $\\frac{\\pi}{4}$ x 4$^2$ = 4$\\pi$").to_edge(DOWN)
        self.play(Write(example_text))
        self.wait(3)

        # Fade out everything
        self.play(FadeOut(circle, center_dot, center_label, diameter_line, diameter_label, radius_line, radius_label, relation_text, area_text, diameter_area_text, simplified_area_text, example_text))
        self.wait(1)