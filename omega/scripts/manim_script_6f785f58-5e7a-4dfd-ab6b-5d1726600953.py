from manim import *

class LinearRegression(Scene):
    def construct(self):
        # Create the axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_numbers": True, "include_tip": False},
        )
        axes.add_coordinate_labels()
        self.play(Create(axes), run_time=2)
        self.wait(0.5)

        # Create a set of data points
        data_points = [
            (1, 2),
            (2, 3),
            (3, 5),
            (4, 4),
            (5, 6),
            (6, 7),
            (7, 8),
            (8, 9),
            (9, 8)
        ]

        dots = VGroup(*[
            Dot(axes.coords_to_point(x, y), color=BLUE, radius=0.08)
            for x, y in data_points
        ])
        self.play(Create(dots), run_time=2)
        self.wait(0.5)

        # Create a regression line (initial guess)
        line = Line(axes.coords_to_point(0, 1), axes.coords_to_point(10, 9), color=RED)
        self.play(Create(line), run_time=2)
        self.wait(0.5)

        # Add a label for the line
        line_label = MathTex("y = mx + b").next_to(line, UP, buff=0.2)
        self.play(Write(line_label))
        self.wait(1)

        # Illustrate the concept of error (vertical distance from points to line)
        error_lines = VGroup()
        for x, y in data_points:
            point = axes.coords_to_point(x, y)
            line_y = line.point_from_proportion(x/10)[1]
            error_point = [point[0], line_y, point[2]]
            error_line = DashedLine(point, error_point, color=YELLOW)
            error_lines.add(error_line)

        self.play(Create(error_lines), run_time=2)
        self.wait(0.5)

        # Highlight one error line with an arrow and label
        first_error_line = error_lines[0]
        error_arrow = Arrow(first_error_line.get_start(), first_error_line.get_end(), buff=0.1, color=YELLOW)
        error_label = MathTex("\text{Error}").next_to(error_arrow, RIGHT, buff=0.1).scale(0.7)

        self.play(Create(error_arrow), Write(error_label))
        self.wait(1)
        self.play(FadeOut(error_arrow), FadeOut(error_label))

        # Transition to a better regression line (after optimization)
        better_line = Line(axes.coords_to_point(0, 1.5), axes.coords_to_point(10, 8.5), color=GREEN)

        self.play(
            Transform(line, better_line),
            Transform(line_label, MathTex("y = 0.7x + 1.5").next_to(better_line, UP, buff=0.2))
        )
        self.wait(1)

        # Show that the errors are smaller with the better line
        new_error_lines = VGroup()
        for x, y in data_points:
            point = axes.coords_to_point(x, y)
            line_y = better_line.point_from_proportion(x/10)[1]
            error_point = [point[0], line_y, point[2]]
            error_line = DashedLine(point, error_point, color=YELLOW)
            new_error_lines.add(error_line)

        self.play(Transform(error_lines, new_error_lines), run_time=2)
        self.wait(1)

        # Briefly state the goal of linear regression
        goal_text = Text("Goal: Minimize the sum of squared errors").to_edge(DOWN)
        self.play(Write(goal_text))
        self.wait(2)

        # Clean up
        self.play(FadeOut(axes, dots, line, line_label, error_lines, goal_text))
        self.wait(1)