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
            axis_config={"include_tip": True, "numbers_to_exclude": []},
        )
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")
        self.play(Create(axes), Write(axes_labels))
        self.wait(1)

        # Scatter points
        data_points = [
            (1, 2),
            (2, 3),
            (3, 5),
            (4, 4),
            (5, 6),
            (6, 7),
            (7, 8),
            (8, 8.5),
            (9, 9),
        ]
        dots = VGroup(*[Dot(axes.coords_to_point(x, y), color=BLUE) for x, y in data_points])
        self.play(FadeIn(dots))
        self.wait(1)

        # Line of best fit (linear regression line)
        regression_line = axes.plot(lambda x: 0.9 * x + 1, color=YELLOW)
        regression_label = MathTex("y = 0.9x + 1").next_to(regression_line, UP, buff=0.5)
        self.play(Create(regression_line), Write(regression_label))
        self.wait(1)

        # Highlight a prediction
        x_value = 7.5
        y_value = 0.9 * x_value + 1
        prediction_dot = Dot(axes.coords_to_point(x_value, y_value), color=RED)
        prediction_label = MathTex(f"({x_value:.1f}, {y_value:.1f})").next_to(prediction_dot, RIGHT)
        self.play(FadeIn(prediction_dot), Write(prediction_label))
        self.wait(2)

        # End animation
        self.play(FadeOut(VGroup(title, axes, axes_labels, dots, regression_line, regression_label, prediction_dot, prediction_label)))
        self.wait(1)