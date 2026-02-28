import os

class ImageAgent:
    def generate_image(self, text):
        """
        Placeholder for image generation.
        In future, connect DALL·E / Stable Diffusion.
        """
        image_path = "story_image.txt"

        with open(image_path, "w", encoding="utf-8") as f:
            f.write("Image description:\n\n")
            f.write(text[:500])  # short prompt

        os.startfile(image_path)
        return image_path
