from manim import *

class CircleAreaDiameter(Scene):
    def construct(self):
        # Introduction: State the relationship we're going to explore.
        intro_text = Text("Area of a Circle vs. Diameter", font_size=48)
        self.play(Write(intro_text))
        self.wait(2)
        self.play(FadeOut(intro_text))

        # Create a circle and its diameter
        circle = Circle(radius=2)
        diameter = Line(circle.get_left(), circle.get_right())
        radius_line = Line(circle.get_center(), circle.get_right())
        
        radius_label = MathTex("r", font_size=24).next_to(radius_line, DOWN)
        diameter_label = MathTex("d = 2r", font_size=24).next_to(diameter, DOWN)

        self.play(Create(circle), run_time=2)
        self.play(Create(diameter))
        self.play(Write(diameter_label))
        self.wait(1)
        self.play(Create(radius_line), Write(radius_label))
        self.wait(1)
        
        #Show the Diameter relationship
        self.play(TransformFromCopy(diameter_label, MathTex("d=2r", font_size=48).to_edge(UP)))
        self.wait(1)
        equation = MathTex("d=2r", font_size=48).to_edge(UP)
        self.play(FadeOut(equation))
        
        # Area Formula
        area_formula = MathTex("A = \\pi r^2", font_size=48).to_edge(UP)
        self.play(Write(area_formula))
        self.wait(2)

        # Replace 'r' with 'd/2'
        new_area_formula = MathTex("A = \\pi (\\frac{d}{2})^2", font_size=48).to_edge(UP)
        self.play(ReplacementTransform(area_formula, new_area_formula))
        self.wait(2)

        # Simplify the formula
        simplified_formula = MathTex("A = \\frac{\\pi}{4} d^2", font_size=48).to_edge(UP)
        self.play(ReplacementTransform(new_area_formula, simplified_formula))
        self.wait(2)

        # Highlight the relationship between area and diameter^2
        highlight_text = Text("Area is proportional to d²", font_size=36).to_edge(DOWN)
        self.play(Write(highlight_text))
        self.wait(3)
        
        # Clean up
        self.play(FadeOut(circle, diameter, diameter_label, radius_line, radius_label, simplified_formula, highlight_text))

        # Visual representation
        square = Square(side_length=4) # d = 4
        square.move_to(ORIGIN)
        circle_in_square = Circle(radius=2) # r = 2, d = 4
        circle_in_square.move_to(ORIGIN)

        self.play(Create(square))
        self.play(Create(circle_in_square))

        diameter_line = Line(circle_in_square.get_left(), circle_in_square.get_right())
        self.play(Create(diameter_line))

        diameter_label = MathTex("d", font_size = 24).next_to(diameter_line, DOWN)
        self.play(Write(diameter_label))

        area_formula2 = MathTex("A = \\frac{\\pi}{4} d^2", font_size=48).to_edge(UP)
        self.play(Write(area_formula2))

        square_area = MathTex("d^2", font_size = 24).move_to(square.get_center())
        self.play(Write(square_area))

        self.wait(3)

        self.play(FadeOut(square, circle_in_square, diameter_line, diameter_label, area_formula2, square_area))

        # Conclusion
        conclusion_text = Text("Area of a circle is proportional to the square of its diameter.", font_size=36)
        self.play(Write(conclusion_text))
        self.wait(3)
        self.play(FadeOut(conclusion_text))
        self.wait(1)