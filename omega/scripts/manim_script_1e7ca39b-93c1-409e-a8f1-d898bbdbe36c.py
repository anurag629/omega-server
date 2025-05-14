from manim import *

class LinearRegressionScene(Scene):
    def construct(self):
        # Title
        title = Text("Linear Regression", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_numbers": True},
        )
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")
        self.play(Create(axes), Write(axes_labels))
        self.wait(1)

        # Scatter points (example data)
        points = [
            [1, 2],
            [2, 3],
            [3, 5],
            [4, 4],
            [5, 7],
            [6, 6],
            [7, 8],
            [8, 9],
            [9, 10],
        ]
        dots = VGroup(*[Dot(axes.coords_to_point(x, y), color=BLUE) for x, y in points])
        self.play(FadeIn(dots))
        self.wait(1)

        # Line of best fit
        line = axes.plot(lambda x: 0.9 * x + 1, x_range=[0, 10], color=YELLOW)
        line_label = MathTex("y = 0.9x + 1").next_to(line, UP)
        self.play(Create(line), Write(line_label))
        self.wait(1)

        # Highlighting the concept of minimizing error
        for x, y in points:
            predicted_y = 0.9 * x + 1
            error_line = DashedLine(
                start=axes.coords_to_point(x, y),
                end=axes.coords_to_point(x, predicted_y),
                color=RED,
            )
            self.play(Create(error_line), run_time=0.3)
            self.wait(0.1)
            self.play(FadeOut(error_line))

        # End Scene
        self.wait(2)
        self.play(FadeOut(title, axes, axes_labels, dots, line, line_label))
        self.wait(1)