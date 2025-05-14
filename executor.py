from flask import Flask, request, jsonify
import subprocess
import os
import logging
import tempfile
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route("/")
def home():
    return "Manim Executor Service"

def clean_script(script_path):
    """Check and clean script file if needed"""
    try:
        with open(script_path, "r") as f:
            content = f.read()
            
        if "```python" in content or "```" in content:
            logger.info(f"Cleaning script file: {script_path}")
            cleaned_content = content.replace("```python", "").replace("```", "").strip()
            
            with open(script_path, "w") as f:
                f.write(cleaned_content)
            logger.info("Script cleaned")
            
        return True
    except Exception as e:
        logger.error(f"Error cleaning script: {e}")
        return False

@app.route("/execute-manim", methods=["POST"])
def execute_manim():
    data = request.get_json()
    script_path = data.get("script_path")
    scene_class = data.get("scene_class")
    
    logger.info(f"Received request to execute {script_path} with scene {scene_class}")
    
    if not script_path or not scene_class:
        return jsonify({"success": False, "error": "Missing script_path or scene_class"}), 400
    
    try:
        # Make sure script exists
        if not os.path.exists(script_path):
            return jsonify({"success": False, "error": f"Script file not found: {script_path}"}), 404
            
        # Log file contents for debugging
        with open(script_path, "r") as f:
            script_content = f.read()
        logger.info(f"Script contents:\n{script_content}")
        
        # Clean script if needed
        clean_script(script_path)
        
        # Create a temporary file for output capture
        with tempfile.NamedTemporaryFile(prefix="manim_output_", suffix=".txt") as output_file:
            # Execute manim command with error redirection
            logger.info(f"Executing manim {script_path} {scene_class} -qm")
            cmd = f"cd /manim && manim {script_path} {scene_class} -qm 2>&1 | tee {output_file.name}"
            process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Read output from file to ensure we capture everything
            with open(output_file.name, "r") as f:
                complete_output = f.read()
        
        logger.info(f"Command output:\n{complete_output}")
        
        # Get base filename without extension
        base_name = os.path.splitext(os.path.basename(script_path))[0]
        output_path = f"videos/{base_name}/720p30/{scene_class}.mp4"
        full_output_path = os.path.join("/manim/media", output_path)
        
        # Check if output file exists
        success = process.returncode == 0 and os.path.exists(full_output_path)
        
        if not success:
            # Try to extract more detailed error information
            error_info = complete_output
            if "TypeError: " in complete_output:
                # Extract TypeError and related lines for improved debugging
                error_lines = []
                for line in complete_output.split("\n"):
                    if "TypeError: " in line or "❱" in line:
                        error_lines.append(line)
                    # Also capture stack frames for context
                    if "/manim/" in line and ".py" in line and "in" in line:
                        error_lines.append(line)
                if error_lines:
                    error_info = "\n".join(error_lines)
            
            logger.error(f"Manim execution failed with error: {error_info}")
            return jsonify({
                "success": False,
                "error": error_info,
                "output": complete_output
            })
        
        # Check output file
        if os.path.exists(full_output_path):
            logger.info(f"Output file created: {full_output_path}")
        else:
            logger.warning(f"Output file not found at: {full_output_path}")
            # Try to find the file by listing directory contents
            media_dir = f"/manim/media/videos/{base_name}/720p30/"
            if os.path.exists(media_dir):
                files = os.listdir(media_dir)
                logger.info(f"Files in output directory: {files}")
                if files:  # Use first file if any exist
                    output_path = f"videos/{base_name}/720p30/{files[0]}"
        
        return jsonify({
            "success": True,
            "output": complete_output,
            "output_path": output_path
        })
    except Exception as e:
        error_msg = str(e)
        stack_trace = traceback.format_exc()
        logger.error(f"Error executing script: {error_msg}\n{stack_trace}")
        return jsonify({
            "success": False, 
            "error": f"{error_msg}\n{stack_trace}"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001) 