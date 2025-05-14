from manim import *

class LinearRegression(Scene):
    def construct(self):
        # Define axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=6,
            y_length=6,
            axis_config={"include_numbers": True},
        )
        axes.move_to(LEFT * 3)
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")

        # Create data points
        data_points = [
            (1, 2),
            (2, 3),
            (3, 3.5),
            (4, 5),
            (5, 4.5),
            (6, 7),
            (7, 6.5),
            (8, 8),
            (9, 7.5),
        ]

        dots = VGroup()
        for x, y in data_points:
            dot = Dot(axes.coords_to_point(x, y), color=BLUE, radius=0.08)
            dots.add(dot)

        # Initial guess for the line
        slope = ValueTracker(0.5)
        intercept = ValueTracker(1)

        # Define the line function
        def linear_function():
            return lambda x: slope.get_value() * x + intercept.get_value()

        # Create the line
        line = always_redraw(lambda: axes.plot(linear_function(), color=RED, x_range=[0,10]))

        # Display slope and intercept values
        slope_text = always_redraw(lambda: Tex(f"Slope = {slope.get_value():.2f}").next_to(axes, UP, buff=0.2))
        intercept_text = always_redraw(lambda: Tex(f"Intercept = {intercept.get_value():.2f}").next_to(slope_text, RIGHT, buff=0.5))


        # Group the axes and labels for easier manipulation
        axes_group = VGroup(axes, axes_labels)

        # Introduction animation
        self.play(Create(axes_group), Write(dots))
        self.wait(1)
        self.play(Create(line), Write(slope_text), Write(intercept_text))
        self.wait(1)

        # Adjust slope and intercept
        self.play(
            slope.animate.set_value(1.0),
            intercept.animate.set_value(0.5),
            run_time=3
        )
        self.wait(1)

        self.play(
            slope.animate.set_value(0.8),
            intercept.animate.set_value(1.2),
            run_time=3
        )
        self.wait(1)

        # Show cost function (Simplified - just some text)
        cost_function_text = Tex("Cost Function: Minimize the distance from points to the line").move_to(RIGHT * 4)
        self.play(Write(cost_function_text))
        self.wait(2)

        # Final adjustments
        self.play(
            slope.animate.set_value(0.75),
            intercept.animate.set_value(1.5),
            run_time=3
        )

        # Fade out and end
        self.wait(2)
        self.play(FadeOut(axes_group, dots, line, slope_text, intercept_text, cost_function_text))
        self.wait(1)