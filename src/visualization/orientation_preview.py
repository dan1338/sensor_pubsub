import numpy as np
import quaternion as quat
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

class OrientationPreview:
    """
    A 3D visualization showing orientation using pyqtgraph.
    Displays a coordinate gizmo representing the orientation.
    Updates GUI at a fixed frame rate, caching the latest orientation.
    """
    
    def __init__(self, title: str, time_step: float = 1.0 / 60):
        self.dt = time_step
        self.latest_orientation = np.quaternion(1, 0, 0, 0)
        self._init_visualization(title)
            
    def _init_visualization(self, title: str):
        # Create the application and window
        self.app = pg.mkQApp("Orientation Visualization")
        self.view = pg.PlotWidget(title="Orientation Preview")
        self.view.setWindowTitle(f'Orientation Visualization {title}')
        self.view.resize(600, 600)
        self.view.show()
        
        # Create plot item
        self.plot = pg.PlotItem()
        self.view.setCentralItem(self.plot)
        
        # Create the axis lines (gizmo)
        self.x_axis = pg.PlotDataItem([], [], pen=pg.mkPen('r', width=2))
        self.y_axis = pg.PlotDataItem([], [], pen=pg.mkPen('g', width=2))
        self.z_axis = pg.PlotDataItem([], [], pen=pg.mkPen('b', width=2))
        
        self.plot.addItem(self.x_axis)
        self.plot.addItem(self.y_axis)
        self.plot.addItem(self.z_axis)
        
        # Set the view range
        self.plot.setRange(xRange=(-1.5, 1.5), yRange=(-1.5, 1.5))
        
        # Setup timer for fixed frame rate updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update_gui)
        self.timer.start(int(self.dt * 1000)) # Convert to milliseconds
        
    def _update_gui(self):
        # Use the latest cached orientation
        orientation = self.latest_orientation
        
        # Define the axes in body frame
        x_axis = np.array([1, 0, 0])
        y_axis = np.array([0, 1, 0])
        z_axis = np.array([0, 0, 1])
        
        # Rotate the axes by the current orientation
        x_rotated = quat.rotate_vectors(orientation, x_axis)
        y_rotated = quat.rotate_vectors(orientation, y_axis)
        z_rotated = quat.rotate_vectors(orientation, z_axis)
        
        # Update the axis lines for 2D projection
        self.x_axis.setData([0, x_rotated[0]], [0, x_rotated[1]])
        self.y_axis.setData([0, y_rotated[0]], [0, y_rotated[1]])
        self.z_axis.setData([0, z_rotated[0]], [0, z_rotated[1]])
        
        # Process UI events at fixed frame rate
        pg.QtGui.QGuiApplication.processEvents()
            
    def update(self, orientation: np.quaternion):
        # Cache the latest orientation (can be called at any frequency)
        self.latest_orientation = orientation
        self.app.processEvents()
        
    def close(self):
        self.timer.stop()
        self.view.close()
