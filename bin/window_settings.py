# -*- coding: utf-8 -*-

"""
Settings dialog for Video Compressor
Adapted from PyPlayer window_settings.py
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import os
import config


class Ui_settingsDialog(object):
    def setupUi(self, settingsDialog):
        settingsDialog.setObjectName("settingsDialog")
        settingsDialog.resize(450, 400)
        settingsDialog.setMinimumSize(QtCore.QSize(450, 400))

        self.gridLayout = QtWidgets.QGridLayout(settingsDialog)
        self.gridLayout.setContentsMargins(8, 8, 8, 8)
        self.gridLayout.setObjectName("gridLayout")

        # Button box (OK/Cancel)
        self.buttonBox = QtWidgets.QDialogButtonBox(settingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 2)

        # Scroll area for settings
        self.scrollArea = QtWidgets.QScrollArea(settingsDialog)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 430, 350))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")

        # General tab (only tab we need)
        self.tabGeneral = QtWidgets.QWidget()
        self.tabGeneral.setObjectName("tabGeneral")

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setVerticalSpacing(10)
        self.formLayout.setObjectName("formLayout")

        # Target file size
        self.label_target_size = QtWidgets.QLabel(self.tabGeneral)
        self.label_target_size.setText("Target file size (MB):")
        self.label_target_size.setObjectName("label_target_size")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_target_size)

        self.spinTargetSize = QtWidgets.QDoubleSpinBox(self.tabGeneral)
        self.spinTargetSize.setDecimals(1)
        self.spinTargetSize.setMinimum(1.0)
        self.spinTargetSize.setMaximum(25.0)
        self.spinTargetSize.setSingleStep(0.1)
        self.spinTargetSize.setProperty("value", 8.2)
        self.spinTargetSize.setObjectName("spinTargetSize")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.spinTargetSize)

        # Audio bitrate
        self.label_audio_bitrate = QtWidgets.QLabel(self.tabGeneral)
        self.label_audio_bitrate.setText("Audio bitrate (kbps):")
        self.label_audio_bitrate.setObjectName("label_audio_bitrate")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_audio_bitrate)

        self.comboAudioBitrate = QtWidgets.QComboBox(self.tabGeneral)
        self.comboAudioBitrate.addItem("64")
        self.comboAudioBitrate.addItem("96")
        self.comboAudioBitrate.addItem("128")
        self.comboAudioBitrate.addItem("192")
        self.comboAudioBitrate.addItem("256")
        self.comboAudioBitrate.setCurrentIndex(2)  # 128 kbps default
        self.comboAudioBitrate.setObjectName("comboAudioBitrate")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboAudioBitrate)

        # FFmpeg path
        self.label_ffmpeg = QtWidgets.QLabel(self.tabGeneral)
        self.label_ffmpeg.setText("FFmpeg path:")
        self.label_ffmpeg.setObjectName("label_ffmpeg")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_ffmpeg)

        self.horizontalLayout_ffmpeg = QtWidgets.QHBoxLayout()
        self.lineFFmpegPath = QtWidgets.QLineEdit(self.tabGeneral)
        self.lineFFmpegPath.setPlaceholderText("Auto-detect or browse...")
        self.lineFFmpegPath.setObjectName("lineFFmpegPath")
        self.horizontalLayout_ffmpeg.addWidget(self.lineFFmpegPath)

        self.buttonBrowseFFmpeg = QtWidgets.QPushButton(self.tabGeneral)
        self.buttonBrowseFFmpeg.setText("Browse...")
        self.buttonBrowseFFmpeg.setObjectName("buttonBrowseFFmpeg")
        self.horizontalLayout_ffmpeg.addWidget(self.buttonBrowseFFmpeg)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_ffmpeg)

        # FFprobe path
        self.label_ffprobe = QtWidgets.QLabel(self.tabGeneral)
        self.label_ffprobe.setText("FFprobe path:")
        self.label_ffprobe.setObjectName("label_ffprobe")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_ffprobe)

        self.horizontalLayout_ffprobe = QtWidgets.QHBoxLayout()
        self.lineFFprobePath = QtWidgets.QLineEdit(self.tabGeneral)
        self.lineFFprobePath.setPlaceholderText("Auto-detect or browse...")
        self.lineFFprobePath.setObjectName("lineFFprobePath")
        self.horizontalLayout_ffprobe.addWidget(self.lineFFprobePath)

        self.buttonBrowseFFprobe = QtWidgets.QPushButton(self.tabGeneral)
        self.buttonBrowseFFprobe.setText("Browse...")
        self.buttonBrowseFFprobe.setObjectName("buttonBrowseFFprobe")
        self.horizontalLayout_ffprobe.addWidget(self.buttonBrowseFFprobe)
        self.formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_ffprobe)

        # Auto-open output
        self.checkAutoOpen = QtWidgets.QCheckBox(self.tabGeneral)
        self.checkAutoOpen.setText("Open output file after compression")
        self.checkAutoOpen.setObjectName("checkAutoOpen")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.SpanningRole, self.checkAutoOpen)

        # Delete after compress
        self.checkDeleteOriginal = QtWidgets.QCheckBox(self.tabGeneral)
        self.checkDeleteOriginal.setText("Delete original after compression (WARNING: Irreversible)")
        self.checkDeleteOriginal.setObjectName("checkDeleteOriginal")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.SpanningRole, self.checkDeleteOriginal)

        # Add form layout to vertical layout
        self.verticalLayout.addLayout(self.formLayout)
        self.verticalLayout.addStretch()

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 2)

        self.retranslateUi(settingsDialog)
        QtCore.QMetaObject.connectSlotsByName(settingsDialog)

    def retranslateUi(self, settingsDialog):
        _translate = QtCore.QCoreApplication.translate
        settingsDialog.setWindowTitle(_translate("settingsDialog", "Settings"))


class SettingsDialog(QtWidgets.QDialog, Ui_settingsDialog):
    """Settings dialog with logic for the video compressor."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Connect signals
        self.buttonBrowseFFmpeg.clicked.connect(self.browse_ffmpeg)
        self.buttonBrowseFFprobe.clicked.connect(self.browse_ffprobe)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Style the delete checkbox
        self.checkDeleteOriginal.setStyleSheet("QCheckBox { color: red; }")

    def browse_ffmpeg(self):
        """Browse for FFmpeg executable."""
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select FFmpeg executable",
            "",
            "Executable files (*.exe);;All files (*.*)"
        )
        if filename:
            self.lineFFmpegPath.setText(filename)

    def browse_ffprobe(self):
        """Browse for FFprobe executable."""
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select FFprobe executable",
            "",
            "Executable files (*.exe);;All files (*.*)"
        )
        if filename:
            self.lineFFprobePath.setText(filename)

    def get_settings(self):
        """Get settings values as dictionary."""
        return {
            'target_size_mb': self.spinTargetSize.value(),
            'audio_bitrate': int(self.comboAudioBitrate.currentText()),
            'ffmpeg_path': self.lineFFmpegPath.text(),
            'ffprobe_path': self.lineFFprobePath.text(),
            'auto_open_output': self.checkAutoOpen.isChecked(),
            'delete_after_compress': self.checkDeleteOriginal.isChecked(),
        }

    def set_settings(self, settings_dict):
        """Set settings from dictionary."""
        self.spinTargetSize.setValue(settings_dict.get('target_size_mb', 8.2))
        bitrate = str(settings_dict.get('audio_bitrate', 128))
        index = self.comboAudioBitrate.findText(bitrate)
        if index >= 0:
            self.comboAudioBitrate.setCurrentIndex(index)
        self.lineFFmpegPath.setText(settings_dict.get('ffmpeg_path', ''))
        self.lineFFprobePath.setText(settings_dict.get('ffprobe_path', ''))
        self.checkAutoOpen.setChecked(settings_dict.get('auto_open_output', False))
        self.checkDeleteOriginal.setChecked(settings_dict.get('delete_after_compress', False))
