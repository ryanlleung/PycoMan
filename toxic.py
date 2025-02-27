import sys
import re
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel
)
from PyQt5.QtCore import QTimer

class HyperlinkExtractor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hyperlink Extractor")
        self.resize(600, 400)

        # Use a list to store detected hyperlinks in order.
        self.links = []
        self.last_clipboard_content = ""

        # Create GUI components.
        self.counter_label = QLabel("Total Links: 0")
        self.status_label = QLabel("")  # Small console to display new link messages.
        self.info_label = QLabel("Automatically capturing hyperlinks from your clipboard...")
        self.list_widget = QListWidget()
        self.copy_button = QPushButton("Copy All Hyperlinks")
        self.reset_button = QPushButton("Reset Links")

        # Layout for counter and status messages.
        top_layout = QVBoxLayout()
        top_layout.addWidget(self.counter_label)
        top_layout.addWidget(self.status_label)

        # Layout for buttons.
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.reset_button)

        # Main layout.
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.info_label)
        main_layout.addWidget(QLabel("Detected Hyperlinks:"))
        main_layout.addWidget(self.list_widget)
        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect button signals.
        self.copy_button.clicked.connect(self.copy_links_to_clipboard)
        self.reset_button.clicked.connect(self.reset_links)

        # Get the clipboard instance and start polling.
        self.clipboard = QApplication.clipboard()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(500)

    def check_clipboard(self):
        """Poll the clipboard for new content and process it only if changed."""
        mime = self.clipboard.mimeData()
        # Prioritize HTML content over plain text.
        if mime.hasHtml():
            html = mime.html()
            if html != self.last_clipboard_content:
                self.last_clipboard_content = html
                self.process_html(html)
        elif mime.hasText():
            text = mime.text()
            if text != self.last_clipboard_content:
                self.last_clipboard_content = text
                self.process_plain_text(text)

    def process_html(self, html):
        """
        Extracts hyperlinks from raw HTML by searching for href attributes.
        """
        pattern = r'href=[\'"]([^\'" >]+)'
        found_links = re.findall(pattern, html)
        new_count = 0
        for link in found_links:
            if link not in self.links:
                self.links.append(link)
                new_count += 1
        if new_count:
            self.update_list_widget()
            self.update_status(new_count)

    def process_plain_text(self, text):
        """
        Extracts hyperlinks from plain text.
        """
        pattern = r'https?://[^\s\'"<>]+'
        found_links = re.findall(pattern, text)
        new_count = 0
        for link in found_links:
            if link not in self.links:
                self.links.append(link)
                new_count += 1
        if new_count:
            self.update_list_widget()
            self.update_status(new_count)

    def update_list_widget(self):
        """Updates the list widget with the current list of hyperlinks and scrolls to the bottom."""
        self.list_widget.clear()
        for link in self.links:
            self.list_widget.addItem(link)
        self.list_widget.scrollToBottom()
        self.counter_label.setText(f"Total Links: {len(self.links)}")

    def update_status(self, new_count):
        """Updates the status console with the number of new links added."""
        self.status_label.setText(f"Added {new_count} new link{'s' if new_count != 1 else ''}.")

    def copy_links_to_clipboard(self):
        """Copies all detected hyperlinks to the clipboard, joined by newline characters."""
        if self.links:
            links_text = "\n".join(self.links)
            self.clipboard.setText(links_text)

    def reset_links(self):
        """Clears the stored links and updates the GUI."""
        self.links = []
        self.list_widget.clear()
        self.counter_label.setText("Total Links: 0")
        self.status_label.setText("Links reset.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HyperlinkExtractor()
    window.show()
    sys.exit(app.exec_())
