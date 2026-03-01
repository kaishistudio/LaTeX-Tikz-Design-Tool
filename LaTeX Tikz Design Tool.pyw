import sys
import math
from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                                QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QFileDialog, 
                                QMessageBox, QListWidget)
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# ======================== Shape Base Class ========================
class TikzShape:
    def to_tikz(self):
        return ""

class TikzRect(TikzShape):
    def __init__(self, x1, y1, x2, y2, color="black", line_width=1, dashed=False, fill_color="none", corner_radius=0):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.color = color
        self.line_width = line_width
        self.dashed = dashed
        self.fill_color = fill_color
        self.corner_radius = corner_radius

    def to_tikz(self):
        fill_part = f", fill={self.fill_color}" if self.fill_color != "none" else ""
        dash_part = ", dashed" if self.dashed else ""
        radius_part = f", rounded corners={self.corner_radius}pt" if self.corner_radius > 0 else ""
        return f"\\draw[draw={self.color}, line width={self.line_width}pt{fill_part}{dash_part}{radius_part}] ({self.x1},{self.y1}) rectangle ({self.x2},{self.y2});"

class TikzCircle(TikzShape):
    def __init__(self, cx, cy, r, color="black", line_width=1, dashed=False, fill_color="none"):
        self.cx, self.cy, self.r = cx, cy, r
        self.color = color
        self.line_width = line_width
        self.dashed = dashed
        self.fill_color = fill_color

    def to_tikz(self):
        fill_part = f", fill={self.fill_color}" if self.fill_color != "none" else ""
        dash_part = ", dashed" if self.dashed else ""
        return f"\\draw[draw={self.color}, line width={self.line_width}pt{fill_part}{dash_part}] ({self.cx},{self.cy}) circle ({self.r});"

class TikzLine(TikzShape):
    def __init__(self, x1, y1, x2, y2, color="black", line_width=1, dashed=False):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.color = color
        self.line_width = line_width
        self.dashed = dashed
        self.fill_color = "none"

    def to_tikz(self):
        dash_part = ", dashed" if self.dashed else ""
        return f"\\draw[draw={self.color}, line width={self.line_width}pt{dash_part}] ({self.x1},{self.y1}) -- ({self.x2},{self.y2});"

class TikzArrow(TikzShape):
    def __init__(self, x1, y1, x2, y2, color="black", line_width=1, dashed=False):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.color = color
        self.line_width = line_width
        self.dashed = dashed
        self.fill_color = "none"

    def to_tikz(self):
        dash_part = ", dashed" if self.dashed else ""
        return f"\\draw[draw={self.color}, line width={self.line_width}pt{dash_part}, ->] ({self.x1},{self.y1}) -- ({self.x2},{self.y2});"

class TikzEllipse(TikzShape):
    def __init__(self, cx, cy, rx, ry, color="black", line_width=1, dashed=False, fill_color="none"):
        self.cx, self.cy = cx, cy
        self.rx, self.ry = rx, ry
        self.color = color
        self.line_width = line_width
        self.dashed = dashed
        self.fill_color = fill_color

    def to_tikz(self):
        fill_part = f", fill={self.fill_color}" if self.fill_color != "none" else ""
        dash_part = ", dashed" if self.dashed else ""
        return f"\\draw[draw={self.color}, line width={self.line_width}pt{fill_part}{dash_part}] ({self.cx},{self.cy}) ellipse ({self.rx} and {self.ry});"

class TikzPolygon(TikzShape):
    def __init__(self, cx, cy, radius, sides, color="black", line_width=1, dashed=False, fill_color="none", rotation=0):
        self.cx, self.cy = cx, cy
        self.radius = radius
        self.sides = sides
        self.color = color
        self.line_width = line_width
        self.dashed = dashed
        self.fill_color = fill_color
        self.rotation = rotation

    def to_tikz(self):
        fill_part = f", fill={self.fill_color}" if self.fill_color != "none" else ""
        dash_part = ", dashed" if self.dashed else ""
        rotation_part = f", rotate={self.rotation}" if self.rotation != 0 else ""
        # Calculate vertices for regular polygon
        vertices = []
        for i in range(self.sides):
            angle = 2 * math.pi * i / self.sides - math.pi / 2 + math.radians(self.rotation)
            x = self.cx + self.radius * math.cos(angle)
            y = self.cy + self.radius * math.sin(angle)
            vertices.append(f"({x:.2f},{y:.2f})")
        return f"\\draw[draw={self.color}, line width={self.line_width}pt{fill_part}{dash_part}] {' -- '.join(vertices)} -- cycle;"

class TikzCustomPolygon(TikzShape):
    def __init__(self, vertices, color="black", line_width=1, dashed=False, fill_color="none"):
        self.vertices = vertices  # List of (x, y) tuples
        self.color = color
        self.line_width = line_width
        self.dashed = dashed
        self.fill_color = fill_color

    def to_tikz(self):
        fill_part = f", fill={self.fill_color}" if self.fill_color != "none" else ""
        dash_part = ", dashed" if self.dashed else ""
        # Convert vertices to TikZ format
        vertex_strings = [f"({x:.2f},{y:.2f})" for x, y in self.vertices]
        return f"\\draw[draw={self.color}, line width={self.line_width}pt{fill_part}{dash_part}] {' -- '.join(vertex_strings)} -- cycle;"

class TikzArc(TikzShape):
    def __init__(self, cx, cy, r, start_angle, end_angle, color="black", line_width=1, dashed=False, cx1=None, cy1=None):
        self.cx, self.cy = cx, cy
        self.cx1, self.cy1 = cx1, cy1
        self.r = r
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.color = color
        self.line_width = line_width
        self.dashed = dashed
        self.fill_color = "none"

    def to_tikz(self):
        dash_part = ", dashed" if self.dashed else ""
        return f"\\draw[draw={self.color}, line width={self.line_width}pt{dash_part}] ({self.cx},{self.cy}) arc ({-self.start_angle}:{-self.end_angle}:{self.r});"

class TikzEllipticArc(TikzShape):
    def __init__(self, cx, cy, rx, ry, start_angle, end_angle, color="black", line_width=1, dashed=False, cx1=None, cy1=None):
        self.cx, self.cy = cx, cy
        self.rx, self.ry = rx, ry
        self.cx1, self.cy1 = cx1, cy1
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.color = color
        self.line_width = line_width
        self.dashed = dashed
        self.fill_color = "none"

    def to_tikz(self):
        dash_part = ", dashed" if self.dashed else ""
        return f"\\draw[draw={self.color}, line width={self.line_width}pt{dash_part}] ({self.cx},{self.cy}) arc ({-self.start_angle}:{-self.end_angle}:{self.rx} and {self.ry});"

class TikzBezier(TikzShape):
    def __init__(self, x1, y1, x2, y2, x3, y3, color="black", line_width=1, dashed=False):
        self.x1, self.y1 = x1, y1  # Start point
        self.x2, self.y2 = x2, y2  # Control point
        self.x3, self.y3 = x3, y3  # End point
        self.color = color
        self.line_width = line_width
        self.dashed = dashed
        self.fill_color = "none"

    def to_tikz(self):
        dash_part = ", dashed" if self.dashed else ""
        return f"\\draw[draw={self.color}, line width={self.line_width}pt{dash_part}] ({self.x1},{self.y1}) .. controls ({self.x2},{self.y2}) .. ({self.x3},{self.y3});"

class TikzText(TikzShape):
    def __init__(self, x, y, text, color="black", font_size=12, anchor="left"):
        self.x, self.y = x, y  # Position
        self.text = text  # Text content
        self.color = color
        self.font_size = font_size  # Font size in points
        self.anchor = anchor  # Text anchor: left, center, right
        self.line_width = 1  # For compatibility
        self.dashed = False  # For compatibility
        self.fill_color = "none"

    def to_tikz(self):
        anchor_map = {"left": "west", "center": "center", "right": "east"}
        tikz_anchor = anchor_map.get(self.anchor, "west")
        return f"\\node[anchor={tikz_anchor}, text={self.color}, font=\\fontsize{{{self.font_size}}}{{{int(self.font_size*1.2)}}}\\selectfont] at ({self.x},{self.y}) {{{self.text}}};"

class TikzDimension(TikzShape):
    """Linear dimension annotation showing distance between two points"""
    def __init__(self, x1, y1, x2, y2, offset=0.5, color="black", line_width=1, text_color="black"):
        self.x1, self.y1 = x1, y1  # Start point
        self.x2, self.y2 = x2, y2  # End point
        self.offset = offset  # Offset distance from the measured line
        self.color = color
        self.line_width = line_width
        self.text_color = text_color
        self.dashed = False
        self.fill_color = "none"
        
        # Calculate dimension value
        self.value = math.sqrt((x2-x1)**2 + (y2-y1)**2)
    
    def to_tikz(self):
        # Calculate offset direction (perpendicular to the line)
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        length = math.sqrt(dx**2 + dy**2)
        if length > 0:
            # Perpendicular direction (rotate 90 degrees)
            perp_x = -dy / length * self.offset
            perp_y = dx / length * self.offset
        else:
            perp_x, perp_y = 0, self.offset
        
        # Extension line start and end points (with offset)
        ext1_x = self.x1 + perp_x
        ext1_y = self.y1 + perp_y
        ext2_x = self.x2 + perp_x
        ext2_y = self.y2 + perp_y
        
        # Midpoint for text
        mid_x = (ext1_x + ext2_x) / 2
        mid_y = (ext1_y + ext2_y) / 2
        
        # Format value to 2 decimal places
        value_str = f"{self.value:.2f}"
        
        lines = []
        # Extension lines
        lines.append(f"\\draw[{self.color}, line width={self.line_width}pt] ({self.x1},{self.y1}) -- ({ext1_x:.2f},{ext1_y:.2f});")
        lines.append(f"\\draw[{self.color}, line width={self.line_width}pt] ({self.x2},{self.y2}) -- ({ext2_x:.2f},{ext2_y:.2f});")
        # Dimension line with arrows
        lines.append(f"\\draw[{self.color}, line width={self.line_width}pt, <->] ({ext1_x:.2f},{ext1_y:.2f}) -- ({ext2_x:.2f},{ext2_y:.2f});")
        # Text label
        lines.append(f"\\node[fill=white, inner sep=1pt, text={self.text_color}, font=\\small] at ({mid_x:.2f},{mid_y:.2f}) {{{value_str}}};")
        
        return "\n".join(lines)

# ======================== Canvas ========================
class Canvas(QWidget):
    shape_changed = Signal()
    shape_moved = Signal()

    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 500)
        self.mode = "rect"
        self.shapes = []
        self.start = None
        self.current = None
        # For undo/redo functionality
        self.history = []
        self.history_index = -1
        self.max_history = 50  # Limit history size
        # Current drawing properties
        self.current_color = "black"
        self.current_line_width = 1
        self.current_dashed = False
        self.current_fill_color = "none"
        # Selected shape for editing
        self.selected_shape = None
        # Control points for selected shape
        self.control_points = []
        # Custom polygon vertices
        self.custom_polygon_vertices = []

    def set_mode(self, mode):
        self.mode = mode
        if mode == "move":
            # Set move cursor
            self.setCursor(Qt.SizeAllCursor)
        else:
            # Set default cursor
            self.setCursor(Qt.ArrowCursor)

    def draw_control_points(self, painter):
        # Draw control points for selected shape
        if not self.selected_shape:
            return
        
        painter.setPen(QPen(Qt.red, 2))
        painter.setBrush(QBrush(Qt.red))
        point_size = 1
        
        # Set font for coordinate labels
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(Qt.black)
        
        if isinstance(self.selected_shape, TikzRect):
            # Draw 2 corner points (top-left and bottom-right)
            x1 = self.selected_shape.x1*50
            y1 = (self.height() - self.selected_shape.y1*50)
            x2 = self.selected_shape.x2*50
            y2 = (self.height() - self.selected_shape.y2*50)
            
            # Top-left corner
            corner_x = min(x1, x2)
            corner_y = min(y1, y2)
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(corner_x, corner_y), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(corner_x + 8), int(corner_y - 8), f"({self.selected_shape.x1:.1f}, {self.selected_shape.y1:.1f})")
            
            # Bottom-right corner
            corner_x = max(x1, x2)
            corner_y = max(y1, y2)
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(corner_x, corner_y), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(corner_x + 8), int(corner_y + 15), f"({self.selected_shape.x2:.1f}, {self.selected_shape.y2:.1f})")
            
        elif isinstance(self.selected_shape, TikzCircle):
            # Draw center point only
            cx = self.selected_shape.cx*50
            cy = (self.height() - self.selected_shape.cy*50)
            
            # Center point
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(cx, cy), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(cx + 8), int(cy - 8), f"Center: ({self.selected_shape.cx:.1f}, {self.selected_shape.cy:.1f})")
        elif isinstance(self.selected_shape, TikzEllipse):
            # Draw center point only
            cx = self.selected_shape.cx*50
            cy = (self.height() - self.selected_shape.cy*50)
            
            # Center point
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(cx, cy), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(cx + 8), int(cy - 8), f"Center: ({self.selected_shape.cx:.1f}, {self.selected_shape.cy:.1f})")
        elif isinstance(self.selected_shape, TikzPolygon):
            # Draw center point only
            cx = self.selected_shape.cx*50
            cy = (self.height() - self.selected_shape.cy*50)
            
            # Center point
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(cx, cy), point_size, point_size)
            painter.setPen(Qt.black)
            sides_name = {3: "Triangle", 5: "Pentagon", 6: "Hexagon"}.get(self.selected_shape.sides, f"Polygon ({self.selected_shape.sides})")
            painter.drawText(int(cx + 8), int(cy - 8), f"Center: ({self.selected_shape.cx:.1f}, {self.selected_shape.cy:.1f})")
            
        elif isinstance(self.selected_shape, TikzLine) or isinstance(self.selected_shape, TikzArrow):
            # Draw start and end points with coordinates
            x1 = self.selected_shape.x1*50
            y1 = (self.height() - self.selected_shape.y1*50)
            x2 = self.selected_shape.x2*50
            y2 = (self.height() - self.selected_shape.y2*50)
            
            # Start point
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(x1, y1), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(x1 + 8), int(y1 - 8), f"Start: ({self.selected_shape.x1:.1f}, {self.selected_shape.y1:.1f})")
            
            # End point
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(x2, y2), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(x2 + 8), int(y2 - 8), f"End: ({self.selected_shape.x2:.1f}, {self.selected_shape.y2:.1f})")
        elif isinstance(self.selected_shape, TikzArc):
            # Draw center point
            cx = self.selected_shape.cx1*50
            cy = (self.height() - self.selected_shape.cy1*50)
            
            # Center point
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(cx, cy), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(cx + 8), int(cy - 8), f"Center: ({self.selected_shape.cx:.1f}, {self.selected_shape.cy:.1f})")
            
            # Draw start and end points
            start_angle_rad = math.radians(self.selected_shape.start_angle)
            end_angle_rad = math.radians(self.selected_shape.end_angle)
            r = self.selected_shape.r * 50
            
            start_x = cx + r * math.cos(start_angle_rad)
            start_y = cy - r * math.sin(start_angle_rad)
            end_x = cx + r * math.cos(end_angle_rad)
            end_y = cy - r * math.sin(end_angle_rad)
            
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(start_x, start_y), point_size, point_size)
            painter.drawEllipse(QPointF(end_x, end_y), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(start_x + 8), int(start_y - 8), f"Start: {self.selected_shape.start_angle:.1f}°")
            painter.drawText(int(end_x + 8), int(end_y + 15), f"End: {self.selected_shape.end_angle:.1f}°")
        elif isinstance(self.selected_shape, TikzEllipticArc):
            # Draw center point
            cx = self.selected_shape.cx1*50
            cy = (self.height() - self.selected_shape.cy1*50)
            
            # Center point
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(cx, cy), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(cx + 8), int(cy - 8), f"Center: ({self.selected_shape.cx:.1f}, {self.selected_shape.cy:.1f})")
            
            # Draw start and end points
            start_angle_rad = math.radians(self.selected_shape.start_angle)
            end_angle_rad = math.radians(self.selected_shape.end_angle)
            rx = self.selected_shape.rx * 50
            ry = self.selected_shape.ry * 50
            
            start_x = cx + rx * math.cos(start_angle_rad)
            start_y = cy - ry * math.sin(start_angle_rad)
            end_x = cx + rx * math.cos(end_angle_rad)
            end_y = cy - ry * math.sin(end_angle_rad)
            
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(start_x, start_y), point_size, point_size)
            painter.drawEllipse(QPointF(end_x, end_y), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(start_x + 8), int(start_y - 8), f"Start: {self.selected_shape.start_angle:.1f}°")
            painter.drawText(int(end_x + 8), int(end_y + 15), f"End: {self.selected_shape.end_angle:.1f}°")
        elif isinstance(self.selected_shape, TikzBezier):
            # Draw start point
            x1 = self.selected_shape.x1*50
            y1 = (self.height() - self.selected_shape.y1*50)
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(x1, y1), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(x1 + 8), int(y1 - 8), f"Start: ({self.selected_shape.x1:.1f}, {self.selected_shape.y1:.1f})")
            
            # Draw control point
            x2 = self.selected_shape.x2*50
            y2 = (self.height() - self.selected_shape.y2*50)
            painter.setPen(QPen(Qt.blue, 2))
            painter.setBrush(QBrush(Qt.blue))
            painter.drawEllipse(QPointF(x2, y2), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(x2 + 8), int(y2 - 8), f"Control: ({self.selected_shape.x2:.1f}, {self.selected_shape.y2:.1f})")
            
            # Draw end point
            x3 = self.selected_shape.x3*50
            y3 = (self.height() - self.selected_shape.y3*50)
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(x3, y3), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(x3 + 8), int(y3 - 8), f"End: ({self.selected_shape.x3:.1f}, {self.selected_shape.y3:.1f})")
            
            # Draw control lines
            painter.setPen(QPen(Qt.gray, 1, Qt.DashLine))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            painter.drawLine(QPointF(x2, y2), QPointF(x3, y3))
        elif isinstance(self.selected_shape, TikzText):
            # Draw position point
            x = self.selected_shape.x * 50
            y = (self.height() - self.selected_shape.y * 50)
            
            # Position point
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(x, y), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(x + 8), int(y - 8), f"Pos: ({self.selected_shape.x:.1f}, {self.selected_shape.y:.1f})")
            
            # Draw text content
            painter.drawText(int(x + 8), int(y + 15), f"Text: {self.selected_shape.text}")
        elif isinstance(self.selected_shape, TikzDimension):
            # Draw start and end points
            x1 = self.selected_shape.x1 * 50
            y1 = (self.height() - self.selected_shape.y1 * 50)
            x2 = self.selected_shape.x2 * 50
            y2 = (self.height() - self.selected_shape.y2 * 50)
            
            # Start point
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(x1, y1), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(x1 + 8), int(y1 - 8), f"Start: ({self.selected_shape.x1:.1f}, {self.selected_shape.y1:.1f})")
            
            # End point
            painter.setPen(QPen(Qt.red, 2))
            painter.setBrush(QBrush(Qt.red))
            painter.drawEllipse(QPointF(x2, y2), point_size, point_size)
            painter.setPen(Qt.black)
            painter.drawText(int(x2 + 8), int(y2 - 8), f"End: ({self.selected_shape.x2:.1f}, {self.selected_shape.y2:.1f})")
            
            # Show dimension value
            painter.drawText(int(x2 + 8), int(y2 + 15), f"Value: {self.selected_shape.value:.2f}")
        
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self.mode == "move":
                # Check if clicked on a shape
                click_x = e.position().x()
                click_y = e.position().y()
                
                # Find the shape under the mouse (reverse order to select top-most)
                for shape in reversed(self.shapes):
                    if self.is_point_in_shape(click_x, click_y, shape):
                        self.selected_shape = shape
                        self.start = e.position()
                        self.current = e.position()
                        # Store original position for moving
                        self.move_start_pos = self.get_shape_position(shape)
                        break
            elif self.mode == "custom_polygon":
                # Add vertex for custom polygon
                x = e.position().x() / 50
                y = (self.height() - e.position().y()) / 50
                
                # Check if closing the polygon (click near first vertex)
                if len(self.custom_polygon_vertices) >= 3:
                    first_x, first_y = self.custom_polygon_vertices[0]
                    distance = ((x - first_x) ** 2 + (y - first_y) ** 2) ** 0.5
                    if distance < 0.2:  # Close enough to first vertex
                        # Create custom polygon
                        self.shapes.append(TikzCustomPolygon(self.custom_polygon_vertices, self.current_color, self.current_line_width, self.current_dashed, self.current_fill_color))
                        # Save history
                        self.save_history()
                        # Emit signal to update code and properties
                        self.shape_changed.emit()
                        # Clear vertices
                        self.custom_polygon_vertices = []
                    else:
                        # Add new vertex
                        self.custom_polygon_vertices.append((x, y))
                else:
                    # Add first few vertices
                    self.custom_polygon_vertices.append((x, y))
                self.update()
            else:
                # Clear selection when clicking on canvas in drawing mode
                self.selected_shape = None
                self.start = e.position()
            self.update()

    def mouseMoveEvent(self, e):
        if self.start:
            self.current = e.position()
            if self.mode == "move" and self.selected_shape:
                # Move the selected shape
                self.move_shape(self.selected_shape, self.start, self.current)
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.start:
            if self.mode == "move" and self.selected_shape:
                # Save history after moving
                self.save_history()
                self.shape_changed.emit()
            elif self.mode == "custom_polygon":
                # For custom polygon, we handle vertex addition in mousePressEvent
                pass
            else:
                end = e.position()
                s = self.start
                # Convert screen coordinates to TikZ coordinates (flip Y axis)
                x1, y1 = s.x()/50, (self.height() - s.y())/50
                x2, y2 = end.x()/50, (self.height() - end.y())/50

                if self.mode == "rect":
                    self.shapes.append(TikzRect(x1, y1, x2, y2, self.current_color, self.current_line_width, self.current_dashed, self.current_fill_color))
                elif self.mode == "circle":
                    r = ((x2-x1)**2 + (y2-y1)**2)**0.5
                    self.shapes.append(TikzCircle(x1, y1, r, self.current_color, self.current_line_width, self.current_dashed, self.current_fill_color))
                elif self.mode == "ellipse":
                    rx = abs(x2 - x1)
                    ry = abs(y2 - y1)
                    self.shapes.append(TikzEllipse(x1, y1, rx, ry, self.current_color, self.current_line_width, self.current_dashed, self.current_fill_color))
                elif self.mode == "triangle":
                    r = ((x2-x1)**2 + (y2-y1)**2)**0.5
                    self.shapes.append(TikzPolygon(x1, y1, r, 3, self.current_color, self.current_line_width, self.current_dashed, self.current_fill_color))
                elif self.mode == "pentagon":
                    r = ((x2-x1)**2 + (y2-y1)**2)**0.5
                    self.shapes.append(TikzPolygon(x1, y1, r, 5, self.current_color, self.current_line_width, self.current_dashed, self.current_fill_color))
                elif self.mode == "hexagon":
                    r = ((x2-x1)**2 + (y2-y1)**2)**0.5
                    self.shapes.append(TikzPolygon(x1, y1, r, 6, self.current_color, self.current_line_width, self.current_dashed, self.current_fill_color))
                elif self.mode == "line":
                    self.shapes.append(TikzLine(x1, y1, x2, y2, self.current_color, self.current_line_width, self.current_dashed))
                elif self.mode == "arrow":
                    self.shapes.append(TikzArrow(x1, y1, x2, y2, self.current_color, self.current_line_width, self.current_dashed))
                elif self.mode == "arc":
                    # Calculate center as midpoint
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    # Calculate radius
                    r = ((x2-x1)**2 + (y2-y1)**2)**0.5 / 2
                    # Calculate start and end angles
                    # Use y1 - cy and x1 - cx for start point (mouse press)
                    # Use y2 - cy and x2 - cx for end point (mouse release)
                    # Note: math.atan2(y, x) in Python uses (y, x) order
                    start_angle = math.degrees(math.atan2(y1 - cy, x1 - cx))
                    end_angle = math.degrees(math.atan2(y2 - cy, x2 - cx))
                    # Ensure end_angle > start_angle
                    if end_angle < start_angle:
                        end_angle += 360
                    # Adjust angles to match TikZ's coordinate system (flip Y axis)
                    start_angle = -start_angle
                    end_angle = -end_angle
                    self.shapes.append(TikzArc(x1, y1, r, start_angle, end_angle, self.current_color, self.current_line_width, self.current_dashed,cx,cy))
                elif self.mode == "elliptic_arc":
                    # Calculate center as midpoint
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    # Calculate radii
                    rx = abs(x2 - x1) / 2
                    ry = abs(y2 - y1) / 2
                    # Calculate start and end angles
                    # Use y1 - cy and x1 - cx for start point (mouse press)
                    # Use y2 - cy and x2 - cx for end point (mouse release)
                    start_angle = math.degrees(math.atan2(y1 - cy, x1 - cx))
                    end_angle = math.degrees(math.atan2(y2 - cy, x2 - cx))
                    # Ensure end_angle > start_angle
                    if end_angle < start_angle:
                        end_angle += 360
                    # Adjust angles to match TikZ's coordinate system (flip Y axis)
                    start_angle = -start_angle
                    end_angle = -end_angle
                    self.shapes.append(TikzEllipticArc(x1, y1, rx, ry, start_angle, end_angle, self.current_color, self.current_line_width, self.current_dashed, cx, cy))
                elif self.mode == "bezier":
                    # For bezier curve, we'll use a simple approach: start point, control point (midpoint), end point
                    # Start point: mouse press position
                    # Control point: midpoint between start and end
                    # End point: mouse release position
                    ctrl_x = (x1 + x2) / 2
                    ctrl_y = (y1 + y2) / 2
                    self.shapes.append(TikzBezier(x1, y1, ctrl_x, ctrl_y, x2, y2, self.current_color, self.current_line_width, self.current_dashed))
                elif self.mode == "text":
                    # For text, just use the click position
                    # Show a simple input dialog for text content
                    from PySide6.QtWidgets import QInputDialog
                    text, ok = QInputDialog.getText(self, "Text Input", "Enter text:")
                    if ok and text:
                        self.shapes.append(TikzText(x1, y1, text, self.current_color))
                elif self.mode == "dimension":
                    # Linear dimension: measure distance between two points
                    self.shapes.append(TikzDimension(x1, y1, x2, y2, offset=0.5, color=self.current_color))

                self.save_history()
                self.start = None
                self.current = None
                self.update()
                self.shape_changed.emit()


    def is_point_in_shape(self, x, y, shape):
        # Check if point (x, y) is inside the shape
        if isinstance(shape, TikzRect):
            # Convert to screen coordinates
            sx1 = shape.x1 * 50
            sy1 = (self.height() - shape.y1 * 50)
            sx2 = shape.x2 * 50
            sy2 = (self.height() - shape.y2 * 50)
            left = min(sx1, sx2)
            right = max(sx1, sx2)
            top = min(sy1, sy2)
            bottom = max(sy1, sy2)
            return left <= x <= right and top <= y <= bottom
        elif isinstance(shape, TikzCircle):
            cx = shape.cx * 50
            cy = (self.height() - shape.cy * 50)
            r = shape.r * 50
            distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            return distance <= r
        elif isinstance(shape, TikzEllipse):
            cx = shape.cx * 50
            cy = (self.height() - shape.cy * 50)
            rx = shape.rx * 50
            ry = shape.ry * 50
            # Check if point is inside ellipse
            return ((x - cx) ** 2) / (rx ** 2) + ((y - cy) ** 2) / (ry ** 2) <= 1
        elif isinstance(shape, TikzPolygon):
            # Check if point is inside polygon using ray casting algorithm
            cx = shape.cx * 50
            cy = (self.height() - shape.cy * 50)
            r = shape.radius * 50
            
            # Get polygon vertices
            vertices = []
            for i in range(shape.sides):
                angle = 2 * math.pi * i / shape.sides - math.pi / 2 + math.radians(shape.rotation)
                vx = cx + r * math.cos(angle)
                vy = cy - r * math.sin(angle)
                vertices.append((vx, vy))
            
            # Ray casting algorithm
            n = len(vertices)
            inside = False
            j = n - 1
            for i in range(n):
                xi, yi = vertices[i]
                xj, yj = vertices[j]
                if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                    inside = not inside
                j = i
            return inside
        elif isinstance(shape, TikzCustomPolygon):
            # Check if point is inside custom polygon using ray casting algorithm
            # Convert vertices to screen coordinates
            vertices = []
            for vertex in shape.vertices:
                vx = vertex[0] * 50
                vy = (self.height() - vertex[1] * 50)
                vertices.append((vx, vy))
            
            # Ray casting algorithm
            n = len(vertices)
            inside = False
            j = n - 1
            for i in range(n):
                xi, yi = vertices[i]
                xj, yj = vertices[j]
                if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                    inside = not inside
                j = i
            return inside
        elif isinstance(shape, TikzLine) or isinstance(shape, TikzArrow):
            # Check distance to line segment
            x1 = shape.x1 * 50
            y1 = (self.height() - shape.y1 * 50)
            x2 = shape.x2 * 50
            y2 = (self.height() - shape.y2 * 50)
            # Distance from point to line segment
            line_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            if line_length == 0:
                return False
            # Calculate distance
            t = max(0, min(1, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / (line_length ** 2)))
            projection_x = x1 + t * (x2 - x1)
            projection_y = y1 + t * (y2 - y1)
            distance = ((x - projection_x) ** 2 + (y - projection_y) ** 2) ** 0.5
            return distance <= 10  # 10 pixels tolerance
        elif isinstance(shape, TikzArc):
            # Check distance to arc
            cx = shape.cx1 * 50
            cy = (self.height() - shape.cy1 * 50)
            r = shape.r * 50
            # Calculate distance from point to center
            distance_to_center = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            # Check if point is on the arc (within tolerance)
            if abs(distance_to_center - r) <= 10:
                # Check if point is within the angle range
                angle = math.degrees(math.atan2(cy - y, x - cx))
                # Normalize angles
                start_angle = shape.start_angle % 360
                end_angle = shape.end_angle % 360
                angle = angle % 360
                if start_angle <= end_angle:
                    return start_angle <= angle <= end_angle
                else:
                    return angle >= start_angle or angle <= end_angle
            return False
        elif isinstance(shape, TikzEllipticArc):
            # Check distance to elliptical arc
            cx = shape.cx1 * 50
            cy = (self.height() - shape.cy1 * 50)
            rx = shape.rx * 50
            ry = shape.ry * 50
            # Calculate angle of point from center
            angle = math.degrees(math.atan2(cy - y, x - cx))
            # Normalize angles
            start_angle = shape.start_angle % 360
            end_angle = shape.end_angle % 360
            angle = angle % 360
            # Check if point is within the angle range
            if start_angle <= end_angle:
                if not (start_angle <= angle <= end_angle):
                    return False
            else:
                if not (angle >= start_angle or angle <= end_angle):
                    return False
            # Calculate distance from point to ellipse at this angle
            angle_rad = math.radians(angle)
            ellipse_x = cx + rx * math.cos(angle_rad)
            ellipse_y = cy - ry * math.sin(angle_rad)
            distance = ((x - ellipse_x) ** 2 + (y - ellipse_y) ** 2) ** 0.5
            return distance <= 10  # 10 pixels tolerance
        elif isinstance(shape, TikzText):
            # Check if point is near text position
            tx = shape.x * 50
            ty = (self.height() - shape.y * 50)
            distance = ((x - tx) ** 2 + (y - ty) ** 2) ** 0.5
            return distance <= 20  # 20 pixels tolerance
        elif isinstance(shape, TikzDimension):
            # Check if point is near either start or end point
            x1 = shape.x1 * 50
            y1 = (self.height() - shape.y1 * 50)
            x2 = shape.x2 * 50
            y2 = (self.height() - shape.y2 * 50)
            d1 = ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
            d2 = ((x - x2) ** 2 + (y - y2) ** 2) ** 0.5
            return d1 <= 15 or d2 <= 15
        return False

    def get_shape_position(self, shape):
        # Get position data for moving
        if isinstance(shape, TikzRect):
            return (shape.x1, shape.y1, shape.x2, shape.y2)
        elif isinstance(shape, TikzCircle):
            return (shape.cx, shape.cy)
        elif isinstance(shape, TikzEllipse):
            return (shape.cx, shape.cy)
        elif isinstance(shape, TikzLine) or isinstance(shape, TikzArrow):
            return (shape.x1, shape.y1, shape.x2, shape.y2)
        elif isinstance(shape, TikzArc):
            return (shape.cx, shape.cy)
        elif isinstance(shape, TikzEllipticArc):
            return (shape.cx, shape.cy)
        return None

    def move_shape(self, shape, start_pos, current_pos):
        # Move shape by the difference between start and current positions
        dx = (current_pos.x() - start_pos.x()) / 50
        dy = -(current_pos.y() - start_pos.y()) / 50  # Flip Y axis
        
        if isinstance(shape, TikzRect):
            shape.x1 += dx
            shape.y1 += dy
            shape.x2 += dx
            shape.y2 += dy
        elif isinstance(shape, TikzCircle):
            shape.cx += dx
            shape.cy += dy
        elif isinstance(shape, TikzEllipse):
            shape.cx += dx
            shape.cy += dy
        elif isinstance(shape, TikzArc):
            shape.cx += dx
            shape.cy += dy
        elif isinstance(shape, TikzEllipticArc):
            shape.cx += dx
            shape.cy += dy
        elif isinstance(shape, TikzBezier):
            shape.x1 += dx
            shape.y1 += dy
            shape.x2 += dx
            shape.y2 += dy
            shape.x3 += dx
            shape.y3 += dy
        elif isinstance(shape, TikzPolygon):
            shape.cx += dx
            shape.cy += dy
        elif isinstance(shape, TikzCustomPolygon):
            # Move all vertices of the custom polygon
            new_vertices = []
            for vertex in shape.vertices:
                new_x = vertex[0] + dx
                new_y = vertex[1] + dy
                new_vertices.append((new_x, new_y))
            shape.vertices = new_vertices
        elif isinstance(shape, TikzLine) or isinstance(shape, TikzArrow):
            shape.x1 += dx
            shape.y1 += dy
            shape.x2 += dx
            shape.y2 += dy
        elif isinstance(shape, TikzText):
            shape.x += dx
            shape.y += dy
        elif isinstance(shape, TikzDimension):
            shape.x1 += dx
            shape.y1 += dy
            shape.x2 += dx
            shape.y2 += dy
        # Update start position for next move
        self.start = current_pos
        
        # Emit signal to update properties panel
        self.shape_moved.emit()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), Qt.white)

        # Draw grid lines
        p.setPen(QPen(Qt.lightGray, 0.5))
        grid_size = 10  # 25 pixels = 0.5 TikZ units (denser grid)
        
        # Draw vertical grid lines
        for x in range(0, self.width(), grid_size):
            p.drawLine(x, 0, x, self.height())
        
        # Draw horizontal grid lines
        for y in range(0, self.height(), grid_size):
            p.drawLine(0, y, self.width(), y)

        # Drawn shapes
        for s in self.shapes:
            # Set shape properties
            color = QColor(s.color)
            p.setPen(QPen(color, s.line_width))
            
            if s.dashed:
                pen = p.pen()
                pen.setStyle(Qt.DashLine)
                p.setPen(pen)
            
            if isinstance(s, TikzRect):
                # Convert TikZ coordinates back to screen coordinates (flip Y axis)
                x1 = s.x1*50
                y1 = (self.height() - s.y1*50)
                x2 = s.x2*50
                y2 = (self.height() - s.y2*50)
                
                # Set fill color if specified
                if s.fill_color != "none":
                    fill_color = QColor(s.fill_color)
                    p.setBrush(QBrush(fill_color))
                else:
                    p.setBrush(Qt.NoBrush)
                
                # Draw rounded rectangle if corner_radius > 0
                if s.corner_radius > 0:
                    rect = QRectF(min(x1, x2), min(y1, y2), abs(x2-x1), abs(y2-y1))
                    p.drawRoundedRect(rect, s.corner_radius, s.corner_radius, Qt.AbsoluteSize)
                else:
                    p.drawRect(QRectF(min(x1, x2), min(y1, y2), abs(x2-x1), abs(y2-y1)))
            elif isinstance(s, TikzCircle):
                cx = s.cx*50
                cy = (self.height() - s.cy*50)
                
                # Set fill color if specified
                if s.fill_color != "none":
                    fill_color = QColor(s.fill_color)
                    p.setBrush(QBrush(fill_color))
                else:
                    p.setBrush(Qt.NoBrush)
                
                p.drawEllipse(QPointF(cx, cy), s.r*50, s.r*50)
            elif isinstance(s, TikzEllipse):
                cx = s.cx*50
                cy = (self.height() - s.cy*50)
                
                # Set fill color if specified
                if s.fill_color != "none":
                    fill_color = QColor(s.fill_color)
                    p.setBrush(QBrush(fill_color))
                else:
                    p.setBrush(Qt.NoBrush)
                
                p.drawEllipse(QPointF(cx, cy), s.rx*50, s.ry*50)
            elif isinstance(s, TikzPolygon):
                # Calculate vertices for polygon
                vertices = []
                for i in range(s.sides):
                    angle = 2 * math.pi * i / s.sides - math.pi / 2 + math.radians(s.rotation)
                    x = s.cx*50 + s.radius*50 * math.cos(angle)
                    y = (self.height() - s.cy*50) - s.radius*50 * math.sin(angle)
                    vertices.append(QPointF(x, y))
                
                # Set fill color if specified
                if s.fill_color != "none":
                    fill_color = QColor(s.fill_color)
                    p.setBrush(QBrush(fill_color))
                else:
                    p.setBrush(Qt.NoBrush)
                
                # Draw polygon
                p.drawPolygon(QPolygonF(vertices))
            elif isinstance(s, TikzLine):
                x1 = s.x1*50
                y1 = (self.height() - s.y1*50)
                x2 = s.x2*50
                y2 = (self.height() - s.y2*50)
                p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            elif isinstance(s, TikzArrow):
                x1 = s.x1*50
                y1 = (self.height() - s.y1*50)
                x2 = s.x2*50
                y2 = (self.height() - s.y2*50)
                p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
                # Simple arrowhead
                p.drawLine(QPointF(x2, y2), QPointF(x2-3, y2-3))
                p.drawLine(QPointF(x2, y2), QPointF(x2-3, y2+3))
            elif isinstance(s, TikzArc):
                cx = s.cx1*50
                cy = (self.height() - s.cy1*50)
                r = s.r*50
                # The stored angles are adjusted for TikZ, so we need to convert them for canvas drawing
                # TikZ uses (x, y) with y increasing upward
                # Canvas uses (x, y) with y increasing downward
                # Convert angles to canvas coordinate system
                canvas_start_angle = -s.start_angle
                canvas_end_angle = -s.end_angle
                # Convert angles to 1/16 of a degree for drawArc
                start_angle = int(canvas_start_angle * 16)
                end_angle = int(canvas_end_angle * 16)
                # Calculate sweep angle (positive for clockwise in Qt's drawArc)
                sweep_angle = end_angle - start_angle
                if sweep_angle < 0:
                    sweep_angle += 64 * 360  # 64 = 16 * 4 (full circle)
                # Draw arc using drawArc (no extra line)
                rect = QRectF(cx - r, cy - r, 2 * r, 2 * r)
                p.drawArc(rect, start_angle, sweep_angle)
            elif isinstance(s, TikzEllipticArc):
                cx = s.cx1*50
                cy = (self.height() - s.cy1*50)
                rx = s.rx*50
                ry = s.ry*50
                # The stored angles are adjusted for TikZ, so we need to convert them for canvas drawing
                # TikZ uses (x, y) with y increasing upward
                # Canvas uses (x, y) with y increasing downward
                # Convert angles to canvas coordinate system
                canvas_start_angle = -s.start_angle
                canvas_end_angle = -s.end_angle
                # Convert angles from degrees to radians
                start_angle_rad = math.radians(canvas_start_angle)
                end_angle_rad = math.radians(canvas_end_angle)
                # Calculate points along the elliptical arc
                path = QPainterPath()
                # Calculate start point
                start_x = cx + rx * math.cos(start_angle_rad)
                start_y = cy - ry * math.sin(start_angle_rad)
                path.moveTo(start_x, start_y)
                # Draw elliptical arc using multiple segments in correct direction
                steps = max(10, abs(int(canvas_end_angle - canvas_start_angle)))
                for i in range(1, steps + 1):
                    # Calculate angle in correct direction
                    angle = start_angle_rad + (end_angle_rad - start_angle_rad) * i / steps
                    x = cx + rx * math.cos(angle)
                    y = cy - ry * math.sin(angle)
                    path.lineTo(x, y)
                p.drawPath(path)
            elif isinstance(s, TikzBezier):
                # Draw Bezier curve
                x1 = s.x1*50
                y1 = (self.height() - s.y1*50)
                x2 = s.x2*50
                y2 = (self.height() - s.y2*50)
                x3 = s.x3*50
                y3 = (self.height() - s.y3*50)
                
                path = QPainterPath()
                path.moveTo(x1, y1)
                path.quadTo(x2, y2, x3, y3)
                p.drawPath(path)
            elif isinstance(s, TikzText):
                # Draw text
                x = s.x * 50
                y = (self.height() - s.y * 50)
                
                # Set font
                font = QFont()
                font.setPointSize(s.font_size)
                p.setFont(font)
                
                # Set color
                color = QColor(s.color)
                p.setPen(QPen(color))
                
                # Calculate text position based on anchor
                metrics = p.fontMetrics()
                text_width = metrics.horizontalAdvance(s.text)
                text_height = metrics.height()
                
                if s.anchor == "center":
                    text_x = x - text_width / 2
                    text_y = y + text_height / 4  # Adjust for baseline
                elif s.anchor == "right":
                    text_x = x - text_width
                    text_y = y + text_height / 4
                else:  # left
                    text_x = x
                    text_y = y + text_height / 4
                
                p.drawText(int(text_x), int(text_y), s.text)
            elif isinstance(s, TikzCustomPolygon):
                # Draw custom polygon
                vertices = []
                for vertex in s.vertices:
                    x = vertex[0] * 50
                    y = (self.height() - vertex[1] * 50)
                    vertices.append(QPointF(x, y))
                
                # Set fill color if specified
                if s.fill_color != "none":
                    fill_color = QColor(s.fill_color)
                    p.setBrush(QBrush(fill_color))
                else:
                    p.setBrush(Qt.NoBrush)
                
                # Draw polygon
                p.drawPolygon(QPolygonF(vertices))
            elif isinstance(s, TikzDimension):
                # Draw linear dimension annotation
                x1 = s.x1 * 50
                y1 = (self.height() - s.y1 * 50)
                x2 = s.x2 * 50
                y2 = (self.height() - s.y2 * 50)
                
                # Calculate offset direction (perpendicular to the line)
                dx = x2 - x1
                dy = y2 - y1
                length = math.sqrt(dx**2 + dy**2)
                offset_pixels = s.offset * 50
                
                if length > 0:
                    # In screen coordinates, y increases downward
                    # For the same visual offset as in TikZ (where y increases upward),
                    # we need to flip the sign of dy in the perpendicular calculation
                    perp_x = dy / length * offset_pixels
                    perp_y = dx / length * offset_pixels
                else:
                    perp_x, perp_y = 0, offset_pixels
                
                # Extension line points
                ext1_x = x1 + perp_x
                ext1_y = y1 + perp_y
                ext2_x = x2 + perp_x
                ext2_y = y2 + perp_y
                
                # Draw extension lines
                color = QColor(s.color)
                p.setPen(QPen(color, s.line_width))
                p.drawLine(QPointF(x1, y1), QPointF(ext1_x, ext1_y))
                p.drawLine(QPointF(x2, y2), QPointF(ext2_x, ext2_y))
                
                # Draw dimension line with arrows
                p.drawLine(QPointF(ext1_x, ext1_y), QPointF(ext2_x, ext2_y))
                
                # Draw arrowheads
                arrow_size = 5
                angle = math.atan2(ext2_y - ext1_y, ext2_x - ext1_x)
                # Left arrow
                p.drawLine(QPointF(ext1_x, ext1_y), 
                          QPointF(ext1_x + arrow_size * math.cos(angle + math.pi/6), 
                                 ext1_y + arrow_size * math.sin(angle + math.pi/6)))
                p.drawLine(QPointF(ext1_x, ext1_y), 
                          QPointF(ext1_x + arrow_size * math.cos(angle - math.pi/6), 
                                 ext1_y + arrow_size * math.sin(angle - math.pi/6)))
                # Right arrow
                p.drawLine(QPointF(ext2_x, ext2_y), 
                          QPointF(ext2_x - arrow_size * math.cos(angle + math.pi/6), 
                                 ext2_y - arrow_size * math.sin(angle + math.pi/6)))
                p.drawLine(QPointF(ext2_x, ext2_y), 
                          QPointF(ext2_x - arrow_size * math.cos(angle - math.pi/6), 
                                 ext2_y - arrow_size * math.sin(angle - math.pi/6)))
                
                # Draw text label
                mid_x = (ext1_x + ext2_x) / 2
                mid_y = (ext1_y + ext2_y) / 2
                text_color = QColor(s.text_color)
                p.setPen(QPen(text_color))
                font = QFont()
                font.setPointSize(10)
                p.setFont(font)
                value_str = f"{s.value:.2f}"
                metrics = p.fontMetrics()
                text_width = metrics.horizontalAdvance(value_str)
                p.drawText(int(mid_x - text_width/2), int(mid_y - 5), value_str)

        # Draw control points for selected shape
        if self.selected_shape:
            self.draw_control_points(p)

        # Dragging
        if self.start and self.current:
            p.setPen(Qt.gray)
            sx, sy = self.start.x(), self.start.y()
            ex, ey = self.current.x(), self.current.y()
            if self.mode == "rect":
                p.drawRect(QRectF(sx, sy, ex-sx, ey-sy))
            elif self.mode == "circle":
                r = ((ex-sx)**2 + (ey-sy)**2)**0.5
                p.drawEllipse(QPointF(sx, sy), r, r)
            elif self.mode == "ellipse":
                rx = abs(ex - sx)
                ry = abs(ey - sy)
                p.drawEllipse(QPointF(sx, sy), rx, ry)
            elif self.mode in ["triangle", "pentagon", "hexagon"]:
                r = ((ex-sx)**2 + (ey-sy)**2)**0.5
                sides = 3 if self.mode == "triangle" else (5 if self.mode == "pentagon" else 6)
                vertices = []
                for i in range(sides):
                    angle = 2 * math.pi * i / sides - math.pi / 2
                    x = sx + r * math.cos(angle)
                    y = sy - r * math.sin(angle)
                    vertices.append(QPointF(x, y))
                p.drawPolygon(QPolygonF(vertices))
            elif self.mode in ["line", "arrow","dimension"]:
                p.drawLine(QPointF(sx, sy), QPointF(ex, ey))
            elif self.mode == "arc":
                p.drawLine(QPointF(sx, sy), QPointF(ex, ey))
        
        # Draw custom polygon vertices and preview
        if self.mode == "custom_polygon" and self.custom_polygon_vertices:
            # Draw lines between vertices
            p.setPen(QPen(Qt.black, 2))
            for i in range(1, len(self.custom_polygon_vertices)):
                x1 = self.custom_polygon_vertices[i-1][0] * 50
                y1 = (self.height() - self.custom_polygon_vertices[i-1][1] * 50)
                x2 = self.custom_polygon_vertices[i][0] * 50
                y2 = (self.height() - self.custom_polygon_vertices[i][1] * 50)
                p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
            # Draw vertices
            p.setPen(QPen(Qt.red, 2))
            p.setBrush(QBrush(Qt.red))
            for vertex in self.custom_polygon_vertices:
                x = vertex[0] * 50
                y = (self.height() - vertex[1] * 50)
                p.drawEllipse(QPointF(x, y), 3, 3)
            
            # Draw preview line from last vertex to current mouse position
            if self.current:
                last_vertex = self.custom_polygon_vertices[-1]
                x1 = last_vertex[0] * 50
                y1 = (self.height() - last_vertex[1] * 50)
                x2 = self.current.x()
                y2 = self.current.y()
                p.setPen(QPen(Qt.gray, 1, Qt.DashLine))
                p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def clear_all(self):
        self.save_history()
        self.shapes.clear()
        self.update()
        self.shape_changed.emit()

    def save_history(self):
        # Save current state to history
        if len(self.history) > self.history_index + 1:
            # Remove future history if we're not at the end
            self.history = self.history[:self.history_index + 1]
        
        # Save current state (deep copy)
        current_state = []
        for shape in self.shapes:
            if isinstance(shape, TikzRect):
                current_state.append(("rect", shape.x1, shape.y1, shape.x2, shape.y2, 
                                  shape.color, shape.line_width, shape.dashed, shape.fill_color, shape.corner_radius))
            elif isinstance(shape, TikzCircle):
                current_state.append(("circle", shape.cx, shape.cy, shape.r,
                                  shape.color, shape.line_width, shape.dashed, shape.fill_color))
            elif isinstance(shape, TikzEllipse):
                current_state.append(("ellipse", shape.cx, shape.cy, shape.rx, shape.ry,
                                  shape.color, shape.line_width, shape.dashed, shape.fill_color))
            elif isinstance(shape, TikzPolygon):
                current_state.append(("polygon", shape.cx, shape.cy, shape.radius, shape.sides,
                                  shape.color, shape.line_width, shape.dashed, shape.fill_color, shape.rotation))
            elif isinstance(shape, TikzLine):
                current_state.append(("line", shape.x1, shape.y1, shape.x2, shape.y2,
                                  shape.color, shape.line_width, shape.dashed))
            elif isinstance(shape, TikzArrow):
                current_state.append(("arrow", shape.x1, shape.y1, shape.x2, shape.y2,
                                  shape.color, shape.line_width, shape.dashed))
            elif isinstance(shape, TikzArc):
                current_state.append(("arc", shape.cx, shape.cy, shape.r, shape.start_angle, shape.end_angle,
                                  shape.color, shape.line_width, shape.dashed))
            elif isinstance(shape, TikzEllipticArc):
                current_state.append(("elliptic_arc", shape.cx, shape.cy, shape.rx, shape.ry, shape.start_angle, shape.end_angle,
                                  shape.color, shape.line_width, shape.dashed))
            elif isinstance(shape, TikzBezier):
                current_state.append(("bezier", shape.x1, shape.y1, shape.x2, shape.y2, shape.x3, shape.y3,
                                  shape.color, shape.line_width, shape.dashed))
            elif isinstance(shape, TikzText):
                current_state.append(("text", shape.x, shape.y, shape.text,
                                  shape.color, shape.font_size, shape.anchor))
            elif isinstance(shape, TikzDimension):
                current_state.append(("dimension", shape.x1, shape.y1, shape.x2, shape.y2, shape.offset,
                                  shape.color, shape.line_width, shape.text_color))
        
        self.history.append(current_state)
        self.history_index += 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.restore_from_history()

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.restore_from_history()

    def restore_from_history(self):
        # Restore state from history
        if 0 <= self.history_index < len(self.history):
            self.shapes.clear()
            state = self.history[self.history_index]
            for item in state:
                shape_type = item[0]
                if shape_type == "rect":
                    self.shapes.append(TikzRect(item[1], item[2], item[3], item[4],
                                            item[5], item[6], item[7], item[8], item[9]))
                elif shape_type == "circle":
                    self.shapes.append(TikzCircle(item[1], item[2], item[3],
                                             item[4], item[5], item[6], item[7], item[8]))
                elif shape_type == "ellipse":
                    self.shapes.append(TikzEllipse(item[1], item[2], item[3], item[4],
                                              item[5], item[6], item[7], item[8]))
                elif shape_type == "polygon":
                    self.shapes.append(TikzPolygon(item[1], item[2], item[3], item[4],
                                               item[5], item[6], item[7], item[8], item[9]))
                elif shape_type == "line":
                    self.shapes.append(TikzLine(item[1], item[2], item[3], item[4],
                                            item[5], item[6], item[7]))
                elif shape_type == "arrow":
                    self.shapes.append(TikzArrow(item[1], item[2], item[3], item[4],
                                             item[5], item[6], item[7]))
                elif shape_type == "arc":
                    self.shapes.append(TikzArc(item[1], item[2], item[3], item[4], item[5],
                                         item[6], item[7], item[8]))
                elif shape_type == "elliptic_arc":
                    self.shapes.append(TikzEllipticArc(item[1], item[2], item[3], item[4], item[5], item[6],
                                                item[7], item[8], item[9]))
                elif shape_type == "bezier":
                    self.shapes.append(TikzBezier(item[1], item[2], item[3], item[4], item[5], item[6],
                                         item[7], item[8], item[9]))
                elif shape_type == "text":
                    self.shapes.append(TikzText(item[1], item[2], item[3],
                                         item[4], item[5], item[6]))
                elif shape_type == "dimension":
                    self.shapes.append(TikzDimension(item[1], item[2], item[3], item[4], item[5],
                                         item[6], item[7], item[8]))
            self.update()
            self.shape_changed.emit()

# ======================== Main Window ========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LaTeX Tikz Design Tool")
        self.resize(1000, 600)

        main = QWidget()
        self.setCentralWidget(main)
        layout = QHBoxLayout(main)

        # Left side: Toolbar (vertical) + Canvas
        left = QHBoxLayout()
        
        # Create vertical toolbar on the left
        toolbar = QVBoxLayout()
        toolbar.setSpacing(5)
        
        # Create buttons with text (large size)
        self.btn_rect = QPushButton("▭")
        self.btn_rect.setToolTip("Rectangle")
        self.btn_rect.setFixedSize(50, 50)
        font = self.btn_rect.font()
        font.setPointSize(16)
        self.btn_rect.setFont(font)
        
        self.btn_circle = QPushButton("○")
        self.btn_circle.setToolTip("Circle")
        self.btn_circle.setFixedSize(50, 50)
        font = self.btn_circle.font()
        font.setPointSize(16)
        self.btn_circle.setFont(font)
        
        self.btn_ellipse = QPushButton("⬭")
        self.btn_ellipse.setToolTip("Ellipse")
        self.btn_ellipse.setFixedSize(50, 50)
        font = self.btn_ellipse.font()
        font.setPointSize(16)
        self.btn_ellipse.setFont(font)
        
        self.btn_triangle = QPushButton("△")
        self.btn_triangle.setToolTip("Triangle")
        self.btn_triangle.setFixedSize(50, 50)
        font = self.btn_triangle.font()
        font.setPointSize(16)
        self.btn_triangle.setFont(font)
        
        self.btn_pentagon = QPushButton("⬟")
        self.btn_pentagon.setToolTip("Pentagon")
        self.btn_pentagon.setFixedSize(50, 50)
        font = self.btn_pentagon.font()
        font.setPointSize(16)
        self.btn_pentagon.setFont(font)
        
        self.btn_hexagon = QPushButton("⬣")
        self.btn_hexagon.setToolTip("Hexagon")
        self.btn_hexagon.setFixedSize(50, 50)
        font = self.btn_hexagon.font()
        font.setPointSize(16)
        self.btn_hexagon.setFont(font)
        
        self.btn_line = QPushButton("—")
        self.btn_line.setToolTip("Line")
        self.btn_line.setFixedSize(50, 50)
        font = self.btn_line.font()
        font.setPointSize(16)
        self.btn_line.setFont(font)
        
        self.btn_arrow = QPushButton("→")
        self.btn_arrow.setToolTip("Arrow")
        self.btn_arrow.setFixedSize(50, 50)
        font = self.btn_arrow.font()
        font.setPointSize(16)
        self.btn_arrow.setFont(font)
        
        self.btn_arc = QPushButton("⌒")
        self.btn_arc.setToolTip("Arc")
        self.btn_arc.setFixedSize(50, 50)
        font = self.btn_arc.font()
        font.setPointSize(16)
        self.btn_arc.setFont(font)
        
        self.btn_elliptic_arc = QPushButton("⬭")
        self.btn_elliptic_arc.setToolTip("Elliptic Arc")
        self.btn_elliptic_arc.setFixedSize(50, 50)
        font = self.btn_elliptic_arc.font()
        font.setPointSize(16)
        self.btn_elliptic_arc.setFont(font)
        
        self.btn_bezier = QPushButton("~")
        self.btn_bezier.setToolTip("Bezier")
        self.btn_bezier.setFixedSize(50, 50)
        font = self.btn_bezier.font()
        font.setPointSize(16)
        self.btn_bezier.setFont(font)
        
        self.btn_text = QPushButton("T")
        self.btn_text.setToolTip("Text")
        self.btn_text.setFixedSize(50, 50)
        font = self.btn_text.font()
        font.setPointSize(16)
        self.btn_text.setFont(font)
        
        self.btn_dimension = QPushButton("|")
        self.btn_dimension.setToolTip("Dimension")
        self.btn_dimension.setFixedSize(50, 50)
        font = self.btn_dimension.font()
        font.setPointSize(16)
        self.btn_dimension.setFont(font)
        
        self.btn_custom_polygon = QPushButton("✎")
        self.btn_custom_polygon.setToolTip("Custom Polygon")
        self.btn_custom_polygon.setFixedSize(50, 50)
        font = self.btn_custom_polygon.font()
        font.setPointSize(16)
        self.btn_custom_polygon.setFont(font)
        
        self.btn_move = QPushButton("Move")
        self.btn_clear = QPushButton("Clear")

        # Add all buttons vertically
        toolbar.addWidget(self.btn_rect)
        toolbar.addWidget(self.btn_circle)
        toolbar.addWidget(self.btn_ellipse)
        toolbar.addWidget(self.btn_triangle)
        toolbar.addWidget(self.btn_pentagon)
        toolbar.addWidget(self.btn_hexagon)
        toolbar.addWidget(self.btn_line)
        toolbar.addWidget(self.btn_arrow)
        toolbar.addWidget(self.btn_arc)
        toolbar.addWidget(self.btn_elliptic_arc)
        toolbar.addWidget(self.btn_bezier)
        toolbar.addWidget(self.btn_text)
        toolbar.addWidget(self.btn_dimension)
        toolbar.addWidget(self.btn_custom_polygon)
        toolbar.addStretch()

        # Create canvas area
        canvas_area = QVBoxLayout()
        self.canvas = Canvas()
        
        # Create floating Move button
        self.btn_move.setFixedSize(80, 30)
        self.btn_move.setParent(self.canvas)
        
        # Create floating Clear button
        self.btn_clear.setFixedSize(80, 30)
        self.btn_clear.setParent(self.canvas)
        
        # Update button positions when canvas is resized
        self.canvas.resizeEvent = lambda event: self.update_floating_buttons_position(event)
        
        # Update button positions when window is shown
        self.showEvent = lambda event: self.update_floating_buttons_position(None)
        
        # Show buttons
        self.btn_move.show()
        self.btn_clear.show()
        
        # Add canvas to layout
        canvas_area.addWidget(self.canvas, 1)

        left.addLayout(toolbar)
        left.addLayout(canvas_area, 1)  # Canvas area takes remaining space

        # Middle: Properties panel
        middle = QVBoxLayout()
        
        middle.addWidget(QLabel("Properties"))
        
        # Shape list
        list_group = QVBoxLayout()
        list_label = QLabel("Shapes:")
        self.shape_list = QListWidget()
        self.shape_list.currentRowChanged.connect(self.on_shape_selected)
        list_group.addWidget(list_label)
        list_group.addWidget(self.shape_list)
        
        # Color controls
        color_group = QVBoxLayout()
        color_label = QLabel("Line Color:")
        self.color_combo = QComboBox()
        self.color_combo.addItems(["black", "red", "blue", "green", "yellow", "orange", "purple", "brown", "pink", "gray"])
        self.color_combo.setCurrentText("black")
        self.color_combo.currentTextChanged.connect(self.apply_properties)
        color_group.addWidget(color_label)
        color_group.addWidget(self.color_combo)
        
        # Fill color controls
        fill_group = QVBoxLayout()
        fill_label = QLabel("Fill Color:")
        self.fill_combo = QComboBox()
        self.fill_combo.addItems(["none", "red", "blue", "green", "yellow", "orange", "purple", "brown", "pink", "gray", "lightblue", "lightgreen", "lightyellow"])
        self.fill_combo.setCurrentText("none")
        self.fill_combo.currentTextChanged.connect(self.apply_properties)
        fill_group.addWidget(fill_label)
        fill_group.addWidget(self.fill_combo)
        
        # Line width controls
        width_group = QVBoxLayout()
        width_label = QLabel("Line Width:")
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10)
        self.width_spin.setValue(1)
        self.width_spin.valueChanged.connect(self.apply_properties)
        width_group.addWidget(width_label)
        width_group.addWidget(self.width_spin)
        
        # Dashed line controls
        dashed_group = QVBoxLayout()
        self.dashed_check = QCheckBox("Dashed Line")
        self.dashed_check.stateChanged.connect(self.apply_properties)
        dashed_group.addWidget(self.dashed_check)
        
        # Corner radius controls (for rectangles)
        radius_group = QVBoxLayout()
        radius_label = QLabel("Corner Radius:")
        self.radius_spin = QDoubleSpinBox()
        self.radius_spin.setRange(0, 50)
        self.radius_spin.setSingleStep(1)
        self.radius_spin.setValue(0)
        self.radius_spin.valueChanged.connect(self.apply_properties)
        radius_group.addWidget(radius_label)
        radius_group.addWidget(self.radius_spin)
        
        # Coordinate and size display
        coord_group = QVBoxLayout()
        coord_label = QLabel("Selected Shape:")
        self.coord_label = QLabel("No selection")
        self.coord_label.setStyleSheet("border: 1px solid gray; padding: 5px;")
        coord_group.addWidget(coord_label)
        coord_group.addWidget(self.coord_label)
        
        # Position controls
        position_group = QVBoxLayout()
        position_label = QLabel("Position:")
        
        # X1, Y1 controls
        x1y1_layout = QHBoxLayout()
        self.x1_label = QLabel("X1:")
        self.x1_spin = QDoubleSpinBox()
        self.x1_spin.setRange(-100, 100)
        self.x1_spin.setSingleStep(0.1)
        self.x1_spin.setValue(0)
        self.x1_spin.valueChanged.connect(self.apply_properties)
        x1y1_layout.addWidget(self.x1_label)
        x1y1_layout.addWidget(self.x1_spin)
        
        self.y1_label = QLabel("Y1:")
        self.y1_spin = QDoubleSpinBox()
        self.y1_spin.setRange(-100, 100)
        self.y1_spin.setSingleStep(0.1)
        self.y1_spin.setValue(0)
        self.y1_spin.valueChanged.connect(self.apply_properties)
        x1y1_layout.addWidget(self.y1_label)
        x1y1_layout.addWidget(self.y1_spin)
        
        # X2, Y2 controls
        x2y2_layout = QHBoxLayout()
        self.x2_label = QLabel("X2:")
        self.x2_spin = QDoubleSpinBox()
        self.x2_spin.setRange(-100, 100)
        self.x2_spin.setSingleStep(0.1)
        self.x2_spin.setValue(1)
        self.x2_spin.valueChanged.connect(self.apply_properties)
        x2y2_layout.addWidget(self.x2_label)
        x2y2_layout.addWidget(self.x2_spin)
        
        self.y2_label = QLabel("Y2:")
        self.y2_spin = QDoubleSpinBox()
        self.y2_spin.setRange(-100, 100)
        self.y2_spin.setSingleStep(0.1)
        self.y2_spin.setValue(1)
        self.y2_spin.valueChanged.connect(self.apply_properties)
        x2y2_layout.addWidget(self.y2_label)
        x2y2_layout.addWidget(self.y2_spin)
        
        position_group.addWidget(position_label)
        position_group.addLayout(x1y1_layout)
        position_group.addLayout(x2y2_layout)
        
        # Hide position controls initially
        self.x1_label.setVisible(False)
        self.x1_spin.setVisible(False)
        self.y1_label.setVisible(False)
        self.y1_spin.setVisible(False)
        self.x2_label.setVisible(False)
        self.x2_spin.setVisible(False)
        self.y2_label.setVisible(False)
        self.y2_spin.setVisible(False)
        
        # Delete button
        delete_group = QVBoxLayout()
        self.delete_shape_button = QPushButton("Delete Shape")
        self.delete_shape_button.clicked.connect(self.delete_selected_shape)
        delete_group.addWidget(self.delete_shape_button)
        
        middle.addLayout(list_group)
        middle.addLayout(color_group)
        middle.addLayout(fill_group)
        middle.addLayout(width_group)
        middle.addLayout(dashed_group)
        middle.addLayout(radius_group)
        middle.addLayout(coord_group)
        middle.addLayout(position_group)
        middle.addLayout(delete_group)
        middle.addStretch()

        # Right side: Code
        right = QVBoxLayout()
        
        # Add ad container
        ad_container = QWidget()
        ad_container.setCursor(Qt.PointingHandCursor)
        ad_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 12px;
                padding: 5px;
            }
            QLabel {
                color: white;
            }
        """)
        ad_container.setFixedSize(280, 90)
        ad_container.mousePressEvent = lambda e: self.open_ad_link()
        ad_layout = QHBoxLayout(ad_container)
        ad_layout.setContentsMargins(8, 5, 8, 5)
        ad_layout.setSpacing(8)
        
        self.ad_image_label = QLabel()
        self.ad_image_label.setFixedSize(70, 70)
        self.ad_image_label.setStyleSheet("background-color: white; border-radius: 8px;")
        self.ad_image_label.setAlignment(Qt.AlignCenter)
        ad_layout.addWidget(self.ad_image_label)
        
        self.load_ad_image()
        
        ad_text_layout = QVBoxLayout()
        ad_text_layout.setSpacing(2)
        
        ad_title = QLabel('<a href="#" style="text-decoration:none; color:#FFD700;">★ Discount now !</a>')
        ad_title.setFont(QFont("Arial", 12, QFont.Bold))
        ad_title.setStyleSheet("color: #FFD700; font-weight: bold;")
        ad_title.setTextFormat(Qt.RichText)
        ad_text_layout.addWidget(ad_title)
        
        ad_subtitle = QLabel("Visual LaTeX Document Quick Writer ")
        ad_subtitle.setFont(QFont("Arial", 8))
        ad_subtitle.setStyleSheet("color: #FFFFFF;")
        ad_text_layout.addWidget(ad_subtitle)
        
        ad_slogan = QLabel("✨ Click to get it!")
        ad_slogan_font = QFont("Arial", 8)
        ad_slogan_font.setItalic(True)
        ad_slogan.setFont(ad_slogan_font)
        ad_slogan.setStyleSheet("color: #E0E0E0; font-style: italic;")
        ad_text_layout.addWidget(ad_slogan)
        
        ad_layout.addLayout(ad_text_layout)
        right.addWidget(ad_container)
        
        # Add package text box
        right.addWidget(QLabel("TikZ Code"))
        package_edit = QTextEdit()
        package_edit.setPlainText("\\usepackage{tikz}")
        package_edit.setReadOnly(True)
        package_edit.setMaximumHeight(30)
        right.addWidget(package_edit)
        # Add TikZ code section
        self.code_edit = QTextEdit()
        self.code_edit.setReadOnly(True)
        right.addWidget(self.code_edit)
        
        # Copy button
        self.copy_button = QPushButton("Copy Code")
        self.copy_button.clicked.connect(self.copy_code)
        right.addWidget(self.copy_button)

        layout.addLayout(left, 3)
        layout.addLayout(middle, 1)
        layout.addLayout(right, 1)

        # Create menu bar after all UI elements are created
        self.create_menu_bar()

        # Connections
        self.btn_rect.clicked.connect(lambda: self.canvas.set_mode("rect"))
        self.btn_circle.clicked.connect(lambda: self.canvas.set_mode("circle"))
        self.btn_ellipse.clicked.connect(lambda: self.canvas.set_mode("ellipse"))
        self.btn_triangle.clicked.connect(lambda: self.canvas.set_mode("triangle"))
        self.btn_pentagon.clicked.connect(lambda: self.canvas.set_mode("pentagon"))
        self.btn_hexagon.clicked.connect(lambda: self.canvas.set_mode("hexagon"))
        self.btn_line.clicked.connect(lambda: self.canvas.set_mode("line"))
        self.btn_arrow.clicked.connect(lambda: self.canvas.set_mode("arrow"))
        self.btn_arc.clicked.connect(lambda: self.canvas.set_mode("arc"))
        self.btn_elliptic_arc.clicked.connect(lambda: self.canvas.set_mode("elliptic_arc"))
        self.btn_bezier.clicked.connect(lambda: self.canvas.set_mode("bezier"))
        self.btn_text.clicked.connect(lambda: self.canvas.set_mode("text"))
        self.btn_dimension.clicked.connect(lambda: self.canvas.set_mode("dimension"))
        self.btn_custom_polygon.clicked.connect(lambda: self.canvas.set_mode("custom_polygon"))
        self.btn_move.clicked.connect(lambda: self.canvas.set_mode("move"))
        self.btn_clear.clicked.connect(self.canvas.clear_all)
        self.canvas.shape_changed.connect(self.update_code)
        self.canvas.shape_changed.connect(self.update_shape_list)
        self.canvas.shape_moved.connect(self.update_properties_on_move)

    def update_floating_buttons_position(self, event):
        # Update floating buttons position when canvas is resized or window is shown
        if hasattr(self, 'btn_move') and hasattr(self, 'btn_clear') and hasattr(self, 'canvas'):
            # Position buttons at top-right
            self.btn_move.move(self.canvas.width() - 170, 10)  # 170 = 80 + 80 + 10
            self.btn_clear.move(self.canvas.width() - 80, 10)

    def create_menu_bar(self):
        # Create menu bar
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        
        # New action
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        # Save action
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        # Load action
        load_action = QAction("Load", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_file)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        # Undo action
        # undo_action = QAction("Undo", self)
        # undo_action.setShortcut("Ctrl+Z")
        # undo_action.triggered.connect(self.canvas.undo)
        # edit_menu.addAction(undo_action)
        
        # # Redo action
        # redo_action = QAction("Redo", self)
        # redo_action.setShortcut("Ctrl+Y")
        # redo_action.triggered.connect(self.canvas.redo)
        # edit_menu.addAction(redo_action)
        
        # edit_menu.addSeparator()
        
        # Clear action
        clear_action = QAction("Clear All", self)
        clear_action.setShortcut("Ctrl+Shift+C")
        clear_action.triggered.connect(self.canvas.clear_all)
        edit_menu.addAction(clear_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        # License action
        license_action = QAction("License (PySide6)", self)
        license_action.triggered.connect(self.show_license)
        help_menu.addAction(license_action)

        visual_latex_menu = menubar.addMenu("Visual LaTeX Editor")
        
        github_action = QAction("GitHub", self)
        github_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/kaishistudio/Latex-document-quick-writer")))
        visual_latex_menu.addAction(github_action)

    def show_license(self):
        license_text = """<h3>PySide6 License Information</h3>
<p>This application uses PySide6, which is licensed under the following licenses:</p>

<h4>GNU Lesser General Public License (LGPL) v3</h4>
<p>PySide6 is available under the GNU Lesser General Public License version 3. 
You may use, modify, and distribute this software under the terms of the LGPL v3.</p>

<h4>Key Points:</h4>
<ul>
<li>You can use PySide6 in proprietary applications</li>
<li>You must include the PySide6 license notice</li>
<li>If you modify PySide6 itself, you must share those modifications</li>
<li>Your application code can remain proprietary</li>
</ul>

<h4>Qt Licensing</h4>
<p>Qt framework is dual-licensed under LGPL v3 and commercial licenses.</p>

<p>For more information, visit:<br>
<a href="https://www.qt.io/licensing">https://www.qt.io/licensing</a><br>
<a href="https://www.gnu.org/licenses/lgpl-3.0.html">https://www.gnu.org/licenses/lgpl-3.0.html</a></p>
"""
        msg = QMessageBox(self)
        msg.setWindowTitle("PySide6 License")
        msg.setTextFormat(Qt.RichText)
        msg.setText(license_text)
        msg.setTextInteractionFlags(Qt.TextBrowserInteraction)
        msg.exec()
    def new_file(self):
        # Clear canvas for new file
        self.canvas.clear_all()

    def save_file(self):
        # Save shapes to file
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "LaTeX Files (*.tex);;All Files (*)"
        )
        if file_path:
            with open(file_path, 'w') as f:
                lines = ["\\begin{tikzpicture}"]
                for s in self.canvas.shapes:
                    lines.append("    " + s.to_tikz())
                lines.append("\\end{tikzpicture}")
                f.write("\n".join(lines))

    def load_file(self):
        # Load shapes from file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load File", "", "LaTeX Files (*.tex);;All Files (*)"
        )
        if file_path:
            # Clear current shapes
            self.canvas.shapes.clear()
            
            # Parse file and add shapes
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Simple parsing - this could be improved
                    print("File loaded successfully")
            except Exception as e:
                print(f"Error loading file: {e}")

    def open_ad_link(self):
        # Open ad link in browser
        import webbrowser
        webbrowser.open("https://github.com/kaishistudio/Latex-document-quick-writer")

    def load_ad_image(self):
        self.network_manager = QNetworkAccessManager(self)
        url = QUrl("https://store-images.s-microsoft.com/image/apps.36411.14354944906131901.5f53df68-33d2-45d8-833e-d77664367196.57df3d3b-22d0-4cc3-a5d3-0014e5631b7b?h=210")
        request = QNetworkRequest(url)
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self.on_ad_image_loaded(reply))

    def on_ad_image_loaded(self, reply):
        from PySide6.QtGui import QPixmap
        
        if reply.error() == QNetworkReply.NoError:
            pixmap = QPixmap()
            if pixmap.loadFromData(reply.readAll()):
                # Resize pixmap to fit the label
                scaled_pixmap = pixmap.scaled(self.ad_image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.ad_image_label.setPixmap(scaled_pixmap)
        reply.deleteLater()

    def show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About LaTeX Tikz Design Tool")
        msg.setTextFormat(Qt.RichText)
        msg.setText(
    "<h3>LaTeX TikZ Design Tool</h3>"
    "<p>Author: KS.STUDIO | Version 1.0</p>"
    "<p>A professional tool for visualizing TikZ graphics & auto-generating LaTeX code.</p>"
    "<p>Key Features:</p>"
    "<ul>"
    "<li>Visual drawing: Lines, rectangles, circles, ellipses, polygons, flowcharts</li>"
    "<li>Style customization: Colors, line widths, linear/radial gradient fills</li>"
    "<li>One-click export of ready-to-use TikZ code</li>"
    "<li>Real-time code preview</li>"
    "</ul>"
    "<p>Built with PySide6 (Qt for Python) - Cross-platform</p>"
    "<p>GitHub: <a href='https://github.com/kaishistudio/LaTeX-Tikz-Design-Tool'>"
    "https://github.com/kaishistudio/LaTeX-Tikz-Design-Tool</a></p>"
)
        msg.setTextInteractionFlags(Qt.TextBrowserInteraction)
        msg.exec()


    def update_code(self):
        lines = ["\\begin{tikzpicture}"]
        for s in self.canvas.shapes:
            lines.append("    " + s.to_tikz())
        lines.append("\\end{tikzpicture}")
        self.code_edit.setPlainText("\n".join(lines))

    def update_shape_list(self):
        # Update shape list based on canvas shapes
        current_selection = self.shape_list.currentRow()
        self.shape_list.clear()
        for i, shape in enumerate(self.canvas.shapes):
            if isinstance(shape, TikzRect):
                item_text = f"Rectangle {i+1}"
            elif isinstance(shape, TikzCircle):
                item_text = f"Circle {i+1}"
            elif isinstance(shape, TikzEllipse):
                item_text = f"Ellipse {i+1}"
            elif isinstance(shape, TikzPolygon):
                if shape.sides == 3:
                    item_text = f"Triangle {i+1}"
                elif shape.sides == 5:
                    item_text = f"Pentagon {i+1}"
                elif shape.sides == 6:
                    item_text = f"Hexagon {i+1}"
                else:
                    item_text = f"Polygon ({shape.sides}) {i+1}"
            elif isinstance(shape, TikzLine):
                item_text = f"Line {i+1}"
            elif isinstance(shape, TikzArrow):
                item_text = f"Arrow {i+1}"
            elif isinstance(shape, TikzArc):
                item_text = f"Arc {i+1}"
            elif isinstance(shape, TikzEllipticArc):
                item_text = f"Elliptic Arc {i+1}"
            elif isinstance(shape, TikzBezier):
                item_text = f"Bezier {i+1}"
            elif isinstance(shape, TikzText):
                item_text = f"Text: {shape.text[:10]}{'...' if len(shape.text) > 10 else ''}"
            elif isinstance(shape, TikzDimension):
                item_text = f"Dimension: {shape.value:.2f}"
            else:
                item_text = f"Shape {i+1}"
            self.shape_list.addItem(item_text)
        
        # Restore selection if possible
        if 0 <= current_selection < self.shape_list.count():
            self.shape_list.setCurrentRow(current_selection)

    def on_shape_selected(self, index):
        # Handle shape selection from list
        if index >= 0 and index < len(self.canvas.shapes):
            self.canvas.selected_shape = self.canvas.shapes[index]
            self.update_properties_display(self.canvas.selected_shape)
        else:
            self.canvas.selected_shape = None
            self.update_properties_display(None)
        self.canvas.update()

    def copy_code(self):
        # Copy code to clipboard with package
        full_code = self.code_edit.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(full_code)
        QMessageBox.information(self, "Success", "Code copied to clipboard!")

    def apply_properties(self):
        # Apply properties to selected shape
        if self.canvas.selected_shape:
            shape = self.canvas.selected_shape
            
            # Update shape properties
            shape.color = self.color_combo.currentText()
            shape.line_width = self.width_spin.value()
            shape.dashed = self.dashed_check.isChecked()
            if hasattr(shape, 'fill_color'):
                shape.fill_color = self.fill_combo.currentText()
            
            # Update corner radius (only for rectangles)
            if isinstance(shape, TikzRect):
                shape.corner_radius = self.radius_spin.value()
            
            # Update position if controls are visible
            if self.x1_spin.isVisible():
                if isinstance(shape, TikzRect):
                    shape.x1 = self.x1_spin.value()
                    shape.y1 = self.y1_spin.value()
                    shape.x2 = self.x2_spin.value()
                    shape.y2 = self.y2_spin.value()
                elif isinstance(shape, TikzCircle):
                    shape.cx = self.x1_spin.value()
                    shape.cy = self.y1_spin.value()
                    shape.r = self.x2_spin.value()
                elif isinstance(shape, TikzEllipse):
                    shape.cx = self.x1_spin.value()
                    shape.cy = self.y1_spin.value()
                    shape.rx = self.x2_spin.value()
                    shape.ry = self.y2_spin.value()
                elif isinstance(shape, TikzPolygon):
                    shape.cx = self.x1_spin.value()
                    shape.cy = self.y1_spin.value()
                    shape.radius = self.x2_spin.value()
                elif isinstance(shape, TikzLine) or isinstance(shape, TikzArrow):
                    shape.x1 = self.x1_spin.value()
                    shape.y1 = self.y1_spin.value()
                    shape.x2 = self.x2_spin.value()
                    shape.y2 = self.y2_spin.value()
                elif isinstance(shape, TikzArc):
                    shape.cx = self.x1_spin.value()
                    shape.cy = self.y1_spin.value()
                    shape.r = self.x2_spin.value()
                elif isinstance(shape, TikzEllipticArc):
                    shape.cx = self.x1_spin.value()
                    shape.cy = self.y1_spin.value()
                    shape.rx = self.x2_spin.value()
                    shape.ry = self.y2_spin.value()
                elif isinstance(shape, TikzBezier):
                    shape.x1 = self.x1_spin.value()
                    shape.y1 = self.y1_spin.value()
                    shape.x2 = self.x2_spin.value()
                    shape.y2 = self.y2_spin.value()
                elif isinstance(shape, TikzText):
                    shape.x = self.x1_spin.value()
                    shape.y = self.y1_spin.value()
                elif isinstance(shape, TikzDimension):
                    shape.x1 = self.x1_spin.value()
                    shape.y1 = self.y1_spin.value()
                    shape.x2 = self.x2_spin.value()
                    shape.y2 = self.y2_spin.value()
                    # Recalculate value
                    shape.value = math.sqrt((shape.x2-shape.x1)**2 + (shape.y2-shape.y1)**2)
                
            # Save to history
            self.canvas.save_history()
            
            # Update canvas, code and list
            self.canvas.update()
            self.update_code()
            self.update_shape_list()

    def delete_selected_shape(self):
        # Delete selected shape
        if self.canvas.selected_shape and self.canvas.selected_shape in self.canvas.shapes:
            index = self.canvas.shapes.index(self.canvas.selected_shape)
            self.canvas.shapes.remove(self.canvas.selected_shape)
            self.canvas.selected_shape = None
            
            # Save to history
            self.canvas.save_history()
            
            # Update canvas, code and list
            self.canvas.update()
            self.update_code()
            self.update_shape_list()
            self.update_properties_display(None)

    def update_properties_on_move(self):
        # Update properties panel when shape is moved
        if self.canvas.selected_shape:
            self.update_properties_display(self.canvas.selected_shape)

    def update_properties_display(self, shape):
        # Block all property control signals to prevent triggering apply_properties
        self.color_combo.blockSignals(True)
        self.fill_combo.blockSignals(True)
        self.width_spin.blockSignals(True)
        self.dashed_check.blockSignals(True)
        self.radius_spin.blockSignals(True)
        self.x1_spin.blockSignals(True)
        self.y1_spin.blockSignals(True)
        self.x2_spin.blockSignals(True)
        self.y2_spin.blockSignals(True)
        
        # Update properties panel display based on selected shape
        if shape:
            # Update color
            if shape.color in [self.color_combo.itemText(i) for i in range(self.color_combo.count())]:
                self.color_combo.setCurrentText(shape.color)
            
            # Update line width
            self.width_spin.setValue(shape.line_width)
            
            # Update dashed
            self.dashed_check.setChecked(shape.dashed)
            
            # Update corner radius (only for rectangles)
            if isinstance(shape, TikzRect):
                self.radius_spin.setEnabled(True)
                self.radius_spin.setValue(shape.corner_radius)
            else:
                self.radius_spin.setEnabled(False)
                self.radius_spin.setValue(0)
            
            # Update fill color (only for shapes that support it)
            if hasattr(shape, 'fill_color'):
                self.fill_combo.setEnabled(True)
                if shape.fill_color in [self.fill_combo.itemText(i) for i in range(self.fill_combo.count())]:
                    self.fill_combo.setCurrentText(shape.fill_color)
            else:
                self.fill_combo.setEnabled(False)
            
            # Update position controls based on shape type
            if isinstance(shape, TikzRect):
                self.x1_label.setText("X1:")
                self.y1_label.setText("Y1:")
                self.x2_label.setText("X2:")
                self.y2_label.setText("Y2:")
                self.x1_spin.setValue(shape.x1)
                self.y1_spin.setValue(shape.y1)
                self.x2_spin.setValue(shape.x2)
                self.y2_spin.setValue(shape.y2)
                
                # Show all position controls
                self.x1_label.setVisible(True)
                self.x1_spin.setVisible(True)
                self.y1_label.setVisible(True)
                self.y1_spin.setVisible(True)
                self.x2_label.setVisible(True)
                self.x2_spin.setVisible(True)
                self.y2_label.setVisible(True)
                self.y2_spin.setVisible(True)
                
                # Set inputs to editable for other shapes
                self.x1_spin.setReadOnly(False)
                self.y1_spin.setReadOnly(False)
                self.x2_spin.setReadOnly(False)
                self.y2_spin.setReadOnly(False)
                
                coord_text = f"Rectangle: ({shape.x1:.2f}, {shape.y1:.2f}) to ({shape.x2:.2f}, {shape.y2:.2f})"
            elif isinstance(shape, TikzCircle):
                self.x1_label.setText("CX:")
                self.y1_label.setText("CY:")
                self.x2_label.setText("Radius:")
                self.y2_label.setVisible(False)
                self.y2_spin.setVisible(False)
                self.x1_spin.setValue(shape.cx)
                self.y1_spin.setValue(shape.cy)
                self.x2_spin.setValue(shape.r)
                
                # Show relevant position controls
                self.x1_label.setVisible(True)
                self.x1_spin.setVisible(True)
                self.y1_label.setVisible(True)
                self.y1_spin.setVisible(True)
                self.x2_label.setVisible(True)
                self.x2_spin.setVisible(True)
                
                # Set inputs to editable for other shapes
                self.x1_spin.setReadOnly(False)
                self.y1_spin.setReadOnly(False)
                self.x2_spin.setReadOnly(False)
                
                coord_text = f"Circle: Center ({shape.cx:.2f}, {shape.cy:.2f}), Radius {shape.r:.2f}"
            elif isinstance(shape, TikzEllipse):
                self.x1_label.setText("CX:")
                self.y1_label.setText("CY:")
                self.x2_label.setText("RX:")
                self.y2_label.setText("RY:")
                self.x1_spin.setValue(shape.cx)
                self.y1_spin.setValue(shape.cy)
                self.x2_spin.setValue(shape.rx)
                self.y2_spin.setValue(shape.ry)
                
                # Show all position controls
                self.x1_label.setVisible(True)
                self.x1_spin.setVisible(True)
                self.y1_label.setVisible(True)
                self.y1_spin.setVisible(True)
                self.x2_label.setVisible(True)
                self.x2_spin.setVisible(True)
                self.y2_label.setVisible(True)
                self.y2_spin.setVisible(True)
                
                # Set inputs to editable for other shapes
                self.x1_spin.setReadOnly(False)
                self.y1_spin.setReadOnly(False)
                self.x2_spin.setReadOnly(False)
                self.y2_spin.setReadOnly(False)
                
                coord_text = f"Ellipse: Center ({shape.cx:.2f}, {shape.cy:.2f}), RX {shape.rx:.2f}, RY {shape.ry:.2f}"
            elif isinstance(shape, TikzPolygon):
                self.x1_label.setText("CX:")
                self.y1_label.setText("CY:")
                self.x2_label.setText("Radius:")
                self.y2_label.setVisible(False)
                self.y2_spin.setVisible(False)
                self.x1_spin.setValue(shape.cx)
                self.y1_spin.setValue(shape.cy)
                self.x2_spin.setValue(shape.radius)
                
                # Show relevant position controls
                self.x1_label.setVisible(True)
                self.x1_spin.setVisible(True)
                self.y1_label.setVisible(True)
                self.y1_spin.setVisible(True)
                self.x2_label.setVisible(True)
                self.x2_spin.setVisible(True)
                
                # Set inputs to editable for other shapes
                self.x1_spin.setReadOnly(False)
                self.y1_spin.setReadOnly(False)
                self.x2_spin.setReadOnly(False)
                
                sides_name = {3: "Triangle", 5: "Pentagon", 6: "Hexagon"}.get(shape.sides, f"Polygon ({shape.sides})")
                coord_text = f"{sides_name}: Center ({shape.cx:.2f}, {shape.cy:.2f}), Radius {shape.radius:.2f}"
            elif isinstance(shape, TikzLine) or isinstance(shape, TikzArrow):
                self.x1_label.setText("X1:")
                self.y1_label.setText("Y1:")
                self.x2_label.setText("X2:")
                self.y2_label.setText("Y2:")
                self.x1_spin.setValue(shape.x1)
                self.y1_spin.setValue(shape.y1)
                self.x2_spin.setValue(shape.x2)
                self.y2_spin.setValue(shape.y2)
                
                # Show all position controls
                self.x1_label.setVisible(True)
                self.x1_spin.setVisible(True)
                self.y1_label.setVisible(True)
                self.y1_spin.setVisible(True)
                self.x2_label.setVisible(True)
                self.x2_spin.setVisible(True)
                self.y2_label.setVisible(True)
                self.y2_spin.setVisible(True)
                
                # Set inputs to editable for other shapes
                self.x1_spin.setReadOnly(False)
                self.y1_spin.setReadOnly(False)
                self.x2_spin.setReadOnly(False)
                self.y2_spin.setReadOnly(False)
                
                coord_text = f"Line: ({shape.x1:.2f}, {shape.y1:.2f}) to ({shape.x2:.2f}, {shape.y2:.2f})"
            elif isinstance(shape, TikzArc):
                self.x1_label.setText("CX:")
                self.y1_label.setText("CY:")
                self.x2_label.setText("Radius:")
                self.y2_label.setVisible(False)
                self.y2_spin.setVisible(False)
                self.x1_spin.setValue(shape.cx)
                self.y1_spin.setValue(shape.cy)
                self.x2_spin.setValue(shape.r)
                
                # Show relevant position controls
                self.x1_label.setVisible(True)
                self.x1_spin.setVisible(True)
                self.y1_label.setVisible(True)
                self.y1_spin.setVisible(True)
                self.x2_label.setVisible(True)
                self.x2_spin.setVisible(True)
                
                # Set position and radius inputs to read-only for arc
                self.x1_spin.setReadOnly(True)
                self.y1_spin.setReadOnly(True)
                self.x2_spin.setReadOnly(True)
                
                coord_text = f"Arc: Center ({shape.cx:.2f}, {shape.cy:.2f}), Radius {shape.r:.2f}, {shape.start_angle:.1f}° to {shape.end_angle:.1f}°"
            elif isinstance(shape, TikzEllipticArc):
                self.x1_label.setText("CX:")
                self.y1_label.setText("CY:")
                self.x2_label.setText("RX:")
                self.y2_label.setText("RY:")
                self.x1_spin.setValue(shape.cx)
                self.y1_spin.setValue(shape.cy)
                self.x2_spin.setValue(shape.rx)
                self.y2_spin.setValue(shape.ry)
                
                # Show all position controls
                self.x1_label.setVisible(True)
                self.x1_spin.setVisible(True)
                self.y1_label.setVisible(True)
                self.y1_spin.setVisible(True)
                self.x2_label.setVisible(True)
                self.x2_spin.setVisible(True)
                self.y2_label.setVisible(True)
                self.y2_spin.setVisible(True)
                
                # Set position inputs to read-only for elliptic arc
                self.x1_spin.setReadOnly(True)
                self.y1_spin.setReadOnly(True)
                self.x2_spin.setReadOnly(True)
                self.y2_spin.setReadOnly(True)
                
                coord_text = f"Elliptic Arc: Center ({shape.cx:.2f}, {shape.cy:.2f}), RX {shape.rx:.2f}, RY {shape.ry:.2f}, {shape.start_angle:.1f}° to {shape.end_angle:.1f}°"
            elif isinstance(shape, TikzBezier):
                self.x1_label.setText("X1:")
                self.y1_label.setText("Y1:")
                self.x2_label.setText("X2:")
                self.y2_label.setText("Y2:")
                self.x1_spin.setValue(shape.x1)
                self.y1_spin.setValue(shape.y1)
                self.x2_spin.setValue(shape.x2)
                self.y2_spin.setValue(shape.y2)
                
                # Show all position controls
                self.x1_label.setVisible(True)
                self.x1_spin.setVisible(True)
                self.y1_label.setVisible(True)
                self.y1_spin.setVisible(True)
                self.x2_label.setVisible(True)
                self.x2_spin.setVisible(True)
                self.y2_label.setVisible(True)
                self.y2_spin.setVisible(True)
                
                # Set inputs to editable for bezier curve
                self.x1_spin.setReadOnly(False)
                self.y1_spin.setReadOnly(False)
                self.x2_spin.setReadOnly(False)
                self.y2_spin.setReadOnly(False)
                
                coord_text = f"Bezier: Start ({shape.x1:.2f}, {shape.y1:.2f}), Control ({shape.x2:.2f}, {shape.y2:.2f}), End ({shape.x3:.2f}, {shape.y3:.2f})"
            elif isinstance(shape, TikzText):
                self.x1_label.setText("X:")
                self.y1_label.setText("Y:")
                self.x2_label.setVisible(False)
                self.x2_spin.setVisible(False)
                self.y2_label.setVisible(False)
                self.y2_spin.setVisible(False)
                self.x1_spin.setValue(shape.x)
                self.y1_spin.setValue(shape.y)
                
                # Show relevant position controls
                self.x1_label.setVisible(True)
                self.x1_spin.setVisible(True)
                self.y1_label.setVisible(True)
                self.y1_spin.setVisible(True)
                
                # Set inputs to editable for text
                self.x1_spin.setReadOnly(False)
                self.y1_spin.setReadOnly(False)
                
                coord_text = f"Text: '{shape.text}' at ({shape.x:.2f}, {shape.y:.2f})"
            elif isinstance(shape, TikzDimension):
                self.x1_label.setText("X1:")
                self.y1_label.setText("Y1:")
                self.x2_label.setText("X2:")
                self.y2_label.setText("Y2:")
                self.x1_spin.setValue(shape.x1)
                self.y1_spin.setValue(shape.y1)
                self.x2_spin.setValue(shape.x2)
                self.y2_spin.setValue(shape.y2)
                
                # Show all position controls
                self.x1_label.setVisible(True)
                self.x1_spin.setVisible(True)
                self.y1_label.setVisible(True)
                self.y1_spin.setVisible(True)
                self.x2_label.setVisible(True)
                self.x2_spin.setVisible(True)
                self.y2_label.setVisible(True)
                self.y2_spin.setVisible(True)
                
                # Set inputs to editable
                self.x1_spin.setReadOnly(False)
                self.y1_spin.setReadOnly(False)
                self.x2_spin.setReadOnly(False)
                self.y2_spin.setReadOnly(False)
                
                coord_text = f"Dimension: {shape.value:.2f} from ({shape.x1:.2f}, {shape.y1:.2f}) to ({shape.x2:.2f}, {shape.y2:.2f})"
            
            else:
                coord_text = f"Unknown shape"
            
            self.coord_label.setText(coord_text)
        else:
            # Clear properties panel when no shape selected
            self.coord_label.setText("No selection")
            self.fill_combo.setEnabled(False)
            
            # Hide position controls
            self.x1_label.setVisible(False)
            self.x1_spin.setVisible(False)
            self.y1_label.setVisible(False)
            self.y1_spin.setVisible(False)
            self.x2_label.setVisible(False)
            self.x2_spin.setVisible(False)
            self.y2_label.setVisible(False)
            self.y2_spin.setVisible(False)
        
        # Unblock all property control signals
        self.color_combo.blockSignals(False)
        self.fill_combo.blockSignals(False)
        self.width_spin.blockSignals(False)
        self.dashed_check.blockSignals(False)
        self.radius_spin.blockSignals(False)
        self.x1_spin.blockSignals(False)
        self.y1_spin.blockSignals(False)
        self.x2_spin.blockSignals(False)
        self.y2_spin.blockSignals(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    win.showMaximized()
    sys.exit(app.exec())