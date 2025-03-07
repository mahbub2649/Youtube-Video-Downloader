import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QLineEdit, QPushButton, QRadioButton, QGroupBox, QLabel, QMessageBox,
                             QCheckBox, QSizePolicy)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QProcess, Qt, QPropertyAnimation, QEasingCurve, QSize, QTimer
from PyQt6.QtGui import QPalette, QColor, QPainter

def parse_time(time_str):
    """Parse a time string (e.g., '3:40' or '1:23:45') into HH:MM:SS format."""
    parts = time_str.split(":")
    if len(parts) == 1:  # Only seconds
        return f"00:00:{parts[0].zfill(2)}"
    elif len(parts) == 2:  # Minutes and seconds
        return f"00:{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    elif len(parts) == 3:  # Hours, minutes, seconds
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}:{parts[2].zfill(2)}"
    else:
        raise ValueError("Invalid time format")

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self.hide()  # Initially hidden

    def _rotate(self):
        self._angle = (self._angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        if not self.isVisible():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw spinning circles
        painter.translate(20, 20)
        painter.rotate(self._angle)
        
        for i in range(8):
            painter.rotate(45)
            alpha = int(255 * (i + 1) / 8)
            painter.setBrush(QColor(255, 0, 0, alpha))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(-5, -15, 8, 8)

    def start(self):
        self.show()
        self._timer.start(50)

    def stop(self):
        self._timer.stop()
        self.hide()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Video Downloader")
        self.setGeometry(100, 100, 800, 800)  # Made window taller
        self.process = None  # For handling the download process

        # GUI Components
        self.url_input = QLineEdit()
        self.load_button = QPushButton("Load")
        self.preview = QWebEngineView()
        
        # Set minimum size for the preview
        self.preview.setMinimumSize(700, 400)  # 16:9 aspect ratio
        self.preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.full_radio = QRadioButton("Full Video")
        self.partial_radio = QRadioButton("Partial Video")
        self.start_time_input = QLineEdit("00:00:00")
        self.end_time_input = QLineEdit("00:00:00")
        self.download_button = QPushButton("Download")

        # Format selection checkboxes
        self.format_group = QGroupBox("Format Options")
        format_layout = QHBoxLayout()
        self.mp4_checkbox = QCheckBox("MP4")
        self.webm_checkbox = QCheckBox("WEBM")
        self.mp4_checkbox.setChecked(True)  # Default to MP4
        format_layout.addWidget(self.mp4_checkbox)
        format_layout.addWidget(self.webm_checkbox)
        self.format_group.setLayout(format_layout)

        # Status label for download progress
        self.status_label = QLabel("")
        # Size policy and word wrape for status_label
        self.status_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.status_label.setWordWrap(True)


        # Set initial states
        self.full_radio.setChecked(True)
        self.start_time_input.setEnabled(False)
        self.end_time_input.setEnabled(False)
        self.preview.setUrl(QUrl("about:blank"))

        # Connect signals
        self.load_button.clicked.connect(self.load_video)
        self.partial_radio.toggled.connect(self.toggle_time_inputs)
        self.download_button.clicked.connect(self.download)

        # Layout setup
        main_layout = QVBoxLayout()

        # URL input and Load button
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("YouTube URL:"))
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.load_button)
        main_layout.addLayout(url_layout)

        # Video preview
        main_layout.addWidget(self.preview)

        # Download options
        options_group = QGroupBox("Download Options")
        options_layout = QVBoxLayout()
        options_layout.addWidget(self.full_radio)
        options_layout.addWidget(self.partial_radio)

        # Time inputs for partial download
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Start time (HH:MM:SS):"))
        time_layout.addWidget(self.start_time_input)
        time_layout.addWidget(QLabel("End time (HH:MM:SS):"))
        time_layout.addWidget(self.end_time_input)
        options_layout.addLayout(time_layout)
        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)

        # Format selection checkboxes
        main_layout.addWidget(self.format_group)
        main_layout.addWidget(self.status_label)

        # Download button
        main_layout.addWidget(self.download_button)

        # Set the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Create loading spinner
        self.loading_spinner = LoadingSpinner(self)
        
        # Apply custom styling
        self.apply_custom_styling()

    def apply_custom_styling(self):
        # Set the main window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                color: #ffffff;
                font-family: 'Segoe UI', Arial;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #333333;
                border-radius: 10px;
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #ff3333;
            }
            QPushButton {
                padding: 8px 15px;
                border-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3333, stop:1 #ff6666);
                border: none;
                color: white;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff6666, stop:1 #ff9999);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #cc0000, stop:1 #ff3333);
            }
            QRadioButton {
                spacing: 10px;
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
                border-radius: 8px;
                border: 2px solid #666666;
            }
            QRadioButton::indicator:checked {
                background-color: #ff3333;
                border: 2px solid #ff3333;
            }
            QCheckBox {
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                border-radius: 4px;
                border: 2px solid #666666;
            }
            QCheckBox::indicator:checked {
                background-color: #ff3333;
                border: 2px solid #ff3333;
            }
            QGroupBox {
                border: 2px solid #333333;
                border-radius: 10px;
                margin-top: 1em;
                padding-top: 1em;
            }
            QGroupBox::title {
                color: #ff3333;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #cccccc;
            }
            #status_label {
                color: #ff3333;
                font-weight: bold;
            }
        """)

        # Set specific widget properties
        self.status_label.setObjectName("status_label")
        self.status_label.setMaximumWidth(700)
        self.loading_spinner.setStyleSheet("""
            background-color: transparent;
        """)

    def toggle_time_inputs(self, checked):
        """Enable/disable time input fields based on Partial Video selection."""
        self.start_time_input.setEnabled(checked)
        self.end_time_input.setEnabled(checked)

    def load_video(self):
        """Load the video preview in the QWebEngineView."""
        url = self.url_input.text().strip()
        if url:
            self.preview.setUrl(QUrl(url))
        else:
            QMessageBox.warning(self, "Error", "Please enter a valid YouTube URL")

    def download(self):
        """Handle the video download process."""
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            QMessageBox.warning(self, "Error", "A download is already in progress")
            return

        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL")
            return

        if not self.mp4_checkbox.isChecked() and not self.webm_checkbox.isChecked():
            QMessageBox.warning(self, "Error", "Please select at least one format")
            return

        # Prepare the format string
        format_string = []
        if self.mp4_checkbox.isChecked():
            format_string.append("bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/mp4")
        if self.webm_checkbox.isChecked():
            format_string.append("bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]/webm")
        
        format_arg = "/".join(format_string)

        # Prepare the yt-dlp command
        cmd = ['yt-dlp', '-f', format_arg, '-o', '%(title)s.%(ext)s']
        
        if not self.full_radio.isChecked():
            try:
                start = parse_time(self.start_time_input.text())
                end = parse_time(self.end_time_input.text())
                start_secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(start.split(":"))))
                end_secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(end.split(":"))))
                if end_secs <= start_secs:
                    QMessageBox.warning(self, "Error", "End time must be after start time")
                    return
                section = f"*{start}-{end}"
                cmd.extend(['--download-sections', section])
                cmd.extend(['--extractor-args', "youtube:player_client=android,web"])
            except ValueError:
                QMessageBox.warning(self, "Error", "Invalid time format. Use HH:MM:SS or MM:SS")
                return
        
        cmd.append(url)

        # Start the loading spinner
        self.loading_spinner.move(
            self.width() // 2 - self.loading_spinner.width() // 2,
            self.height() // 2 - self.loading_spinner.height() // 2
        )
        self.loading_spinner.start()

        # Start the download process
        self.process = QProcess(self)
        self.process.finished.connect(self.download_finished)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)
        self.download_button.setEnabled(False)
        self.status_label.setText("Starting download...")
        self.process.start(cmd[0], cmd[1:])

    def handle_output(self):
        """Handle process output"""
        if self.process is None:
            return
        output = self.process.readAllStandardOutput().data().decode()
        if output:
            self.status_label.setText(output.split('\r')[-1] if '\r' in output else output)

    def handle_error(self):
        """Handle process errors"""
        if self.process is None:
            return
        error = self.process.readAllStandardError().data().decode()
        if error:
            self.status_label.setText(f"Error: {error}")

    def download_finished(self, exit_code, exit_status):
        """Handle the completion of the download process."""
        self.loading_spinner.stop()
        self.download_button.setEnabled(True)
        if exit_code == 0:
            self.status_label.setText("Download completed successfully!")
            QMessageBox.information(self, "Success", "Download completed successfully!")
        else:
            error_message = "Download failed. Check URL or dependencies."
            self.status_label.setText(error_message)
            QMessageBox.warning(self, "Error", error_message)
        self.process = None

    def resizeEvent(self, event):
        """Handle window resize to keep the spinner centered"""
        super().resizeEvent(event)
        if self.loading_spinner.isVisible():
            self.loading_spinner.move(
                self.width() // 2 - self.loading_spinner.width() // 2,
                self.height() // 2 - self.loading_spinner.height() // 2
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())