# maya_ai/publishing/youtube.py

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

class YouTubeUploader:
    """
    Handles authentication and video uploading to YouTube.
    """
    def __init__(self, client_secrets_file="client_secrets.json", api_service_name="youtube", api_version="v3"):
        self.client_secrets_file = client_secrets_file
        self.api_service_name = api_service_name
        self.api_version = api_version
        # The user's credentials will be stored here after the first login
        self.credentials_file = "token.pickle"
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]

        self.credentials = self._get_credentials()
        self.youtube_client = self._get_youtube_client() if self.credentials else None

    def _get_credentials(self):
        """
        Gets stored user credentials or runs the OAuth2 flow to get them.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens.
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, "rb") as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.client_secrets_file):
                    print(f"ERROR: '{self.client_secrets_file}' not found.")
                    print("Please download it from the Google Cloud Console and place it in the root directory.")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, self.scopes)
                # This will open a browser window for the user to log in and authorize the app.
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.credentials_file, "wb") as token:
                pickle.dump(creds, token)

        return creds

    def _get_youtube_client(self):
        """Initializes the YouTube API client."""
        if not self.credentials:
            print("Cannot create YouTube client without valid credentials.")
            return None
        return build(self.api_service_name, self.api_version, credentials=self.credentials)

    def upload_video(self, video_path: str, title: str, description: str, tags: list, category_id: str = "24", privacy_status: str = "public"):
        """
        Uploads a video to YouTube.

        Args:
            video_path (str): Path to the video file.
            title (str): The video title.
            description (str): The video description.
            tags (list): A list of tags for the video.
            category_id (str): YouTube category ID. "24" is Entertainment.
            privacy_status (str): "public", "private", or "unlisted".

        Returns:
            str: The ID of the uploaded video, or None if failed.
        """
        if not self.youtube_client:
            print("YouTube client not initialized. Cannot upload.")
            return None

        if not os.path.exists(video_path):
            print(f"Error: Video file not found at '{video_path}'")
            return None

        try:
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": category_id
                },
                "status": {
                    "privacyStatus": privacy_status
                }
            }

            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

            print("Uploading video to YouTube... This may take a while.")
            request = self.youtube_client.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )

            response = request.execute()
            print(f"Video uploaded successfully! Video ID: {response['id']}")
            return response['id']

        except Exception as e:
            print(f"An error occurred during video upload: {e}")
            return None

# --- Example Usage ---
if __name__ == '__main__':
    print("--- Testing YouTube Uploader ---")
    # IMPORTANT: You must have 'client_secrets.json' in your root directory for this to work.
    # The first time you run this, a browser window will open for you to log in.
    uploader = YouTubeUploader()

    if uploader.youtube_client:
        print("\nSuccessfully authenticated with YouTube.")
        # NOTE: This part is commented out to prevent accidental uploads during testing.
        # To test, create a dummy video file named 'test_video.mp4' in the root directory.

        # if os.path.exists("test_video.mp4"):
        #     uploader.upload_video(
        #         video_path="test_video.mp4",
        #         title="Test Upload from Maya AI",
        #         description="This is a test video uploaded by Jules, the AI software engineer.",
        #         tags=["ai", "test", "bot"],
        #         privacy_status="private" # Use "private" for testing
        #     )
        # else:
        #     print("\n'test_video.mp4' not found. Skipping upload test.")

    else:
        print("\nCould not authenticate with YouTube. Please check your setup.")

    print("\n--- YouTube Uploader Test Complete ---")
