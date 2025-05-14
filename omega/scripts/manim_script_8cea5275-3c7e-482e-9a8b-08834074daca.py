from manim import *

class LinearRegressionScene(Scene):
    def construct(self):
        # Title
        title = Text("Linear Regression", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Axes for the plot
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_tip": True, "numbers_to_exclude": [0]}
        ).scale(0.8)
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")
        self.play(Create(axes), Write(axes_labels))
        self.wait(1)

        # Points for the dataset
        points = [
            Dot(axes.c2p(1, 2), color=BLUE),
            Dot(axes.c2p(2, 3), color=BLUE),
            Dot(axes.c2p(3, 5), color=BLUE),
            Dot(axes.c2p(4, 4), color=BLUE),
            Dot(axes.c2p(5, 6), color=BLUE),
            Dot(axes.c2p(6, 7), color=BLUE),
            Dot(axes.c2p(7, 8), color=BLUE),
            Dot(axes.c2p(8, 8.5), color=BLUE),
            Dot(axes.c2p(9, 9), color=BLUE),
        ]
        group_points = VGroup(*points)
        self.play(FadeIn(group_points))
        self.wait(1)

        # Displaying a line for linear regression
        regression_line = axes.plot(lambda x: 0.8 * x + 1.5, x_range=[0, 10], color=RED)
        self.play(Create(regression_line))
        self.wait(1)

        # Add label for the regression line
        regression_label = MathTex("y = 0.8x + 1.5", color=RED).next_to(regression_line, UP)
        self.play(Write(regression_label))
        self.wait(1)

        # Explanation for the linear regression concept
        explanation = Text(
            "Linear Regression finds the best-fit line for data points.",
            font_size=28
        ).next_to(axes, DOWN)
        self.play(Write(explanation))
        self.wait(2)

        # Fade out everything
        self.play(FadeOut(title, axes, axes_labels, group_points, regression_line, regression_label, explanation))
        self.wait(1)