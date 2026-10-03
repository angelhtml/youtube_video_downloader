import os
import sys
import shutil
import yt_dlp

# ============================================================
# Configuration
# ============================================================
COOKIES_PATH = "content/cookies.txt"
FIXED_COOKIES_PATH = "content/cookies_fixed.txt"
OUTPUT_DIR = "downloads"

# ============================================================
# Cookie file repair
# ============================================================
def repair_cookies_file(input_path, output_path):
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)

    if not os.path.exists(input_path):
        print(f"❌ Cookies file not found: {input_path}")
        return None

    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    lines = [line.lstrip("\ufeff").rstrip("\r\n") for line in lines]

    has_header = False
    for line in lines:
        if line.strip().startswith("# Netscape HTTP Cookie File") or \
           line.strip().startswith("# HTTP Cookie File"):
            has_header = True
            break

    fixed_lines = []
    if not has_header:
        fixed_lines.append("# Netscape HTTP Cookie File")

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            fixed_lines.append(line)
            continue
        if not stripped:
            continue
        fields = line.split("\t")
        if len(fields) < 7:
            fields = [f for f in line.split(" ") if f]
        if len(fields) >= 7:
            fields[1] = fields[1].upper()
            if len(fields) > 3:
                fields[3] = fields[3].upper()
            fixed_line = "\t".join(fields[:7])
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)

    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(fixed_lines) + "\n")

    print(f"✅ Repaired cookies written to: {output_path}")
    return output_path


# ============================================================
# Quality selection
# ============================================================
def choose_quality():
    """Ask the user for video quality and return a yt-dlp format string."""
    print("\nChoose video quality:")
    print("  1. 144p  (tiny)")
    print("  2. 240p  (very small)")
    print("  3. 360p  (small)")
    print("  4. 480p  (medium)")
    print("  5. 720p  (HD)")
    print("  6. 1080p (Full HD)")
    print("  7. Best available")

    choice = input("Enter number (1-7): ").strip()

    if choice == "1":
        return "bestvideo[height<=144]+bestaudio/best[height<=144]"
    elif choice == "2":
        return "bestvideo[height<=240]+bestaudio/best[height<=240]"
    elif choice == "3":
        return "bestvideo[height<=360]+bestaudio/best[height<=360]"
    elif choice == "4":
        return "bestvideo[height<=480]+bestaudio/best[height<=480]"
    elif choice == "5":
        return "bestvideo[height<=720]+bestaudio/best[height<=720]"
    elif choice == "6":
        return "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    else:
        return "bestvideo+bestaudio/best"


# ============================================================
# Downloader
# ============================================================
def download_youtube_video(url, cookies_path, format_string, output_dir="downloads"):
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'format': format_string,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'js_runtimes': {'deno': {}},
        'cookiefile': cookies_path,
        'extractor_args': {
            'youtube': {
                'remote_components': ['ejs:github']
            }
        },
        'merge_output_format': 'mp4',
        'quiet': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\n⬇️  Downloading: {url}\n")
            ydl.download([url])
        print("\n✅ Download completed successfully.")
        print(f"📁 Saved in: {os.path.abspath(output_dir)}")
    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ Download error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


# ============================================================
# Run
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  YouTube Video Downloader")
    print("=" * 60)

    fixed_path = repair_cookies_file(COOKIES_PATH, FIXED_COOKIES_PATH)
    if not fixed_path:
        print("❌ Could not repair cookies file. Aborting.")
        sys.exit(1)

    video_url = input("\nEnter the YouTube URL: ").strip()
    if not video_url:
        print("❌ No URL provided. Exiting.")
        sys.exit(1)

    format_string = choose_quality()
    download_youtube_video(video_url, fixed_path, format_string, OUTPUT_DIR)
