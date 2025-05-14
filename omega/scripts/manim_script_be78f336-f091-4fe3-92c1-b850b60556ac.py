from manim import *

class LinearRegressionExample(Scene):
    def construct(self):
        # Set up the axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=8,
            y_length=5,
            axis_config={"include_numbers": True},
        ).add_coordinates()

        axes.to_edge(LEFT)  # Position the axes

        x_label = axes.get_x_axis_label("X", edge=RIGHT, direction=UR)
        y_label = axes.get_y_axis_label("Y", edge=UP, direction=RIGHT)

        labels = VGroup(x_label, y_label)

        self.play(Create(axes), Write(labels))
        self.wait(0.5)

        # Generate some example data points (X, Y)
        data_points = [(1, 2), (2, 3), (3, 3.5), (4, 5), (5, 6), (6, 6.5), (7, 8)]
        dots = VGroup()

        for x, y in data_points:
            dot = Dot(axes.coords_to_point(x, y), color=BLUE, radius=0.08)
            dots.add(dot)

        # Animate the data points appearing
        self.play(Create(dots))
        self.wait(1)

        # Describe linear regression
        linear_regression_text = Tex("Linear Regression: Find the best line to fit the data").to_edge(UP)
        self.play(Write(linear_regression_text))
        self.wait(1)

        # Define a line (y = mx + b)
        m = 0.8  # Slope
        b = 1.2  # Y-intercept

        # Create the line
        line = axes.plot(lambda x: m * x + b, x_range=[0, 10], color=RED)

        # Animate the line appearing
        self.play(Create(line))
        self.wait(1)

        # Show the equation of the line
        equation = MathTex(r"y = mx + b").to_edge(DOWN).shift(UP*0.5)
        m_value = MathTex(f"m = {m:.2f}").next_to(equation, LEFT)
        b_value = MathTex(f"b = {b:.2f}").next_to(equation, RIGHT)
        self.play(Write(equation), Write(m_value), Write(b_value))
        self.wait(2)
        
        #Emphasize that the line minimizes error
        error_text = Tex("Minimize the error between the line and the data points").next_to(equation, DOWN)
        self.play(Write(error_text))
        self.wait(2)
        
        #Draw vertical lines indicating error
        error_lines = VGroup()
        for x, y in data_points:
            y_predicted = m*x + b
            error_line = DashedLine(axes.coords_to_point(x, y), axes.coords_to_point(x, y_predicted), color=YELLOW)
            error_lines.add(error_line)
        
        self.play(Create(error_lines))
        self.wait(2)

        # Clean up
        self.play(FadeOut(axes), FadeOut(dots), FadeOut(line), FadeOut(equation), FadeOut(m_value), FadeOut(b_value), FadeOut(linear_regression_text), FadeOut(error_text), FadeOut(error_lines), FadeOut(labels))
        self.wait(1)