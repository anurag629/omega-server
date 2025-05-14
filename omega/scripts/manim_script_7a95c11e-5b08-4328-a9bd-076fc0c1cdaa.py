from manim import *

class LinearRegression(Scene):
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
            axis_config={"include_tip": True, "numbers_to_include": [0, 10]},
        )
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")
        self.play(Create(axes), Write(axes_labels))
        self.wait(1)

        # Scatter Points
        points = [
            Dot(axes.c2p(1, 2), color=BLUE),
            Dot(axes.c2p(2, 3), color=BLUE),
            Dot(axes.c2p(3, 5), color=BLUE),
            Dot(axes.c2p(4, 4), color=BLUE),
            Dot(axes.c2p(5, 7), color=BLUE),
            Dot(axes.c2p(6, 8), color=BLUE),
            Dot(axes.c2p(7, 9), color=BLUE),
        ]
        for point in points:
            self.play(FadeIn(point), run_time=0.3)
        self.wait(1)

        # Line of Best Fit
        line = axes.plot(lambda x: 1.2 * x + 1, x_range=[0, 8], color=RED)
        line_label = MathTex("y = 1.2x + 1").next_to(line, UP, buff=0.5).set_color(RED)
        self.play(Create(line), Write(line_label))
        self.wait(2)

        # Highlight Prediction
        x_value = 6
        predicted_y = 1.2 * x_value + 1
        prediction_dot = Dot(axes.c2p(x_value, predicted_y), color=YELLOW)
        prediction_label = MathTex(f"({x_value}, {predicted_y:.2f})").next_to(prediction_dot, RIGHT)

        self.play(FadeIn(prediction_dot), Write(prediction_label))
        self.wait(2)

        # Fade Out
        self.play(FadeOut(axes), FadeOut(axes_labels), FadeOut(points), FadeOut(line), FadeOut(line_label), FadeOut(prediction_dot), FadeOut(prediction_label), FadeOut(title))
        self.wait(1)