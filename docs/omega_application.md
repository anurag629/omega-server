# Omega Application

The Omega application is the core component of the Codercops Omega project, responsible for generating and executing Manim animation scripts using AI providers.

## Overview

The Omega application provides the following features:

- Generate Manim animation scripts from natural language prompts
- Execute the generated scripts to create animations
- Track script generation and execution history
- Provide API endpoints for script generation and management
- Serve generated media files

## Models

### ManimScript

The `ManimScript` model tracks the generation and execution of Manim scripts:

- `id`: UUID primary key
- `user`: Foreign key to user who created the script
- `prompt`: The natural language prompt used to generate the script
- `script`: The actual generated Manim script
- `provider`: AI provider used for generation (Gemini or Azure OpenAI)
- `script_path`: Path to the saved script file
- `output_path`: Path to the output video
- `output_url`: Full URL to access the output video
- `status`: Script execution status (pending, completed, failed)
- `error_message`: Error message if execution failed
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

## Services

The application includes several services:

### Script Generation

The script generation service uses AI providers to generate Manim scripts from user prompts:

- `generate_manim_script(prompt, provider)`: Generates a Manim script using the specified AI provider

### Script Execution

The script execution service runs the generated scripts using Manim to create animations:

- `execute_manim_script(script)`: Executes a Manim script and returns information about the output

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scripts/` | GET | List all scripts created by the current user |
| `/api/scripts/<id>/` | GET | Get details of a specific script |
| `/api/generate/` | POST | Generate a new Manim script |

## How to Use the Omega Application

### Generating a Manim Script

```json
POST /api/generate/
{
  "prompt": "Create an animation showing the Pythagorean theorem",
  "provider": "gemini",
  "execute": true
}
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "script": "from manim import *\n\nclass PythagoreanTheorem(Scene):\n    def construct(self):\n        # Create a right triangle\n        triangle = Polygon(\n            ORIGIN, 3*RIGHT, 3*RIGHT+4*UP,\n            color=WHITE\n        )\n        ...",
  "script_path": "path/to/script.py",
  "output_path": "videos/manim_script_123e4567/720p30/PythagoreanTheorem.mp4",
  "output_url": "http://localhost:8000/media/videos/manim_script_123e4567/720p30/PythagoreanTheorem.mp4"
}
```

### Listing User's Manim Scripts

```
GET /api/scripts/
```

Response:
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "prompt": "Create an animation showing the Pythagorean theorem",
    "script": "from manim import *\n...",
    "provider": "gemini",
    "status": "completed",
    "output_url": "http://localhost:8000/media/videos/manim_script_123e4567/720p30/PythagoreanTheorem.mp4",
    "created_at": "2023-06-01T12:00:00Z"
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "prompt": "Create an animation showing a sine wave",
    "script": "from manim import *\n...",
    "provider": "azure_openai",
    "status": "completed",
    "output_url": "http://localhost:8000/media/videos/manim_script_223e4567/720p30/SineWave.mp4",
    "created_at": "2023-06-02T12:00:00Z"
  }
]
```

### Getting Details of a Specific Script

```
GET /api/scripts/123e4567-e89b-12d3-a456-426614174000/
```

Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "prompt": "Create an animation showing the Pythagorean theorem",
  "script": "from manim import *\n...",
  "provider": "gemini",
  "script_path": "path/to/script.py",
  "output_path": "videos/manim_script_123e4567/720p30/PythagoreanTheorem.mp4",
  "output_url": "http://localhost:8000/media/videos/manim_script_123e4567/720p30/PythagoreanTheorem.mp4",
  "status": "completed",
  "error_message": null,
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-01T12:05:00Z"
}
```

## Working with Manim

### Understanding Manim

Manim is a mathematical animation engine created by Grant Sanderson (3Blue1Brown). It allows you to create precise animations for mathematical and scientific topics.

Key concepts:
- **Scene**: The main container for animations
- **Mobject**: Mathematical objects that can be animated
- **Animation**: Changes to mobjects over time

### Common Manim Patterns

The AI will generate scripts that follow common Manim patterns:

```python
from manim import *

class MyAnimation(Scene):
    def construct(self):
        # Create objects
        circle = Circle()
        square = Square()
        
        # Add objects to the scene
        self.add(circle)
        
        # Animate transformations
        self.play(Transform(circle, square))
        self.wait(1)
```

### Output Resolution

The Manim scripts are executed with 720p30 resolution by default (720p at 30fps).

## Media Storage

Generated animations and images are stored in the media directory:

- Videos: `media/videos/manim_script_{script_id}/720p30/`
- Images: `media/images/manim_script_{script_id}/`

These files can be accessed through the API or directly through the media serving endpoint. 