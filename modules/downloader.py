import yt_dlp
import os
import time

class VideoDownloader:
    def __init__(self, output_dir="downloads"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.last_error = None
        self.last_title = None

    def download_video(self, url, progress_callback=None):
        """Download video and return (filepath, title) or (None, error_message)"""
        self.last_error = None
        self.last_title = None

        # Closure state for throttling
        state = {'last_time': 0}

        def progress_hook(d):
            if not progress_callback: return
            
            now = time.time()
            if d['status'] == 'downloading':
                # Throttle to 10 updates per second for "Live" feel
                if now - state['last_time'] > 0.1:
                    p = d.get('_percent_str', '0%')
                    # Clean up speed/eta string
                    s = d.get('_speed_str', 'N/A')
                    e = d.get('_eta_str', 'N/A')
                    # Consistent prefix for GUI to overwrite
                    progress_callback(None, f"Downloading: {p} | Speed: {s} | ETA: {e}")
                    state['last_time'] = now
            elif d['status'] == 'finished':
                progress_callback(None, "Download finished, converting...")

        ffmpeg_path = os.path.join(os.path.dirname(__file__), '..', 'bin')
        
        # Enforce temp directory
        temp_dir = os.path.join(self.output_dir, "temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        ydl_opts = {
            'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'no_color': True,
            'progress_hooks': [progress_hook],
            'ffmpeg_location': ffmpeg_path,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Handle merged format filename
                if not os.path.exists(filename):
                    # Try with .mp4 extension
                    base = os.path.splitext(filename)[0]
                    if os.path.exists(base + '.mp4'):
                        filename = base + '.mp4'
                
                # Move from temp to main output_dir
                if os.path.exists(filename):
                    final_name = os.path.join(self.output_dir, os.path.basename(filename))
                    if os.path.exists(final_name):
                        os.remove(final_name) # Overwrite if exists
                    os.rename(filename, final_name)
                    filename = final_name

                self.last_title = info.get('title', 'Untitled')
                return filename
                
        except yt_dlp.utils.DownloadError as e:
            self.last_error = f"Download error: {str(e)}"
            return None
        except yt_dlp.utils.ExtractorError as e:
            self.last_error = f"Cannot extract video: {str(e)}"
            return None
        except Exception as e:
            self.last_error = f"Error: {str(e)}"
            return None

    def get_video_info(self, url):
        """Get video info without downloading"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Untitled'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                }
        except Exception as e:
            self.last_error = str(e)
            return None

    def get_channel_videos(self, channel_url, limit=5):
        """Get video URLs from a channel"""
        ydl_opts = {
            'extract_flat': True,
            'quiet': True,
        }
        
        video_urls = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(channel_url, download=False)
                if 'entries' in result:
                    for i, entry in enumerate(result['entries']):
                        if i >= limit:
                            break
                        if entry.get('url'):
                            video_urls.append(entry.get('url'))
                        elif entry.get('id'):
                            video_urls.append(f"https://www.youtube.com/watch?v={entry.get('id')}")
        except Exception as e:
            self.last_error = str(e)
        
        return video_urls
