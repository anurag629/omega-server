from manim import *

class LinearRegression(Scene):
    def construct(self):
        # Define axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=7,
            y_length=5,
            axis_config={"include_numbers": True},
        )
        axes.move_to(LEFT * 3)
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y")
        labels = VGroup(x_label, y_label)

        # Create data points
        data_points = [
            (1, 2),
            (2, 3),
            (3, 5),
            (4, 6),
            (5, 5),
            (6, 7),
            (7, 8),
            (8, 9),
            (9, 8),
        ]
        dots = VGroup(*[
            Dot(axes.coords_to_point(x, y), color=BLUE, radius=0.08)
            for x, y in data_points
        ])

        # Create initial line
        initial_slope = 0.5
        initial_intercept = 1
        line = axes.plot(
            lambda x: initial_slope * x + initial_intercept,
            x_range=[0, 10],
            color=GREEN,
        )
        line_label = MathTex(r"y = 0.5x + 1", color=GREEN)
        line_label.next_to(line, UP)

        # Show the objects
        self.play(Create(axes), Write(labels))
        self.play(Create(dots), run_time=2)
        self.play(Create(line), Write(line_label))
        self.wait(1)

        # Define a function to calculate the error
        def calculate_error(slope, intercept):
            error = 0
            for x, y in data_points:
                error += (slope * x + intercept - y) ** 2
            return error

        # Demonstrate adjusting the line
        new_slope = 0.8
        new_intercept = 0.5
        new_line = axes.plot(
            lambda x: new_slope * x + new_intercept,
            x_range=[0, 10],
            color=RED,
        )
        new_line_label = MathTex(r"y = 0.8x + 0.5", color=RED)
        new_line_label.next_to(new_line, UP)

        self.play(
            Transform(line, new_line),
            Transform(line_label, new_line_label),
        )
        self.wait(1)

        # Briefly explain the error calculation
        error_text = Text("Error = Sum of squared differences", font_size=24)
        error_text.to_edge(DOWN)
        self.play(Write(error_text))
        self.wait(1)
        self.play(FadeOut(error_text))

        # Simulate iterative improvement - more steps are possible
        final_slope = 0.7
        final_intercept = 1.2
        final_line = axes.plot(
            lambda x: final_slope * x + final_intercept,
            x_range=[0, 10],
            color=YELLOW,
        )
        final_line_label = MathTex(r"y = 0.7x + 1.2", color=YELLOW)
        final_line_label.next_to(final_line, UP)

        self.play(
            Transform(line, final_line),
            Transform(line_label, final_line_label),
        )
        self.wait(2)

        # Final Explanation
        explanation = Text("Linear Regression: Finding the best fit line", font_size=36)
        explanation.move_to(RIGHT * 3)
        self.play(Write(explanation))
        self.wait(3)

        # Fade out everything
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        self.wait(1)