from manim import *

class CircleAreaDiameterRelation(Scene):
    def construct(self):
        # Create a circle
        circle = Circle(radius=2, color=BLUE)
        self.play(Create(circle), run_time=2)
        self.wait(0.5)

        # Show the radius
        radius_line = Line(circle.get_center(), circle.get_center() + RIGHT * 2, color=YELLOW)
        radius_label = MathTex("r", color=YELLOW).next_to(radius_line, UP)
        self.play(Create(radius_line), Write(radius_label), run_time=1.5)
        self.wait(0.5)

        # Show the diameter
        diameter_line = Line(circle.get_center() + LEFT * 2, circle.get_center() + RIGHT * 2, color=GREEN)
        diameter_label = MathTex("d = 2r", color=GREEN).next_to(diameter_line, DOWN)
        self.play(Create(diameter_line), Write(diameter_label), run_time=1.5)
        self.wait(0.5)

        # Area formula
        area_formula = MathTex("A = \\pi r^2").to_edge(UP)
        self.play(Write(area_formula), run_time=2)
        self.wait(0.5)

        # Replace radius with diameter
        area_formula_diameter = MathTex("A = \\pi (\\frac{d}{2})^2").next_to(area_formula, DOWN)
        self.play(TransformMatchingTex(area_formula.copy(), area_formula_diameter), run_time=2)
        self.wait(0.5)

        # Simplify the formula
        simplified_formula = MathTex("A = \\frac{\\pi}{4} d^2").next_to(area_formula_diameter, DOWN)
        self.play(TransformMatchingTex(area_formula_diameter.copy(), simplified_formula), run_time=2)
        self.wait(1)

        # Highlight the relationship
        frame = SurroundingRectangle(simplified_formula, color=RED)
        self.play(Create(frame))
        self.wait(2)

        # Remove everything
        self.play(FadeOut(circle, radius_line, radius_label, diameter_line, diameter_label, area_formula, area_formula_diameter, simplified_formula, frame))
        self.wait(1)