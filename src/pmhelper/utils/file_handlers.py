#!/usr/bin/env python3
"""
File Handlers Module

Provides utilities for loading and saving project data from various file formats.
Supports CSV, Excel, and other data formats commonly used in project management.
"""

import csv
import pandas as pd
import os
from typing import List, Dict, Any, Optional


class FileHandler:
    """Handles file operations for project data"""
    
    @staticmethod
    def load_csv(file_path: str) -> List[Dict[str, Any]]:
        """
        Load activities from CSV file
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            List[Dict]: List of activity dictionaries
        """
        activities_data = []
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                # Try to detect delimiter
                sample = file.read(1024)
                file.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                for row in reader:
                    # Convert keys to lowercase and strip whitespace
                    cleaned_row = {k.lower().strip(): v.strip() if isinstance(v, str) else v 
                                 for k, v in row.items() if k}
                    if cleaned_row:  # Skip empty rows
                        activities_data.append(cleaned_row)
                        
        except Exception as e:
            raise ValueError(f"Error reading CSV file {file_path}: {str(e)}")
        
        return activities_data
    
    @staticmethod
    def load_excel(file_path: str, sheet_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load activities from Excel file
        
        Args:
            file_path (str): Path to the Excel file
            sheet_name (str, optional): Name of the sheet to read. If None, reads first sheet.
            
        Returns:
            List[Dict]: List of activity dictionaries
        """
        try:
            # Read Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            # Convert to list of dictionaries
            activities_data = []
            for _, row in df.iterrows():
                # Convert keys to lowercase and handle NaN values
                cleaned_row = {}
                for k, v in row.items():
                    key = str(k).lower().strip()
                    if pd.isna(v):
                        value = ""
                    else:
                        value = str(v).strip()
                    cleaned_row[key] = value
                
                if any(cleaned_row.values()):  # Skip completely empty rows
                    activities_data.append(cleaned_row)
                    
        except Exception as e:
            raise ValueError(f"Error reading Excel file {file_path}: {str(e)}")
        
        return activities_data
    
    @staticmethod
    def save_csv(data: List[Dict[str, Any]], file_path: str, fieldnames: Optional[List[str]] = None) -> None:
        """
        Save activities data to CSV file
        
        Args:
            data (List[Dict]): List of activity dictionaries
            file_path (str): Path where to save the CSV file
            fieldnames (List[str], optional): Column names. If None, inferred from data.
        """
        if not data:
            raise ValueError("No data to save")
        
        # Infer fieldnames if not provided
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
                
        except Exception as e:
            raise ValueError(f"Error writing CSV file {file_path}: {str(e)}")
    
    @staticmethod
    def save_excel(data: List[Dict[str, Any]], file_path: str, sheet_name: str = 'Activities') -> None:
        """
        Save activities data to Excel file
        
        Args:
            data (List[Dict]): List of activity dictionaries
            file_path (str): Path where to save the Excel file
            sheet_name (str): Name of the sheet
        """
        if not data:
            raise ValueError("No data to save")
        
        try:
            df = pd.DataFrame(data)
            df.to_excel(file_path, sheet_name=sheet_name, index=False)
            
        except Exception as e:
            raise ValueError(f"Error writing Excel file {file_path}: {str(e)}")
    
    @staticmethod
    def validate_required_columns(data: List[Dict[str, Any]], required_columns: List[str]) -> bool:
        """
        Validate that data contains required columns
        
        Args:
            data (List[Dict]): List of activity dictionaries
            required_columns (List[str]): List of required column names
            
        Returns:
            bool: True if all required columns are present
            
        Raises:
            ValueError: If required columns are missing
        """
        if not data:
            raise ValueError("No data provided for validation")
        
        available_columns = set(data[0].keys())
        missing_columns = set(required_columns) - available_columns
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        return True
    
    @staticmethod
    def get_sample_cpm_data() -> List[Dict[str, Any]]:
        """
        Get sample CPM data for testing and demonstrations
        
        Returns:
            List[Dict]: Sample activity data
        """
        return [
            {
                "id": "A",
                "activity": "Design Phase",
                "duration": "5",
                "predecessors": "",
                "min_duration": "1",
                "crash_cost": "300",
                "resource_demand": "2"
            },
            {
                "id": "B",
                "activity": "Requirements Analysis",
                "duration": "3",
                "predecessors": "",
                "min_duration": "2",
                "crash_cost": "500",
                "resource_demand": "1"
            },
            {
                "id": "C",
                "activity": "Architecture Design",
                "duration": "7",
                "predecessors": "A, B",
                "min_duration": "5",
                "crash_cost": "600",
                "resource_demand": "3"
            },
            {
                "id": "D",
                "activity": "Database Design",
                "duration": "5",
                "predecessors": "C",
                "min_duration": "4",
                "crash_cost": "400",
                "resource_demand": "1"
            },
            {
                "id": "E",
                "activity": "Frontend Development",
                "duration": "6",
                "predecessors": "C",
                "min_duration": "3",
                "crash_cost": "300",
                "resource_demand": "4"
            },
            {
                "id": "F",
                "activity": "Backend Development",
                "duration": "8",
                "predecessors": "C",
                "min_duration": "5",
                "crash_cost": "200",
                "resource_demand": "5"
            },
            {
                "id": "G",
                "activity": "Testing",
                "duration": "3",
                "predecessors": "D",
                "min_duration": "3",
                "crash_cost": "800",
                "resource_demand": "2"
            },
            {
                "id": "H",
                "activity": "Deployment",
                "duration": "4",
                "predecessors": "E, F",
                "min_duration": "2",
                "crash_cost": "1000",
                "resource_demand": "1"
            },
            {
                "id": "I",
                "activity": "Documentation",
                "duration": "3",
                "predecessors": "G, H",
                "min_duration": "2",
                "crash_cost": "250",
                "resource_demand": "2"
            }
        ]
    
    @staticmethod
    def get_sample_pert_data() -> List[Dict[str, Any]]:
        """
        Get sample PERT data for testing and demonstrations
        
        Returns:
            List[Dict]: Sample PERT activity data
        """
        return [
            {
                "id": "A",
                "activity": "Design Phase",
                "optimistic": "3",
                "most_likely": "5",
                "pessimistic": "8",
                "predecessors": "",
                "min_duration": "1",
                "crash_cost": "300",
                "resource_demand": "2",
                "normal_cost": "1000"
            },
            {
                "id": "B",
                "activity": "Requirements Analysis",
                "optimistic": "2",
                "most_likely": "3",
                "pessimistic": "5",
                "predecessors": "",
                "min_duration": "2",
                "crash_cost": "500",
                "resource_demand": "1",
                "normal_cost": "800"
            },
            {
                "id": "C",
                "activity": "Architecture Design",
                "optimistic": "5",
                "most_likely": "7",
                "pessimistic": "10",
                "predecessors": "A, B",
                "min_duration": "5",
                "crash_cost": "600",
                "resource_demand": "3",
                "normal_cost": "1200"
            },
            {
                "id": "D",
                "activity": "Database Design",
                "optimistic": "3",
                "most_likely": "5",
                "pessimistic": "8",
                "predecessors": "C",
                "min_duration": "4",
                "crash_cost": "400",
                "resource_demand": "1",
                "normal_cost": "700"
            },
            {
                "id": "E",
                "activity": "Frontend Development",
                "optimistic": "4",
                "most_likely": "6",
                "pessimistic": "9",
                "predecessors": "C",
                "min_duration": "3",
                "crash_cost": "300",
                "resource_demand": "4",
                "normal_cost": "900"
            }
        ]
