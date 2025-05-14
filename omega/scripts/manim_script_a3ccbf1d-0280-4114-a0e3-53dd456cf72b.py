from manim import *

class LinearRegression(Scene):
    def construct(self):
        # 1. Define axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_numbers": True}
        )
        axes.add_coordinate_labels()
        axes.to_edge(LEFT)
        self.play(Create(axes), run_time=2)

        # 2. Create data points
        data_points = [
            (1, 2), (2, 3), (3, 3.5), (4, 5), (5, 5.5),
            (6, 7), (7, 6.5), (8, 8), (9, 7.5)
        ]
        dots = VGroup(*[
            Dot(axes.coords_to_point(x, y), color=BLUE, radius=0.08)
            for x, y in data_points
        ])
        self.play(Create(dots), run_time=2)

        # 3. Define the linear regression line (initial guess)
        slope = 0.5
        intercept = 1
        line = axes.plot(lambda x: slope * x + intercept, color=RED)
        self.play(Create(line), run_time=2)

        # 4. Add labels
        title = Tex("Linear Regression").to_edge(UP)
        self.play(Write(title))

        slope_label = Tex(f"Slope: {slope:.2f}").to_corner(DR)
        intercept_label = Tex(f"Intercept: {intercept:.2f}").next_to(slope_label, UP)
        self.play(Write(slope_label), Write(intercept_label))

        # 5. Introduce the concept of error
        error_lines = VGroup()
        for x, y in data_points:
            predicted_y = slope * x + intercept
            error = y - predicted_y
            error_line = Line(
                axes.coords_to_point(x, y),
                axes.coords_to_point(x, predicted_y),
                color=YELLOW
            )
            error_lines.add(error_line)

        self.play(Create(error_lines), run_time=2)
        self.wait(1)
        self.play(Uncreate(error_lines), run_time=1)

        # 6. Simulate optimization (adjust slope and intercept)
        new_slope = 0.8
        new_intercept = 1.5
        new_line = axes.plot(lambda x: new_slope * x + new_intercept, color=GREEN)

        self.play(
            Transform(line, new_line),
            slope_label.animate.become(Tex(f"Slope: {new_slope:.2f}").to_corner(DR)),
            intercept_label.animate.become(Tex(f"Intercept: {new_intercept:.2f}").next_to(slope_label, UP)),
            run_time=3
        )

        # 7. Highlight the new errors
        error_lines_new = VGroup()
        for x, y in data_points:
            predicted_y = new_slope * x + new_intercept
            error = y - predicted_y
            error_line = Line(
                axes.coords_to_point(x, y),
                axes.coords_to_point(x, predicted_y),
                color=YELLOW
            )
            error_lines_new.add(error_line)

        self.play(Create(error_lines_new), run_time=2)
        self.wait(2)

        # 8. Clean up
        self.play(
            Uncreate(axes),
            Uncreate(dots),
            Uncreate(line),
            Uncreate(error_lines_new),
            Unwrite(title),
            Unwrite(slope_label),
            Unwrite(intercept_label),
            run_time=2
        )
        self.wait(1)