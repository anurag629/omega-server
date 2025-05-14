from manim import *

class LinearRegressionScene(Scene):
    def construct(self):
        # Title: "Linear Regression"
        title = Text("Linear Regression", font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Create axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_tip": True, "numbers_to_include": range(0, 11)},
        )
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")
        
        self.play(Create(axes), Write(axes_labels))
        self.wait(1)

        # Generate random data points
        points = [
            Dot(axes.c2p(x, y), color=BLUE)
            for x, y in [(1, 2), (2, 4), (3, 5), (4, 4), (5, 6), (6, 7), (7, 8), (8, 9)]
        ]
        
        # Show data points
        self.play(*[FadeIn(point) for point in points])
        self.wait(1)

        # Add a regression line
        regression_line = axes.plot(lambda x: 0.9 * x + 1, color=RED, stroke_width=4)
        regression_label = MathTex("y = 0.9x + 1").next_to(regression_line, UP)

        self.play(Create(regression_line), Write(regression_label))
        self.wait(1)

        # Highlight data points and their proximity to the line
        for point in points:
            x, y = axes.p2c(point.get_center())
            nearest_y = 0.9 * x + 1
            distance_line = DashedLine(
                point.get_center(),
                axes.c2p(x, nearest_y),
                color=YELLOW,
            )
            self.play(Create(distance_line))
            self.wait(0.2)

        self.wait(2)

        # End scene
        self.play(FadeOut(title, axes, axes_labels, regression_line, regression_label, *points))
        self.wait(1)