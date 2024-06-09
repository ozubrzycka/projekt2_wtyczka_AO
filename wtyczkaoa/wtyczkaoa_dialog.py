# -*- coding: utf-8 -*-
"""
/***************************************************************************
 wtyczkaoaDialog
                                 A QGIS plugin
 Wtyczka służy do przetwarzania i analizy danych geoprzestrzennych bezpośrednio w QGIS. Oferuje następujące funkcjonalności: Obliczanie różnicy wysokości oraz obliczanie pola powierzchni metodą Gaussa
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-06-08
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Oliwia Zubrzycka, Alicja Wiatr
        email                : 01179242@pw.edu.pl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from math import atan2, sqrt, pi
from qgis.utils import iface
from qgis.PyQt import QtWidgets, uic
from qgis.core import QgsFeature, QgsGeometry, QgsPointXY
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'wtyczkaoa_dialog_base.ui'))


class wtyczkaoaDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(wtyczkaoaDialog, self).__init__(parent)
        self.setupUi(self)
        self.height_difference.clicked.connect(self.height_difference_function)
        self.count_points.clicked.connect(self.count_elements)
        self.display_coordinates.clicked.connect(self.coordinates_function)
        self.area.clicked.connect(self.area_function)
        self.clear_table.clicked.connect(self.clear_array_function)
        self.close_button.clicked.connect(self.clear_data_function)
        self.azimuth.clicked.connect(self.azimuth_function)
        self.segment_length.clicked.connect(self.segment_length_function)
        self.reset_all.clicked.connect(self.clear_data_function)
        self.save_file.clicked.connect(self.save_file_function)
        self.reverse_azimuth.clicked.connect(self.azimuth_function)
        self.load_file.clicked.connect(self.select_file_function)

    def show_error_message(self, error_message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(error_message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()

    def check_current_layer(self):
        current_layer = self.mMapLayerComboBox_layers.currentLayer()
        if current_layer is None:
            self.show_error_message("No layer selected")
            return False
        return True 

    def segment_length_function(self):
        if not self.check_current_layer():
            return
    
        selected_features = self.mMapLayerComboBox_layers.currentLayer().selectedFeatures()
        num_elements = len(selected_features)
        if num_elements == 2:
            points = [[feature.geometry().asPoint().x(), feature.geometry().asPoint().y()] for feature in selected_features]
            distance = sqrt((points[0][0] - points[1][0])**2 + (points[0][1] - points[1][1])**2)
            self.segment_length_result.setText(f'Distance between points (point id:1- id:2) is: {distance:.3f} [m]')
            return distance
        else:
            self.show_error_message("Error: Incorrect number of points selected")
    def extract_coordinates(self, selected_features):
        coords = []
        for feature in selected_features:
            wsp = feature.geometry().asPoint()
            coords.append([wsp.x(), wsp.y()])
        return coords

    def azimuth_function(self):
        if not self.check_current_layer():
            return
    
        selected_features = self.mMapLayerComboBox_layers.currentLayer().selectedFeatures()
        num_elements = len(selected_features)
        print(f"Number of selected elements: {num_elements}")  # Debugging
    
        if num_elements == 2:
            coords = self.extract_coordinates(selected_features)
            azimuth = atan2((coords[1][1] - coords[0][1]), (coords[1][0] - coords[0][0]))
            print(f"Initial Azimuth (radians): {azimuth}")  # Debugging
    
            if 'decimal_degrees' == self.unit_azimuth.currentText():
                azimuth_degrees = azimuth * 180 / pi
                if azimuth_degrees < 0:
                    azimuth_degrees += 360
                elif azimuth_degrees > 360:
                    azimuth_degrees -= 360
                reverse_azimuth_degrees = azimuth_degrees + 180
                if reverse_azimuth_degrees < 0:
                    reverse_azimuth_degrees += 360
                elif reverse_azimuth_degrees > 360:
                    reverse_azimuth_degrees -= 360
                self.azimuth_result.setText(f'Azimuth is (point id:1- id:2): {azimuth_degrees:.7f}[decimal_degrees]')
                self.reverse_azimuth_result.setText(f'Reverse azimuth is (point id:2- id:1): {reverse_azimuth_degrees:.7f}[decimal_degrees]')

            elif 'grads' == self.unit_azimuth.currentText():
                azimuth_grads = azimuth * 200 / pi
                if azimuth_grads < 0:
                    azimuth_grads += 400
                elif azimuth_grads > 400:
                    azimuth_grads -= 400
                reverse_azimuth_grads = azimuth_grads + 200
                if reverse_azimuth_grads < 0:
                    reverse_azimuth_grads += 400
                elif reverse_azimuth_grads > 400:
                    reverse_azimuth_grads -= 400
                self.azimuth_result.setText(f'Azimuth is (point id:1- id:2): {azimuth_grads:.4f}[grads]')
                self.reverse_azimuth_result.setText(f'Reverse azimuth is (point id:2- id:1): {reverse_azimuth_grads:.4f}[grads]')
        else:
            self.show_error_message("Error: Incorrect number of points selected")

    def count_elements(self):
        if not self.check_current_layer():
            return
        num_elements = len(self.mMapLayerComboBox_layers.currentLayer().selectedFeatures())
        self.show_point_count.setText(str(num_elements))

    def coordinates_function(self):
        if not self.check_current_layer():
            return
        selected_features = self.mMapLayerComboBox_layers.currentLayer().selectedFeatures()
        coords = ""
        point_id = 1
        for feature in selected_features:
            wsp = feature.geometry().asPoint()
            X = wsp.x()
            Y = wsp.y()
            coords += f'Coordinates of point {point_id}: X = {X:.3f}, Y = {Y:.3f}\n'
            point_id += 1
        self.coordinates.setText(coords)

    def height_difference_function(self):
        if not self.check_current_layer():
            return
        num_elements = len(self.mMapLayerComboBox_layers.currentLayer().selectedFeatures())
        heights = []
        if num_elements == 2:
            selected_layer = iface.activeLayer()
            selected_features = selected_layer.selectedFeatures()
            for feature in selected_features:
                height = float(feature[20])
                heights.append(height)
            height_difference = heights[1] - heights[0]
            self.height_difference_result.setText(f'Height difference {height_difference:.3f}[m]')
            return height_difference
        elif num_elements < 2:
            self.height_difference_result.setText("Error")
            self.show_error_message("Too few points selected")
        elif num_elements > 2:
            self.height_difference_result.setText("Error")
            self.show_error_message("Too many points selected")

    def get_angle(self, point, centroid):
        dx = point[0] - centroid[0]
        dy = point[1] - centroid[1]
        angle = atan2(dy, dx)
        return angle

    def sort_points(self, points):
        centroid = [sum(p[0] for p in points) / len(points), sum(p[1] for p in points) / len(points)]
        sorted_points = sorted(points, key=lambda p: self.get_angle(p, centroid))
        return sorted_points

    def area_function(self):
        if not self.check_current_layer():
            return
        num_elements = len(self.mMapLayerComboBox_layers.currentLayer().selectedFeatures())
        if num_elements >= 3:
            selected_features = self.mMapLayerComboBox_layers.currentLayer().selectedFeatures()
            points = []
            for feature in selected_features:
                point = feature.geometry().asPoint()
                points.append([point.x(), point.y()])
            points = self.sort_points(points)
            area_sum = 0
            for i in range(len(points)):
                if i < len(points) - 1:
                    P = (points[i][0] * (points[i + 1][1] - points[i - 1][1]))
                    area_sum += P
            P = (points[-1][0] * (points[-2][1]))
            area_sum += P
            area_sum = 0.5 * abs(area_sum)
        
            if 'square_meters' == self.area_unit.currentText():
                self.surface_area_result.setText(f'Surface area is: {area_sum:.3f} [m2]')
            elif 'hectares' == self.area_unit.currentText():
                area_sum = area_sum * 0.0001
                self.surface_area_result.setText(f'Surface area is: {area_sum:.7f} [ha]')
            elif 'ares' == self.area_unit.currentText():
                area_sum = area_sum * 0.01
                self.surface_area_result.setText(f'Surface area is: {area_sum:.5f} [a]')
            elif 'square_kilometers' == self.area_unit.currentText():
                area_sum = area_sum * 0.000001
                self.surface_area_result.setText(f'Surface area is: {area_sum:.9f} [km2]')
        else:
            self.show_error_message("Error: Incorrect number of points selected")

    def clear_array_function(self):
        self.coordinates.clear()
        self.show_point_count.clear()
        self.azimuth_result.clear()
        self.reverse_azimuth_result.clear()
        self.height_difference_result.clear()
        self.segment_length_result.clear()
        self.surface_area_result.clear()

    def clear_data_function(self):
        self.clear_array_function()
        self.mMapLayerComboBox_layers.clear()

    def save_file_function(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")
        if filename:
            with open(filename, "w") as file:
                selected_features = self.mMapLayerComboBox_layers.currentLayer().selectedFeatures()
                num_points = len(selected_features)
                file.write(f'Number of selected points: {num_points}\n')
                coordinates = ""
                point_id = 1
                for feature in selected_features:
                    wsp = feature.geometry().asPoint()
                    X = wsp.x()
                    Y = wsp.y()
                    coordinates += f"Coordinates of point number {point_id}: X = {X:.3f}, Y = {Y:.3f}\n"
                    point_id += 1
                file.write(coordinates)
    
                distance = self.segment_length_function()
                if distance is not None:
                    file.write(f'Distance between points (point id:1- id:2) is: {distance:.3f} [m]\n')
    
                azimuth, reverse_azimuth = self.azimuth_function()  # Update: Added azimuth calculation
                if azimuth is not None and reverse_azimuth is not None:
                    file.write(f'Azimuth is (point id:1- id:2): {azimuth}\n')
                    file.write(f'Reverse azimuth is (point id:2- id:1): {reverse_azimuth}\n')  # Update: Added azimuth to file
    
                height_difference = self.height_difference_function()
                if height_difference is not None:
                    file.write(f'Height difference: {height_difference:.3f}[m]\n')
    
                self.area_function()


    def select_file_function(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if filename:
            with open(filename, 'r') as file:
                data = file.read()
                # Assuming a specific format of the file, we should parse it accordingly
                sections = data.split("\n\n")
                for section in sections:
                    if section.startswith("Coordinates:"):
                        self.coordinates.setText(section.replace("Coordinates:\n", ""))
                    elif section.startswith("Point Count:"):
                        self.show_point_count.setText(section.replace("Point Count:\n", ""))
                    elif section.startswith("Azimuth:"):
                        self.azimuth_result.setText(section.replace("Azimuth:\n", ""))
                    elif section.startswith("Reverse Azimuth:"):
                        self.reverse_azimuth_result.setText(section.replace("Reverse Azimuth:\n", ""))
                    elif section.startswith("Height Difference:"):
                        self.height_difference_result.setText(section.replace("Height Difference:\n", ""))
                    elif section.startswith("Segment Length:"):
                        self.segment_length_result.setText(section.replace("Segment Length:\n", ""))
                    elif section.startswith("Surface Area:"):
                        self.surface_area_result.setText(section.replace("Surface Area:\n", ""))


def run():
    dialog = wtyczkaoaDialog()
    dialog.show()
