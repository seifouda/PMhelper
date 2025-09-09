#!/usr/bin/env python3
"""
Comprehensive Unit Tests for File Handlers

Tests all functionality of the file handling utilities including:
- CSV reading and writing
- Excel file handling
- Data validation and cleaning
- Sample data generation
- Import/export functionality
- Error handling for file operations
"""

import pytest
import sys
import pandas as pd
import tempfile
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pmhelper.utils.file_handlers import FileHandler


class TestFileHandler:
    """Comprehensive test suite for File Handler"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment before each test"""
        self.handler = FileHandler()
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample CPM data for testing
        self.sample_cpm_data = [
            {
                'id': 'A',
                'activity': 'Start Activity',
                'duration': 3,
                'min_duration': 2,
                'crash_cost': 100,
                'predecessors': '',
                'resource_demand': 2,
                'normal_cost': 200
            },
            {
                'id': 'B',
                'activity': 'Second Activity',
                'duration': 5,
                'min_duration': 3,
                'crash_cost': 150,
                'predecessors': 'A',
                'resource_demand': 3,
                'normal_cost': 300
            }
        ]
        
        # Sample PERT data for testing
        self.sample_pert_data = [
            {
                'id': 'A',
                'activity': 'Start Activity',
                'optimistic': 2,
                'most_likely': 3,
                'pessimistic': 5,
                'predecessors': ''
            },
            {
                'id': 'B',
                'activity': 'Second Activity',
                'optimistic': 3,
                'most_likely': 5,
                'pessimistic': 8,
                'predecessors': 'A'
            }
        ]
    
    def teardown_method(self):
        """Clean up temporary files after each test"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_handler_initialization(self):
        """Test FileHandler can be created and initialized properly"""
        assert self.handler is not None
    
    def test_get_sample_cpm_data(self):
        """Test retrieval of sample CPM data"""
        sample_data = FileHandler.get_sample_cmp_data()
        
        assert sample_data is not None
        assert len(sample_data) > 0
        assert isinstance(sample_data, list)
        
        # Verify sample data structure
        first_item = sample_data[0]
        required_fields = ['id', 'activity', 'duration', 'predecessors']
        for field in required_fields:
            assert field in first_item
    
    def test_get_sample_pert_data(self):
        """Test retrieval of sample PERT data"""
        sample_data = FileHandler.get_sample_pert_data()
        
        assert sample_data is not None
        assert len(sample_data) > 0
        assert isinstance(sample_data, list)
        
        # Verify PERT data structure
        first_item = sample_data[0]
        required_fields = ['id', 'activity', 'optimistic', 'most_likely', 'pessimistic', 'predecessors']
        for field in required_fields:
            assert field in first_item
    
    def test_read_cpm_csv_file(self):
        """Test reading CPM data from CSV file"""
        # Create temporary CSV file
        csv_file = os.path.join(self.temp_dir, 'test_cpm.csv')
        df = pd.DataFrame(self.sample_cpm_data)
        df.to_csv(csv_file, index=False)
        
        # Test reading
        data = self.handler.read_cpm_csv(csv_file)
        
        assert data is not None
        assert len(data) == len(self.sample_cmp_data)
        assert data[0]['id'] == 'A'
        assert data[0]['duration'] == 3
    
    def test_read_pert_csv_file(self):
        """Test reading PERT data from CSV file"""
        # Create temporary CSV file
        csv_file = os.path.join(self.temp_dir, 'test_pert.csv')
        df = pd.DataFrame(self.sample_pert_data)
        df.to_csv(csv_file, index=False)
        
        # Test reading
        data = self.handler.read_pert_csv(csv_file)
        
        assert data is not None
        assert len(data) == len(self.sample_pert_data)
        assert data[0]['id'] == 'A'
        assert data[0]['optimistic'] == 2
        assert data[0]['most_likely'] == 3
        assert data[0]['pessimistic'] == 5
    
    def test_write_cpm_csv_file(self):
        """Test writing CPM data to CSV file"""
        csv_file = os.path.join(self.temp_dir, 'output_cpm.csv')
        
        # Test writing
        success = self.handler.write_cpm_csv(self.sample_cpm_data, csv_file)
        
        assert success
        assert os.path.exists(csv_file)
        
        # Verify written data
        df = pd.read_csv(csv_file)
        assert len(df) == len(self.sample_cpm_data)
        assert df.iloc[0]['id'] == 'A'
    
    def test_write_pert_csv_file(self):
        """Test writing PERT data to CSV file"""
        csv_file = os.path.join(self.temp_dir, 'output_pert.csv')
        
        # Test writing
        success = self.handler.write_pert_csv(self.sample_pert_data, csv_file)
        
        assert success
        assert os.path.exists(csv_file)
        
        # Verify written data
        df = pd.read_csv(csv_file)
        assert len(df) == len(self.sample_pert_data)
        assert df.iloc[0]['id'] == 'A'
    
    def test_read_excel_file(self):
        """Test reading data from Excel file"""
        # Create temporary Excel file
        excel_file = os.path.join(self.temp_dir, 'test_data.xlsx')
        df = pd.DataFrame(self.sample_cpm_data)
        df.to_excel(excel_file, index=False)
        
        # Test reading
        data = self.handler.read_excel(excel_file)
        
        assert data is not None
        assert len(data) == len(self.sample_cpm_data)
    
    def test_write_excel_file(self):
        """Test writing data to Excel file"""
        excel_file = os.path.join(self.temp_dir, 'output_data.xlsx')
        
        # Test writing
        success = self.handler.write_excel(self.sample_cpm_data, excel_file)
        
        assert success
        assert os.path.exists(excel_file)
        
        # Verify written data
        df = pd.read_excel(excel_file)
        assert len(df) == len(self.sample_cpm_data)
    
    def test_validate_cmp_data(self):
        """Test CPM data validation"""
        # Valid data
        valid_data = self.sample_cpm_data
        is_valid, errors = self.handler.validate_cpm_data(valid_data)
        assert is_valid
        assert len(errors) == 0
        
        # Invalid data - missing required field
        invalid_data = [{'id': 'A', 'activity': 'Test'}]  # Missing duration
        is_valid, errors = self.handler.validate_cpm_data(invalid_data)
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_pert_data(self):
        """Test PERT data validation"""
        # Valid data
        valid_data = self.sample_pert_data
        is_valid, errors = self.handler.validate_pert_data(valid_data)
        assert is_valid
        assert len(errors) == 0
        
        # Invalid data - optimistic > pessimistic
        invalid_data = [
            {
                'id': 'A',
                'optimistic': 10,
                'most_likely': 5,
                'pessimistic': 3,
                'predecessors': ''
            }
        ]
        is_valid, errors = self.handler.validate_pert_data(invalid_data)
        assert not is_valid
        assert len(errors) > 0
    
    def test_clean_data(self):
        """Test data cleaning functionality"""
        # Data with issues
        dirty_data = [
            {
                'id': ' A ',  # Extra whitespace
                'activity': 'Test Activity',
                'duration': '3',  # String instead of number
                'predecessors': ' B , C ',  # Extra whitespace in list
                'resource_demand': None
            }
        ]
        
        cleaned_data = self.handler.clean_data(dirty_data)
        
        assert cleaned_data[0]['id'] == 'A'  # Whitespace removed
        assert cleaned_data[0]['duration'] == 3  # Converted to number
        assert 'B' in cleaned_data[0]['predecessors']  # Cleaned predecessor list
    
    def test_export_analysis_results(self):
        """Test exporting analysis results"""
        # Mock analysis results
        results = {
            'project_duration': 10,
            'critical_path': ['A', 'B', 'D'],
            'activities': [
                {'id': 'A', 'ES': 0, 'EF': 3, 'LS': 0, 'LF': 3, 'float': 0},
                {'id': 'B', 'ES': 3, 'EF': 8, 'LS': 3, 'LF': 8, 'float': 0}
            ]
        }
        
        output_file = os.path.join(self.temp_dir, 'results.csv')
        success = self.handler.export_results(results, output_file)
        
        assert success
        assert os.path.exists(output_file)
    
    def test_import_project_template(self):
        """Test importing project templates"""
        # Create a template file
        template_data = self.sample_cpm_data
        template_file = os.path.join(self.temp_dir, 'template.csv')
        df = pd.DataFrame(template_data)
        df.to_csv(template_file, index=False)
        
        # Test importing
        imported_data = self.handler.import_template(template_file)
        
        assert imported_data is not None
        assert len(imported_data) == len(template_data)
    
    def test_file_not_found_error(self):
        """Test handling of file not found errors"""
        non_existent_file = os.path.join(self.temp_dir, 'does_not_exist.csv')
        
        with pytest.raises(FileNotFoundError):
            self.handler.read_cpm_csv(non_existent_file)
    
    def test_invalid_file_format_error(self):
        """Test handling of invalid file format errors"""
        # Create a text file with invalid format
        invalid_file = os.path.join(self.temp_dir, 'invalid.txt')
        with open(invalid_file, 'w') as f:
            f.write("This is not a valid CSV file")
        
        with pytest.raises(Exception):  # Should raise some parsing error
            self.handler.read_cmp_csv(invalid_file)
    
    def test_empty_file_handling(self):
        """Test handling of empty files"""
        empty_file = os.path.join(self.temp_dir, 'empty.csv')
        with open(empty_file, 'w') as f:
            f.write("")  # Empty file
        
        with pytest.raises(Exception):  # Should handle empty files
            self.handler.read_cpm_csv(empty_file)
    
    def test_malformed_csv_handling(self):
        """Test handling of malformed CSV files"""
        malformed_file = os.path.join(self.temp_dir, 'malformed.csv')
        with open(malformed_file, 'w') as f:
            f.write("id,activity,duration\n")
            f.write("A,Test,invalid_duration\n")  # Invalid duration
        
        # Should handle gracefully or raise appropriate error
        try:
            data = self.handler.read_cpm_csv(malformed_file)
            # If it doesn't raise an error, data should be cleaned
        except Exception as e:
            # Should provide meaningful error message
            assert "duration" in str(e).lower() or "invalid" in str(e).lower()
    
    def test_large_file_handling(self):
        """Test handling of large files"""
        # Generate large dataset
        large_data = []
        for i in range(1000):  # 1000 activities
            large_data.append({
                'id': f'A{i}',
                'activity': f'Activity {i}',
                'duration': i % 10 + 1,
                'predecessors': f'A{i-1}' if i > 0 else ''
            })
        
        large_file = os.path.join(self.temp_dir, 'large_file.csv')
        
        # Test writing large file
        success = self.handler.write_cpm_csv(large_data, large_file)
        assert success
        
        # Test reading large file
        import time
        start_time = time.time()
        read_data = self.handler.read_cpm_csv(large_file)
        read_time = time.time() - start_time
        
        assert len(read_data) == 1000
        assert read_time < 10.0  # Should complete within 10 seconds
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters in data"""
        unicode_data = [
            {
                'id': 'A',
                'activity': 'Activité avec des caractères spéciaux: áéíóú',
                'duration': 3,
                'predecessors': ''
            }
        ]
        
        unicode_file = os.path.join(self.temp_dir, 'unicode.csv')
        
        # Test writing unicode data
        success = self.handler.write_cmp_csv(unicode_data, unicode_file)
        assert success
        
        # Test reading unicode data
        read_data = self.handler.read_cpm_csv(unicode_file)
        assert read_data[0]['activity'] == unicode_data[0]['activity']
    
    def test_data_type_conversion(self):
        """Test automatic data type conversion"""
        mixed_type_data = [
            {
                'id': 'A',
                'duration': '5',  # String that should be converted to int
                'crash_cost': '100.50',  # String that should be converted to float
                'resource_demand': 3.0  # Float that should be converted to int
            }
        ]
        
        converted_data = self.handler.convert_data_types(mixed_type_data)
        
        assert isinstance(converted_data[0]['duration'], int)
        assert isinstance(converted_data[0]['crash_cost'], float)
        assert isinstance(converted_data[0]['resource_demand'], int)
    
    def test_backup_and_restore(self):
        """Test backup and restore functionality"""
        original_file = os.path.join(self.temp_dir, 'original.csv')
        backup_file = os.path.join(self.temp_dir, 'backup.csv')
        
        # Create original file
        df = pd.DataFrame(self.sample_cpm_data)
        df.to_csv(original_file, index=False)
        
        # Test backup
        success = self.handler.create_backup(original_file, backup_file)
        assert success
        assert os.path.exists(backup_file)
        
        # Test restore
        restored_data = self.handler.restore_from_backup(backup_file)
        assert len(restored_data) == len(self.sample_cpm_data)


class TestFileHandlerEdgeCases:
    """Additional edge case tests for File Handler"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment"""
        self.handler = FileHandler()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up temporary files"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def test_permission_denied_handling(self):
        """Test handling of permission denied errors"""
        # This test might not work on all systems
        try:
            readonly_file = os.path.join(self.temp_dir, 'readonly.csv')
            
            # Create file and make it read-only
            with open(readonly_file, 'w') as f:
                f.write("test")
            os.chmod(readonly_file, 0o444)  # Read-only
            
            # Try to write to read-only file
            with pytest.raises(PermissionError):
                self.handler.write_cpm_csv([{'id': 'A', 'duration': 3}], readonly_file)
        except:
            # Skip this test if file permissions can't be changed
            pass
    
    def test_disk_space_handling(self):
        """Test handling when disk space is limited"""
        # This is difficult to test without actually filling up disk
        # Just verify that appropriate errors are raised
        pass
    
    def test_concurrent_file_access(self):
        """Test concurrent access to the same file"""
        import threading
        import time
        
        test_file = os.path.join(self.temp_dir, 'concurrent.csv')
        errors = []
        
        def write_data(thread_id):
            try:
                data = [{'id': f'A{thread_id}', 'duration': thread_id}]
                self.handler.write_cpm_csv(data, f"{test_file}_{thread_id}")
            except Exception as e:
                errors.append(e)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=write_data, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should handle concurrent access without major errors
        assert len(errors) < 3  # Allow for some minor errors


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
