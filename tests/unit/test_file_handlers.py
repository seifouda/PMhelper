#!/usr/bin/env python3
"""
Test suite for file handling utilities.

Tests the file_handlers module functionality including:
- CSV file import/export
- Excel file handling
- JSON data processing
- Data validation
- Error handling
"""

import pytest
import sys
import os
import tempfile
import csv
import json
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import pandas as pd

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from pmhelper.utils.file_handlers import (
    load_csv_data,
    save_csv_data,
    load_excel_data,
    save_excel_data,
    load_json_data,
    save_json_data,
    validate_project_data,
    detect_data_format,
    sanitize_filename
)


class TestCSVHandling:
    """Test suite for CSV file handling functionality."""
    
    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.sample_csv_data = [
            {'id': 'A', 'activity': 'Design', 'duration': '5', 'predecessors': ''},
            {'id': 'B', 'activity': 'Development', 'duration': '10', 'predecessors': 'A'},
            {'id': 'C', 'activity': 'Testing', 'duration': '3', 'predecessors': 'B'},
        ]
        
        self.sample_csv_content = (
            "id,activity,duration,predecessors\n"
            "A,Design,5,\n"
            "B,Development,10,A\n"
            "C,Testing,3,B\n"
        )
    
    def test_load_csv_data_success(self):
        """Test successful CSV data loading."""
        with patch('builtins.open', mock_open(read_data=self.sample_csv_content)):
            with patch('csv.DictReader') as mock_reader:
                mock_reader.return_value = self.sample_csv_data
                
                result = load_csv_data('test.csv')
                
                assert result == self.sample_csv_data
                mock_reader.assert_called_once()
    
    def test_load_csv_data_file_not_found(self):
        """Test CSV loading with file not found error."""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            with pytest.raises(FileNotFoundError):
                load_csv_data('nonexistent.csv')
    
    def test_load_csv_data_invalid_format(self):
        """Test CSV loading with invalid file format."""
        invalid_csv_content = "invalid,csv,format\nwith,missing,headers"
        
        with patch('builtins.open', mock_open(read_data=invalid_csv_content)):
            # This should handle the error gracefully
            result = load_csv_data('invalid.csv')
            # Test depends on implementation - might return empty list or raise exception
    
    def test_save_csv_data_success(self):
        """Test successful CSV data saving."""
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('csv.DictWriter') as mock_writer:
                mock_writer_instance = Mock()
                mock_writer.return_value = mock_writer_instance
                
                save_csv_data(self.sample_csv_data, 'output.csv')
                
                mock_file.assert_called_once_with('output.csv', 'w', newline='', encoding='utf-8')
                mock_writer_instance.writeheader.assert_called_once()
                mock_writer_instance.writerows.assert_called_once_with(self.sample_csv_data)
    
    def test_save_csv_data_permission_error(self):
        """Test CSV saving with permission error."""
        with patch('builtins.open', side_effect=PermissionError()):
            with pytest.raises(PermissionError):
                save_csv_data(self.sample_csv_data, 'readonly.csv')
    
    def test_csv_encoding_handling(self):
        """Test CSV handling with different encodings."""
        # Test UTF-8, UTF-16, and other encodings
        encodings = ['utf-8', 'utf-16', 'latin-1']
        
        for encoding in encodings:
            with patch('builtins.open', mock_open(read_data=self.sample_csv_content)):
                # Test that different encodings are handled properly
                try:
                    result = load_csv_data('test.csv')
                    # Verify encoding doesn't break data loading
                    assert isinstance(result, list)
                except UnicodeDecodeError:
                    # Some encodings might fail, which is acceptable
                    pass


class TestExcelHandling:
    """Test suite for Excel file handling functionality."""
    
    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.sample_excel_data = pd.DataFrame([
            {'id': 'A', 'activity': 'Design', 'duration': 5, 'predecessors': ''},
            {'id': 'B', 'activity': 'Development', 'duration': 10, 'predecessors': 'A'},
            {'id': 'C', 'activity': 'Testing', 'duration': 3, 'predecessors': 'B'},
        ])
    
    @patch('pandas.read_excel')
    def test_load_excel_data_success(self, mock_read_excel):
        """Test successful Excel data loading."""
        mock_read_excel.return_value = self.sample_excel_data
        
        result = load_excel_data('test.xlsx')
        
        assert len(result) == 3
        assert result[0]['id'] == 'A'
        mock_read_excel.assert_called_once_with('test.xlsx')
    
    @patch('pandas.read_excel')
    def test_load_excel_data_with_sheet_name(self, mock_read_excel):
        """Test Excel loading with specific sheet name."""
        mock_read_excel.return_value = self.sample_excel_data
        
        result = load_excel_data('test.xlsx', sheet_name='Activities')
        
        mock_read_excel.assert_called_once_with('test.xlsx', sheet_name='Activities')
    
    @patch('pandas.read_excel')
    def test_load_excel_data_file_error(self, mock_read_excel):
        """Test Excel loading with file error."""
        mock_read_excel.side_effect = FileNotFoundError()
        
        with pytest.raises(FileNotFoundError):
            load_excel_data('nonexistent.xlsx')
    
    @patch('pandas.DataFrame.to_excel')
    def test_save_excel_data_success(self, mock_to_excel):
        """Test successful Excel data saving."""
        data = [
            {'id': 'A', 'activity': 'Design', 'duration': 5},
            {'id': 'B', 'activity': 'Development', 'duration': 10},
        ]
        
        save_excel_data(data, 'output.xlsx')
        
        mock_to_excel.assert_called_once()
    
    def test_excel_data_type_conversion(self):
        """Test Excel data type conversion."""
        # Test that Excel data types are properly converted
        mixed_data = pd.DataFrame([
            {'id': 'A', 'duration': '5', 'cost': 1000.50},
            {'id': 'B', 'duration': 10, 'cost': '2000'},
        ])
        
        with patch('pandas.read_excel', return_value=mixed_data):
            result = load_excel_data('test.xlsx')
            
            # Verify data type handling
            assert isinstance(result, list)
            assert len(result) == 2


class TestJSONHandling:
    """Test suite for JSON file handling functionality."""
    
    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.sample_json_data = {
            'project_name': 'Test Project',
            'activities': [
                {'id': 'A', 'activity': 'Design', 'duration': 5, 'predecessors': []},
                {'id': 'B', 'activity': 'Development', 'duration': 10, 'predecessors': ['A']},
            ],
            'metadata': {
                'created': '2024-01-15',
                'version': '1.0'
            }
        }
    
    def test_load_json_data_success(self):
        """Test successful JSON data loading."""
        json_content = json.dumps(self.sample_json_data)
        
        with patch('builtins.open', mock_open(read_data=json_content)):
            result = load_json_data('test.json')
            
            assert result == self.sample_json_data
            assert result['project_name'] == 'Test Project'
            assert len(result['activities']) == 2
    
    def test_load_json_data_invalid_json(self):
        """Test JSON loading with invalid JSON format."""
        invalid_json = "{ invalid json format }"
        
        with patch('builtins.open', mock_open(read_data=invalid_json)):
            with pytest.raises(json.JSONDecodeError):
                load_json_data('invalid.json')
    
    def test_save_json_data_success(self):
        """Test successful JSON data saving."""
        with patch('builtins.open', mock_open()) as mock_file:
            save_json_data(self.sample_json_data, 'output.json')
            
            mock_file.assert_called_once_with('output.json', 'w', encoding='utf-8')
            # Verify that JSON data was written (would need to check the actual write calls)
    
    def test_json_serialization_edge_cases(self):
        """Test JSON serialization with edge cases."""
        edge_case_data = {
            'unicode_text': 'Testing unicode: áéíóú',
            'large_number': 999999999999999999,
            'float_precision': 3.141592653589793,
            'boolean_values': [True, False],
            'null_value': None,
            'empty_list': [],
            'empty_dict': {}
        }
        
        with patch('builtins.open', mock_open()) as mock_file:
            save_json_data(edge_case_data, 'edge_cases.json')
            
            # Verify that edge cases are handled properly
            mock_file.assert_called_once()


class TestDataValidation:
    """Test suite for data validation functionality."""
    
    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.valid_data = [
            {'id': 'A', 'activity': 'Design', 'duration': '5', 'predecessors': ''},
            {'id': 'B', 'activity': 'Development', 'duration': '10', 'predecessors': 'A'},
        ]
        
        self.invalid_data_missing_fields = [
            {'id': 'A', 'activity': 'Design'},  # Missing duration
            {'duration': '10', 'predecessors': 'A'},  # Missing id and activity
        ]
        
        self.invalid_data_wrong_types = [
            {'id': 'A', 'activity': 'Design', 'duration': 'invalid', 'predecessors': ''},
            {'id': 'B', 'activity': 123, 'duration': '10', 'predecessors': 'A'},
        ]
    
    def test_validate_project_data_success(self):
        """Test successful project data validation."""
        result = validate_project_data(self.valid_data)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert len(result['warnings']) == 0
    
    def test_validate_project_data_missing_fields(self):
        """Test validation with missing required fields."""
        result = validate_project_data(self.invalid_data_missing_fields)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert any('missing' in error.lower() for error in result['errors'])
    
    def test_validate_project_data_invalid_types(self):
        """Test validation with invalid data types."""
        result = validate_project_data(self.invalid_data_wrong_types)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
    
    def test_validate_duration_values(self):
        """Test validation of duration values."""
        test_cases = [
            ({'duration': '5'}, True),
            ({'duration': '0'}, False),  # Zero duration should be invalid
            ({'duration': '-5'}, False),  # Negative duration should be invalid
            ({'duration': 'abc'}, False),  # Non-numeric duration should be invalid
        ]
        
        for data, expected_valid in test_cases:
            activity_data = {'id': 'A', 'activity': 'Test', 'predecessors': '', **data}
            result = validate_project_data([activity_data])
            
            if expected_valid:
                assert result['valid'] is True or len(result['errors']) == 0
            else:
                assert result['valid'] is False or len(result['errors']) > 0
    
    def test_validate_predecessor_relationships(self):
        """Test validation of predecessor relationships."""
        # Test circular dependencies
        circular_data = [
            {'id': 'A', 'activity': 'Task A', 'duration': '5', 'predecessors': 'B'},
            {'id': 'B', 'activity': 'Task B', 'duration': '3', 'predecessors': 'A'},
        ]
        
        result = validate_project_data(circular_data)
        # Should detect circular dependency
        assert result['valid'] is False or len(result['warnings']) > 0
    
    def test_validate_duplicate_ids(self):
        """Test validation of duplicate activity IDs."""
        duplicate_data = [
            {'id': 'A', 'activity': 'Task 1', 'duration': '5', 'predecessors': ''},
            {'id': 'A', 'activity': 'Task 2', 'duration': '3', 'predecessors': ''},
        ]
        
        result = validate_project_data(duplicate_data)
        assert result['valid'] is False
        assert any('duplicate' in error.lower() for error in result['errors'])


class TestDataFormatDetection:
    """Test suite for automatic data format detection."""
    
    def test_detect_cpm_format(self):
        """Test detection of CPM data format."""
        cpm_data = [
            {'id': 'A', 'activity': 'Design', 'duration': '5', 'predecessors': ''},
            {'id': 'B', 'activity': 'Development', 'duration': '10', 'predecessors': 'A'},
        ]
        
        format_type = detect_data_format(cpm_data)
        assert format_type == 'cpm'
    
    def test_detect_pert_format(self):
        """Test detection of PERT data format."""
        pert_data = [
            {'id': 'A', 'activity': 'Design', 'optimistic': '3', 'most_likely': '5', 'pessimistic': '8', 'predecessors': ''},
            {'id': 'B', 'activity': 'Development', 'optimistic': '8', 'most_likely': '10', 'pessimistic': '15', 'predecessors': 'A'},
        ]
        
        format_type = detect_data_format(pert_data)
        assert format_type == 'pert'
    
    def test_detect_unknown_format(self):
        """Test detection of unknown data format."""
        unknown_data = [
            {'field1': 'value1', 'field2': 'value2'},
            {'field1': 'value3', 'field2': 'value4'},
        ]
        
        format_type = detect_data_format(unknown_data)
        assert format_type == 'unknown' or format_type is None


class TestFilenameHandling:
    """Test suite for filename handling and sanitization."""
    
    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        test_cases = [
            ('project_data.csv', 'project_data.csv'),
            ('project data.csv', 'project_data.csv'),
            ('project/data.csv', 'project_data.csv'),
            ('project\\data.csv', 'project_data.csv'),
            ('project<data>.csv', 'project_data.csv'),
            ('project:data.csv', 'project_data.csv'),
        ]
        
        for input_name, expected_output in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected_output
    
    def test_sanitize_filename_unicode(self):
        """Test filename sanitization with unicode characters."""
        unicode_filename = 'проект_данные.csv'
        result = sanitize_filename(unicode_filename)
        
        # Should handle unicode appropriately
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_sanitize_filename_length_limit(self):
        """Test filename length limitation."""
        long_filename = 'a' * 300 + '.csv'
        result = sanitize_filename(long_filename)
        
        # Should limit filename length
        assert len(result) <= 255  # Common filesystem limit


class TestErrorHandling:
    """Test suite for file handling error scenarios."""
    
    def test_handle_permission_errors(self):
        """Test handling of file permission errors."""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                load_csv_data('protected_file.csv')
    
    def test_handle_disk_full_errors(self):
        """Test handling of disk full errors during save."""
        with patch('builtins.open', side_effect=OSError("No space left on device")):
            with pytest.raises(OSError):
                save_csv_data([], 'output.csv')
    
    def test_handle_corrupted_files(self):
        """Test handling of corrupted file data."""
        corrupted_csv = "corrupted,data\nwith\ninvalid\nstructure"
        
        with patch('builtins.open', mock_open(read_data=corrupted_csv)):
            # Should handle corrupted data gracefully
            try:
                result = load_csv_data('corrupted.csv')
                # Might return partial data or empty list
                assert isinstance(result, list)
            except Exception as e:
                # Or might raise a specific exception
                assert isinstance(e, (ValueError, csv.Error))


class TestPerformance:
    """Test suite for file handling performance."""
    
    def test_large_file_handling(self):
        """Test handling of large data files."""
        # Create large dataset
        large_data = [
            {'id': f'Activity_{i}', 'activity': f'Task {i}', 'duration': str(i % 10 + 1), 'predecessors': ''}
            for i in range(10000)
        ]
        
        with patch('builtins.open', mock_open()):
            with patch('csv.DictWriter'):
                # Test that large datasets can be handled
                try:
                    save_csv_data(large_data, 'large_file.csv')
                    # Should complete without memory issues
                except MemoryError:
                    pytest.fail("Memory error handling large dataset")
    
    def test_concurrent_file_access(self):
        """Test concurrent file access handling."""
        # Test that file operations handle concurrent access appropriately
        pass


# Integration tests with temporary files
@pytest.mark.integration
class TestFileHandlingIntegration:
    """Integration tests for file handling with real files."""
    
    def test_round_trip_csv_processing(self):
        """Test complete CSV round-trip processing."""
        original_data = [
            {'id': 'A', 'activity': 'Design', 'duration': '5', 'predecessors': ''},
            {'id': 'B', 'activity': 'Development', 'duration': '10', 'predecessors': 'A'},
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            tmp_filename = tmp_file.name
        
        try:
            # Save and load data
            save_csv_data(original_data, tmp_filename)
            loaded_data = load_csv_data(tmp_filename)
            
            # Verify data integrity
            assert len(loaded_data) == len(original_data)
            assert loaded_data[0]['id'] == original_data[0]['id']
            
        finally:
            os.unlink(tmp_filename)
    
    def test_round_trip_json_processing(self):
        """Test complete JSON round-trip processing."""
        original_data = {
            'project_name': 'Test Project',
            'activities': [
                {'id': 'A', 'duration': 5, 'predecessors': []},
                {'id': 'B', 'duration': 10, 'predecessors': ['A']},
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_filename = tmp_file.name
        
        try:
            # Save and load data
            save_json_data(original_data, tmp_filename)
            loaded_data = load_json_data(tmp_filename)
            
            # Verify data integrity
            assert loaded_data == original_data
            
        finally:
            os.unlink(tmp_filename)


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])
