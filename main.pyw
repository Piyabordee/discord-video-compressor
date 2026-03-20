"""Entry point for Discord Video Compressor"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from bin.window_main import MainWindow
from i18n import i18n
import constants


def cli_entry(input_file: str):
    """CLI mode entry point (no GUI)"""
    from core.compressor import Compressor
    from core.edit import Edit

    # Check FFmpeg
    if not constants.FFMPEG_PATH:
        print("Error: FFmpeg not found")
        sys.exit(1)

    # Setup compressor
    compressor = Compressor(constants.FFMPEG_PATH, constants.FFPROBE_PATH)

    # Calculate output path
    d, fn = os.path.split(input_file)
    name, _ = os.path.splitext(fn)
    output_file = os.path.join(d, f"{name}_compressed_9mb.mp4")

    # Compress (synchronous for CLI)
    settings = {'target_mb': 8.2, 'audio_kbps': 128, 'preset': 'medium'}

    try:
        edit = compressor.compress(input_file, output_file, settings)
        print(f"Compressing: {input_file}")
        print(f"To: {output_file}")
        print(f"Video bitrate: {edit.v_kbps:.0f} kbps")

        # Wait for completion
        edit.process.wait()

        if edit.process.returncode == 0:
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"OK: {output_file} ({size_mb:.2f} MB)")
            sys.exit(0)
        else:
            print(f"Error: Compression failed")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(2)


def main():
    """GUI mode entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("VideoCompressor")
    app.setOrganizationName("DiscordVideoCompressor")

    # Load language
    i18n.load('th')  # Default to Thai

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        # CLI mode
        cli_entry(sys.argv[1])
    else:
        # GUI mode
        main()
