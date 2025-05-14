from manim import *

class CircleToPoint(Scene):
    def construct(self):
        # Create a circle
        circle = Circle(radius=2, color=BLUE)
        self.play(Create(circle))
        self.wait(1)

        # Create multiple lines that approximate the circle
        num_lines = 10
        lines = VGroup()
        for i in range(num_lines):
            angle1 = i * 2 * PI / num_lines
            angle2 = (i + 1) * 2 * PI / num_lines
            start_point = circle.point_at_angle(angle1)
            end_point = circle.point_at_angle(angle2)
            line = Line(start_point, end_point)
            lines.add(line)

        # Transform the circle into lines
        self.play(Transform(circle, lines))
        self.wait(1)

        # Gradually shorten the lines
        num_shortening_steps = 5
        for i in range(num_shortening_steps):
            shortened_lines = VGroup()
            shortening_factor = 1 - (i + 1) / num_shortening_steps
            for line in lines:
                new_line = Line(line.get_start(), line.get_end())
                new_line.scale(shortening_factor, about_point=line.get_center())
                shortened_lines.add(new_line)
            self.play(Transform(lines, shortened_lines), run_time=0.5)
            lines = shortened_lines # Update lines for the next iteration
        self.wait(1)

        # Transform the lines into a single point
        point = Dot(lines.get_center(), color=RED)
        self.play(Transform(lines, point))
        self.wait(1)

        self.play(FadeOut(point)) # Optional fade out
        self.wait(1)