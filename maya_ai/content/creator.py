# maya_ai/content/creator.py

import moviepy.editor as mpy
import requests
import os
from PIL import Image

class VideoCreator:
    """
    Creates an engaging, short-form video from a piece of content and a generated reaction.
    """
    def __init__(self, assets_path="maya_ai/assets", output_path="maya_ai/generated_videos"):
        self.assets_path = assets_path
        self.output_path = output_path
        # Ensure output directory exists
        os.makedirs(self.output_path, exist_ok=True)
        print("Video Creator initialized.")

    def _download_image(self, url, filename="content_image.jpg"):
        """Downloads an image from a URL and saves it locally."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            filepath = os.path.join(self.output_path, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filepath
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {e}")
            return None

    def _resize_image_to_fit(self, image_path, target_width, target_height):
        """Resizes an image to fit within the target dimensions while maintaining aspect ratio."""
        with Image.open(image_path) as img:
            img.thumbnail((target_width, target_height))
            # Create a new blank image with the target dimensions
            new_img = Image.new("RGB", (target_width, target_height), "black")
            # Paste the resized image onto the center of the blank image
            paste_x = (target_width - img.width) // 2
            paste_y = (target_height - img.height) // 2
            new_img.paste(img, (paste_x, paste_y))

            resized_path = os.path.join(self.output_path, "resized_" + os.path.basename(image_path))
            new_img.save(resized_path)
            return resized_path

    def create_video(self, content_data: dict, reaction_audio_path: str, reaction_text: str):
        """
        Generates a complete video from the provided content and reaction.

        Args:
            content_data (dict): The dictionary of content details.
            reaction_audio_path (str): The file path to the reaction audio.
            reaction_text (str): The text of the reaction for captions.

        Returns:
            str: The file path to the final video, or None if failed.
        """
        print("Starting video creation process...")

        # --- 1. Prepare Assets ---
        # Download the content image
        content_image_path = self._download_image(content_data['url'])
        if not content_image_path:
            return None

        # Load the audio reaction
        audio_clip = mpy.AudioFileClip(reaction_audio_path)
        video_duration = audio_clip.duration

        if video_duration > 60:
            print("Warning: Audio duration is over 60 seconds. Trimming.")
            audio_clip = audio_clip.subclip(0, 59.9)
            video_duration = 59.9

        # Video dimensions for Shorts/TikTok
        WIDTH, HEIGHT = 1080, 1920

        # Resize content image to fit the top part of the screen
        resized_content_image_path = self._resize_image_to_fit(content_image_path, WIDTH, HEIGHT // 2)
        content_image_clip = mpy.ImageClip(resized_content_image_path).set_duration(video_duration).set_position(('center', 'top'))

        # --- 2. Create Captions ---
        # Simple caption implementation: one caption for the whole text
        # A more advanced version would sync words to the audio.

        # Font fallback logic
        available_fonts = mpy.TextClip.get_fonts()
        font = 'Impact' if 'Impact' in available_fonts else 'Arial'

        caption_clip = mpy.TextClip(
            reaction_text,
            fontsize=70,
            color='yellow',
            font=font,
            stroke_color='black',
            stroke_width=3,
            method='caption',
            size=(WIDTH * 0.9, None)
        ).set_duration(video_duration).set_position(('center', 0.6), relative=True)

        # --- 3. Create Avatar Overlay (Placeholder) ---
        # TODO: Replace with a real avatar image
        avatar_path = os.path.join(self.assets_path, 'images', 'placeholder_avatar.png')
        if not os.path.exists(avatar_path):
            # Create a simple placeholder if it doesn't exist
            Image.new('RGBA', (250, 250), (255, 0, 255, 128)).save(avatar_path)
            print(f"Created a placeholder avatar at {avatar_path}")

        avatar_clip = mpy.ImageClip(avatar_path).set_duration(video_duration).set_position(('center', 'bottom')).resize(height=250)

        # --- 4. Assemble Video ---
        # Create a base color clip for the background
        background = mpy.ColorClip(size=(WIDTH, HEIGHT), color=(25, 25, 25), duration=video_duration)

        final_video = mpy.CompositeVideoClip([
            background,
            content_image_clip,
            caption_clip,
            avatar_clip
        ])

        # Set the audio for the final video
        final_video = final_video.set_audio(audio_clip)

        # --- 5. Export Video ---
        safe_filename = "".join(x for x in content_data['title'] if x.isalnum())[:20]
        output_filename = f"video_{safe_filename}.mp4"
        output_filepath = os.path.join(self.output_path, output_filename)

        print(f"Exporting final video to {output_filepath}...")
        try:
            # Using a preset that is good for web videos
            final_video.write_videofile(output_filepath, codec='libx264', audio_codec='aac', fps=24)
            print("Video created successfully!")
            return output_filepath
        except Exception as e:
            print(f"Error writing video file: {e}")
            return None

# --- Example Usage ---
if __name__ == '__main__':
    from dotenv import load_dotenv
    from content.scanner import ContentScanner
    from content.reactor import ContentReactor
    from core.brain import MayaPersonaSystem
    from voice.tts_engine import TTSEngine
    load_dotenv()

    print("--- Testing Full Content Creation Pipeline (Scanner -> Reactor -> Creator) ---")

    # Init systems
    scanner = ContentScanner()
    brain = MayaPersonaSystem(model="mistral:latest")
    voice = TTSEngine()
    reactor = ContentReactor(brain, voice)
    creator = VideoCreator()

    # Get content
    meme = scanner.get_reddit_memes(limit=1)
    if meme:
        # Get reaction
        brain.switch_persona('durjana')
        text, audio_path = reactor.generate_reaction(meme[0])
        if text and audio_path:
            # Create video
            video_path = creator.create_video(meme[0], audio_path, text)
            if video_path:
                print(f"\n--- 🎬 Video Generated Successfully! ---")
                print(f"Find your video here: {video_path}")
    else:
        print("Could not find a meme to create a video from.")
