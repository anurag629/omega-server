from manim import *

class LinearRegressionScene(Scene):
    def construct(self):
        # Title of the Scene
        title = Text("Linear Regression", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait()

        # Axes for the scatterplot
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            x_length=7,
            y_length=5,
            axis_config={"include_numbers": True},
        ).shift(LEFT * 2)
        self.play(Create(axes))

        # Label axes
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y")
        self.play(Write(x_label), Write(y_label))
        self.wait()

        # Create random data points (scatterplot)
        data_points = [
            Dot(axes.c2p(x, y), color=BLUE)
            for x, y in [(1, 2), (2, 3), (3, 5), (4, 4), (5, 6), (6, 7), (7, 8)]
        ]
        self.play(*[FadeIn(dot) for dot in data_points])
        self.wait()

        # Draw the regression line
        regression_line = axes.plot(lambda x: 1.2 * x + 1, color=RED)
        self.play(Create(regression_line))
        self.wait()

        # Add legend for the regression line
        legend = VGroup(
            Dot(color=RED),
            Text("Regression Line", font_size=24).next_to(Dot(color=RED), RIGHT)
        ).next_to(axes, RIGHT)
        self.play(Write(legend))
        self.wait()

        # Highlight key point: prediction example
        prediction_point = axes.c2p(8, 10.6)  # Example prediction
        prediction_dot = Dot(prediction_point, color=YELLOW)
        prediction_label = Text("Prediction", font_size=24, color=YELLOW).next_to(prediction_dot, UP)
        self.play(FadeIn(prediction_dot), Write(prediction_label))
        self.wait()

        # Fade out everything
        self.play(FadeOut(VGroup(title, axes, x_label, y_label, *data_points, regression_line, legend, prediction_dot, prediction_label)))
        self.wait()