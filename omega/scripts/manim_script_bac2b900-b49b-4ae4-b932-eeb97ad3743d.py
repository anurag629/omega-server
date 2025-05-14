from manim import *

class LinearRegressionScene(Scene):
    def construct(self):
        # Define axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=6,
            y_length=6,
            axis_config={"include_numbers": True}
        )
        axes.move_to(LEFT * 3)
        self.play(Create(axes), run_time=2)
        self.wait(0.5)

        # Generate some sample data points
        data_points = [
            [1, 2],
            [2, 3],
            [3, 3.5],
            [4, 5],
            [5, 6],
            [6, 6.5],
            [7, 8],
            [8, 7],
            [9, 8.5]
        ]

        dots = VGroup()
        for x, y in data_points:
            dot = Dot(axes.coords_to_point(x, y), color=BLUE, radius=0.08)
            dots.add(dot)

        # Animate the appearance of the data points
        self.play(Create(dots), run_time=2)
        self.wait(0.5)

        # Define a function for the linear regression line (initial guess)
        def linear_function(x):
            return 0.5 * x + 1.5

        # Create the initial linear regression line
        line = axes.plot(linear_function, x_range=[0, 10], color=RED)

        # Animate the appearance of the initial line
        self.play(Create(line), run_time=2)
        self.wait(0.5)

        # Add a label for the line
        line_label = Tex("Initial Guess", color=RED).next_to(line, RIGHT)
        self.play(Create(line_label))
        self.wait(0.5)

        # Define a new, better linear function
        def better_linear_function(x):
            return 0.8 * x + 1

        # Create a new, better linear regression line
        better_line = axes.plot(better_linear_function, x_range=[0, 10], color=GREEN)

        # Add a label for the better line
        better_line_label = Tex("Better Fit", color=GREEN).next_to(better_line, RIGHT)
        
        # Animate the transformation from the initial line to the better line
        self.play(
            Transform(line, better_line),
            Transform(line_label, better_line_label),
            run_time=2
        )
        self.wait(0.5)

        # Show the concept of minimizing error (optional - illustrative lines)
        for x, y in data_points:
            predicted_y = better_linear_function(x)
            error_line = Line(
                axes.coords_to_point(x, y),
                axes.coords_to_point(x, predicted_y),
                color=YELLOW,
                stroke_width=2
            )
            self.play(Create(error_line), run_time=0.5)
            self.wait(0.1)
            self.play(FadeOut(error_line), run_time=0.2)

        self.wait(1)

        # Final Fade out
        self.play(FadeOut(axes, dots, line, line_label), run_time=1)
        self.wait(1)