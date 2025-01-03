import yt_dlp


def get_video_formats(url):
    try:
        # Define options for listing formats
        options = {
            'quiet': True,
            'no_warnings': True,
        }

        # Use yt-dlp to extract video info
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Print available formats
            print("Available Formats:")
            for fmt in info['formats']:
                print(f"ID: {fmt['format_id']}, Resolution: {fmt['resolution']}, Codec: {fmt['vcodec']}, "
                      f"Size: {fmt.get('filesize', 'Unknown')} bytes")
            
            return info['formats']  # Return formats if needed

    except Exception as e:
        print(f"Error fetching formats: {str(e)}")



# Example usage
get_video_formats("https://youtu.be/q08AXmV1sv4?si=lnL0n0rwWI-nXSZ9")
