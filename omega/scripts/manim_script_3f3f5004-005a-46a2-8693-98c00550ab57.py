from manim import *

class CircleAreaDiameterRelation(Scene):
    def construct(self):
        # Introduction: State the objective
        intro_text = Tex("Relationship between Area and Diameter of a Circle")
        self.play(Write(intro_text))
        self.wait(2)
        self.play(FadeOut(intro_text))

        # Create a circle
        circle = Circle(radius=2, color=BLUE)
        self.play(Create(circle))

        # Label the radius and diameter
        radius_line = Line(circle.get_center(), circle.get_center() + RIGHT * 2, color=YELLOW)
        radius_label = Tex("r").next_to(radius_line, UP)
        diameter_line = Line(circle.get_center() + LEFT * 2, circle.get_center() + RIGHT * 2, color=RED)
        diameter_label = Tex("d").next_to(diameter_line, DOWN)
        self.play(Create(radius_line), Write(radius_label))
        self.wait(1)
        self.play(Create(diameter_line), Write(diameter_label))
        self.wait(1)

        # Show the relationship between radius and diameter (d = 2r)
        diameter_equals_2r = Tex("d = 2r").to_edge(UP)
        self.play(Write(diameter_equals_2r))
        self.wait(2)

        # Fade out radius and diameter labels, keep the lines
        self.play(FadeOut(radius_label, diameter_label))

        # Mention the formula for the area of the circle
        area_formula = Tex("Area = $\\pi r^2$").next_to(diameter_equals_2r, DOWN)
        self.play(Write(area_formula))
        self.wait(2)

        # Substitute r = d/2 into the area formula
        substitution_text = Tex("Area = $\\pi (\\frac{d}{2})^2$").next_to(area_formula, DOWN)
        self.play(Write(substitution_text))
        self.wait(2)

        # Simplify the expression
        simplified_area_formula = Tex("Area = $\\pi \\frac{d^2}{4}$").next_to(substitution_text, DOWN)
        self.play(Write(simplified_area_formula))
        self.wait(2)

        # Highlight the key takeaway: Area is proportional to d^2
        proportional_relation = Tex("Area $\\propto$ $d^2$").next_to(simplified_area_formula, DOWN)
        self.play(Write(proportional_relation))
        self.wait(3)

        # Fade out all text and lines except the circle
        self.play(FadeOut(diameter_equals_2r, area_formula, substitution_text, simplified_area_formula, proportional_relation, diameter_line, radius_line))
        self.wait(1)
        
        # Scale the circle and show the area change in relation to the diameter
        circle_copy = circle.copy()
        circle_copy.move_to(DOWN * 2)
        circle_copy.scale(2)
        
        self.play(Transform(circle, circle_copy))

        # Add Text to Explain the Circle Scale
        double_diameter_text = Tex("Diameter Doubled").move_to(UP*2)
        four_times_area_text = Tex("Area Quadrupled").move_to(UP*3)

        self.play(Write(double_diameter_text), Write(four_times_area_text))

        self.wait(3)

        self.play(FadeOut(circle, double_diameter_text, four_times_area_text))

        # End Screen
        end_text = Tex("Therefore, Area is proportional to the square of the Diameter.").scale(0.8)
        self.play(Write(end_text))

        self.wait(3)
        self.play(FadeOut(end_text))

        self.wait(1)