#!/usr/bin/env python3
"""
Simple LabelMe‑like annotation tool with PyQt5.

更新日志
────────
* **2025‑07‑26** : 添加“打开图片”按钮、自动适配分辨率、按钮同排。  
* **2025‑07‑26‑b** : 若图片尺寸超过窗口可视面积，自动显示**水平/垂直滚动条**。

核心功能
────────
1. 点击图片选择中心点，实时绘制 600×600 方框（裁剪到边界内）。
2. 打开/保存按钮在同一行；可不带参数启动，通过按钮选图。
3. 打开图片时窗口会根据屏幕可用分辨率自适配（回退 1512×982）。
4. 图片大于窗口时自动出现滚动条，可自由拖动查看全图。

用法
────
```bash
python simple_label_tool.py            # 启动后点击“打开图片”
python simple_label_tool.py IMG.png     # 直接加载图片
```

依赖
────
```bash
pip install pyqt5
```
"""
from __future__ import annotations

import sys
import json
import base64
from pathlib import Path
from typing import Optional, List

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QFileDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QScrollArea,
)
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRect, QSize


# ‑‑‑‑ Image display & drawing widget ‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑─
class ImageLabel(QLabel):
    """QLabel subclass that supports picking a center point and drawing a 600×600 rectangle."""

    RECT_SIZE = 600  # side length of the square

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self._pixmap: Optional[QPixmap] = None
        self.image_path: Optional[str] = None
        self.center_point: Optional[QPoint] = None

    # ‑‑‑‑ Public API -------------------------------------------------------
    def load_image(self, image_path: str) -> None:
        pm = QPixmap(image_path)
        if pm.isNull():
            raise ValueError(f"Cannot load image: {image_path}")
        self._pixmap = pm
        self.image_path = image_path
        self.center_point = None  # reset any previous annotation
        self.setPixmap(pm)
        # 固定尺寸以触发滚动条逻辑
        self.setFixedSize(pm.size())
        self.update()

    def rectangle_points(self) -> Optional[List[List[float]]]:
        if not (self.center_point and self._pixmap):
            return None
        rect = self._current_qrect()
        return [[float(rect.left()), float(rect.top())], [float(rect.right()), float(rect.bottom())]]

    @property
    def pixmap_size(self) -> tuple[int, int]:
        if not self._pixmap:
            return 0, 0
        return self._pixmap.width(), self._pixmap.height()

    # ‑‑‑‑ Event handlers ---------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._pixmap:
            # Translate the click point to image coordinates (scroll offsets handled by QLabel geometry)
            self.center_point = event.pos()
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.center_point and self._pixmap:
            painter = QPainter(self)
            pen = QPen(Qt.yellow, 2)
            painter.setPen(pen)
            painter.drawRect(self._current_qrect())

    # ‑‑‑‑ Helpers ----------------------------------------------------------
    def _current_qrect(self) -> QRect:
        half = self.RECT_SIZE // 2
        cx, cy = self.center_point.x(), self.center_point.y()
        img_w, img_h = self.pixmap_size
        x1 = max(0, cx - half)
        y1 = max(0, cy - half)
        x2 = min(img_w, cx + half)
        y2 = min(img_h, cy + half)
        return QRect(QPoint(x1, y1), QPoint(x2, y2))


# ‑‑‑‑ Main application window ‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑────────
class MainWindow(QMainWindow):
    FALLBACK_SIZE = QSize(1512, 982)  # used when screen resolution cannot be obtained

    def __init__(self, image_path: str):
        super().__init__()
        self.setWindowTitle("Simple LabelMe‑like Tool")

        # Central image widget inside a scroll area
        self.image_label = ImageLabel()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)
        self.image_path = image_path

        if image_path:
            self.image_label.load_image(image_path)

        # Buttons (same row)
        open_btn = QPushButton("打开图片 (Open)")
        save_btn = QPushButton("保存标签 (Save)")
        open_btn.clicked.connect(self.open_image)
        save_btn.clicked.connect(self.save_json)

        button_row = QHBoxLayout()
        button_row.addWidget(open_btn)
        button_row.addWidget(save_btn)
        button_row.addStretch(1)

        # Overall layout
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        layout.addLayout(button_row)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.adjust_window_size()


    # ‑‑‑‑ UI helpers -------------------------------------------------------
    def adjust_window_size(self):
        screen = QApplication.primaryScreen()
        size = screen.availableGeometry().size() if screen else self.FALLBACK_SIZE
        self.resize(size)
        self.setFixedSize(size)

    # ‑‑‑‑ Slots ------------------------------------------------------------
    def open_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "/Users/manishaqian/Documents/骨科工作/ai 外髁骨折/image/移位",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )
        if not path:
            return
        try:
            self.image_label.load_image(path)
        except ValueError as exc:
            QMessageBox.critical(self, "加载失败", str(exc))
            return
        self.adjust_window_size()  # readjust after loading

    def save_json(self):
        if not self.image_label._pixmap:
            QMessageBox.warning(self, "提示", "请先打开图片！")
            return

        points = self.image_label.rectangle_points()
        if not points:
            QMessageBox.warning(self, "提示", "请在图像上点击以选择中心点！")
            return

        json_path, _ = QFileDialog.getSaveFileName(self, "保存 JSON", f"/Users/manishaqian/Documents/labelPZY/d/{self.image_label.image_path.split('/')[-1].replace('.jpg', '').replace('.png', '')}.json", "JSON Files (*.json)")
        if not json_path:
            return

        img_w, img_h = self.image_label.pixmap_size
        image_file = Path(self.image_label.image_path)
        with image_file.open("rb") as fp:
            img_b64 = base64.b64encode(fp.read()).decode("utf‑8")

        data = {
            "version": "5.8.3",
            "flags": {},
            "shapes": [
                {
                    "label": "d",
                    "points": points,
                    "group_id": None,
                    "description": "",
                    "shape_type": "rectangle",
                    "flags": {},
                    "mask": None,
                }
            ],
            "imagePath": image_file.name,
            "imageData": img_b64,
            "imageHeight": img_h,
            "imageWidth": img_w,
        }
        with open(json_path, "w", encoding="utf‑8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "完成", f"标签已保存至 {json_path}")
        self.open_image()


# ‑‑‑‑ Entry point ‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑‑────────
def main():
    image_path = sys.argv[1] if len(sys.argv) == 2 else None
    app = QApplication(sys.argv)
    window = MainWindow(image_path)
    window.show()
    window.open_image()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
