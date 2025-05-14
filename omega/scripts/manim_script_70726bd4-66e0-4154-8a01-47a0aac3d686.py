from manim import *

class LinearRegression(Scene):
    def construct(self):
        # Set up the axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"include_numbers": True}
        )
        axes.add_coordinate_labels()
        axes.move_to(LEFT * 2)

        # Create random data points
        num_points = 10
        points = []
        for _ in range(num_points):
            x = np.random.uniform(1, 9)
            y = 0.7 * x + 1 + np.random.normal(0, 1)  # Simulate data with noise
            points.append(Dot(axes.coords_to_point(x, y), color=BLUE, radius=0.05))

        # Create a VGroup to hold the data points
        data_points = VGroup(*points)

        # Show the axes and data points
        self.play(Create(axes), Create(data_points))
        self.wait(1)

        # Initial guess for the regression line
        slope = ValueTracker(0.5)
        intercept = ValueTracker(0)

        # Define the regression line
        def update_regression_line(line):
            new_slope = slope.get_value()
            new_intercept = intercept.get_value()
            line.become(
                axes.plot(lambda x: new_slope * x + new_intercept, x_range=[0, 10], color=RED)
            )
        
        regression_line = axes.plot(lambda x: slope.get_value() * x + intercept.get_value(), x_range=[0, 10], color=RED)
        regression_line.add_updater(update_regression_line)

        # Display the regression line
        self.play(Create(regression_line))
        self.wait(1)

        # Animate the slope and intercept to improve the fit
        self.play(
            slope.animate.set_value(0.7),
            intercept.animate.set_value(1),
            run_time=3
        )
        self.wait(2)
        
        #Display the equation
        equation = MathTex(r"y = mx + b")
        equation.move_to(RIGHT * 3)

        slope_value = DecimalNumber(slope.get_value(), num_decimal_places=2)
        intercept_value = DecimalNumber(intercept.get_value(), num_decimal_places=2)
        
        slope_label = MathTex("m = ").next_to(equation, DOWN)
        slope_label.shift(LEFT*1)
        intercept_label = MathTex("b = ").next_to(slope_label, DOWN)
        intercept_label.shift(LEFT*1)

        slope_value.next_to(slope_label, RIGHT)
        intercept_value.next_to(intercept_label, RIGHT)

        self.play(Write(equation),Write(slope_label), Write(intercept_label))
        self.play(Write(slope_value),Write(intercept_value))

        #Update decimal number
        slope_value.add_updater(lambda d: d.set_value(slope.get_value()))
        intercept_value.add_updater(lambda d: d.set_value(intercept.get_value()))
        
        self.play(
            slope.animate.set_value(0.6),
            intercept.animate.set_value(1.2),
            run_time=3
        )

        # Clean up and end
        self.wait(2)
        self.play(FadeOut(axes, data_points, regression_line, equation, slope_label, intercept_label, slope_value, intercept_value))
        self.wait(1)