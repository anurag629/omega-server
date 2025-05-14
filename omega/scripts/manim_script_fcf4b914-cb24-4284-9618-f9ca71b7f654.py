from manim import *

class LinearRegression(Scene):
    def construct(self):
        # Set up the axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=8,
            y_length=5,
            axis_config={"include_numbers": True}
        )
        axes.move_to(LEFT * 2)
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y")

        self.play(Create(axes), Write(x_label), Write(y_label))
        self.wait(1)

        # Generate some data points (scatter plot)
        num_points = 10
        x_coords = np.random.uniform(1, 9, num_points)
        y_coords = 0.8 * x_coords + np.random.normal(0, 1.5, num_points) + 1 # Introduce some noise

        points = [Dot(axes.coords_to_point(x, y), color=BLUE) for x, y in zip(x_coords, y_coords)]
        self.play(*[Create(point) for point in points])
        self.wait(1)

        # Fit a line (using a simple equation for demonstration)
        slope = 0.8
        intercept = 1
        line = axes.plot(lambda x: slope * x + intercept, x_range=[0, 10], color=RED)

        self.play(Create(line))
        self.wait(1)

        # Display the equation of the line
        equation = MathTex(r"y = mx + b", color=YELLOW)
        equation.to_edge(UP)
        self.play(Write(equation))
        self.wait(1)

        # Show the values of m and b
        slope_val = MathTex(r"m = " + str(slope), color=GREEN)
        intercept_val = MathTex(r"b = " + str(intercept), color=GREEN)
        slope_val.next_to(equation, DOWN)
        intercept_val.next_to(slope_val, DOWN)

        self.play(Write(slope_val), Write(intercept_val))
        self.wait(2)

        # Illustrate the concept of minimizing errors (optional)
        # For simplicity, let's just highlight one point and show its vertical distance to the line

        # Select a point
        point_index = 3  # arbitrary index
        selected_point = points[point_index]
        x_coord = x_coords[point_index]
        y_coord = y_coords[point_index]

        # Calculate the predicted y-value on the line
        predicted_y = slope * x_coord + intercept

        # Create a vertical line showing the error
        error_line = axes.plot(lambda x: x, x_range=[x_coord, x_coord], y_range=[predicted_y, y_coord], color=PURPLE, stroke_width=3)
        self.play(Create(error_line))
        self.wait(1)

        error_label = MathTex(r"\text{Error}", color=PURPLE)
        error_label.next_to(error_line, RIGHT)
        self.play(Write(error_label))
        self.wait(2)


        # Clean up the scene
        self.play(FadeOut(axes), FadeOut(*points), FadeOut(line), FadeOut(equation), FadeOut(slope_val), FadeOut(intercept_val), FadeOut(error_line), FadeOut(error_label), FadeOut(x_label), FadeOut(y_label))
        self.wait(1)