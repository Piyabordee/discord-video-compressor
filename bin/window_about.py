# -*- coding: utf-8 -*-

"""
About dialog for Video Compressor
Adapted from PyPlayer window_about.py
"""

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_aboutDialog(object):
    def setupUi(self, aboutDialog):
        aboutDialog.setObjectName("aboutDialog")
        aboutDialog.resize(450, 250)
        aboutDialog.setMinimumSize(QtCore.QSize(450, 250))

        # Dark gradient background
        aboutDialog.setStyleSheet(
            "QLabel { color: white; }\n"
            "QDialog {\n"
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, "
            "stop:0 rgba(50, 50, 50, 255), stop:1 rgba(0, 85, 128, 255));\n"
            "}"
        )

        self.gridLayout = QtWidgets.QGridLayout(aboutDialog)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.gridLayout.setSpacing(8)
        self.gridLayout.setObjectName("gridLayout")

        # Button box
        self.dialogButtonBox = QtWidgets.QDialogButtonBox(aboutDialog)
        self.dialogButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.dialogButtonBox.setCenterButtons(True)
        self.dialogButtonBox.setObjectName("dialogButtonBox")
        self.gridLayout.addWidget(self.dialogButtonBox, 3, 0, 1, 3)

        # Separator line
        self.line = QtWidgets.QFrame(aboutDialog)
        self.line.setFrameShadow(QtWidgets.QFrame.Raised)
        self.line.setLineWidth(1)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 2, 0, 1, 3)

        # Description label
        self.label = QtWidgets.QLabel(aboutDialog)
        self.label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        self.label.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse
        )
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 3)

        # Logo and version layout
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Logo label
        self.labelLogo = QtWidgets.QLabel(aboutDialog)
        self.labelLogo.setMaximumSize(QtCore.QSize(96, 96))
        self.labelLogo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.labelLogo.setScaledContents(True)
        self.labelLogo.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.labelLogo.setWordWrap(True)
        self.labelLogo.setObjectName("labelLogo")
        self.horizontalLayout.addWidget(self.labelLogo)

        # Version layout
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(5, 10, -1, 10)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")

        self.labelVersion = QtWidgets.QLabel(aboutDialog)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(20)
        font.setBold(True)
        self.labelVersion.setFont(font)
        self.labelVersion.setStyleSheet("")
        self.labelVersion.setOpenExternalLinks(True)
        self.labelVersion.setTextInteractionFlags(
            QtCore.Qt.LinksAccessibleByMouse | QtCore.Qt.TextSelectableByMouse
        )
        self.labelVersion.setObjectName("labelVersion")
        self.verticalLayout.addWidget(self.labelVersion)

        self.horizontalLayout.addLayout(self.verticalLayout)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 1)

        self.retranslateUi(aboutDialog)
        self.dialogButtonBox.accepted.connect(aboutDialog.accept)  # type: ignore
        self.dialogButtonBox.rejected.connect(aboutDialog.reject)  # type: ignore
        QtCore.QMetaObject.connectSlotsByName(aboutDialog)

    def retranslateUi(self, aboutDialog):
        _translate = QtCore.QCoreApplication.translate
        aboutDialog.setWindowTitle(_translate("aboutDialog", "About Video Compressor"))

        # Description
        self.label.setText(
            _translate(
                "aboutDialog",
                '<html><head/><body><p><span style=" color:#ffffff;">'
                'Compress videos to approximately 8.2 MB for Discord uploads.<br>'
                'Built with <a href="https://www.python.org/" style="text-decoration: underline; color:#00aaff;">Python</a> '
                'and <a href="https://www.riverbankcomputing.com/software/pyqt/" style="text-decoration: underline; color:#00aaff;">PyQt5</a>.<br>'
                'Uses <a href="https://ffmpeg.org/" style="text-decoration: underline; color:#00aaff;">FFmpeg</a> '
                'for video processing.'
                '</span></p></body></html>',
            )
        )

        # Version info
        self.labelVersion.setText(
            _translate(
                "aboutDialog",
                '<html><head/><body><p style="line-height:0.7">Video Compressor v2.0.0</p>'
                '<p style="line-height:0.3"><span style="font-size:10pt;">'
                '<a href="https://github.com/snowb4ll/discord-video-compressor">'
                '<span style="text-decoration: underline; color:#00aaff;">GitHub</span></a> '
                '2026 by Piyabordee</span></p>'
                '<p><span style="font-size:9pt;">MIT License</span></p>'
                '</body></html>',
            )
        )


class AboutDialog(QtWidgets.QDialog, Ui_aboutDialog):
    """About dialog with logic for the video compressor."""

    VERSION = "2.0.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Set logo if available
        self.set_logo()

        # Connect logo click to open GitHub
        self.labelLogo.mousePressEvent = self.open_github

    def set_logo(self):
        """Set application logo if available."""
        # Try to load icon from resources or file
        icon = QtWidgets.QApplication.style().standardIcon(
            QtWidgets.QStyle.SP_ComputerIcon
        )
        pixmap = icon.pixmap(96, 96)
        self.labelLogo.setPixmap(pixmap)

    def open_github(self, event):
        """Open GitHub repository in browser."""
        import webbrowser

        webbrowser.open("https://github.com/snowb4ll/discord-video-compressor")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    aboutDialog = AboutDialog()
    aboutDialog.show()
    sys.exit(app.exec_())
