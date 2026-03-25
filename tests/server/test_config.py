"""
Test Server Configuration

Unit tests for server configuration and settings management.
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

# Import configuration
try:
    from pmhelper.server.config import ServerConfig, config
    CONFIG_AVAILABLE = True
except ImportError as e:
    CONFIG_AVAILABLE = False
    pytest.skip(f"Server config not available: {e}", allow_module_level=True)


class TestServerConfig:
    """Test server configuration class."""
    
    def test_default_config_values(self):
        """Test default configuration values."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        config = ServerConfig()
        
        # Test defaults
        assert config.HOST == "localhost"
        assert config.PORT == 8000
        assert config.DEBUG is False
        assert config.DATABASE_FILE == "pmhelper.db"
        assert config.SECRET_KEY == "dev-secret-key-change-in-production"
        assert config.CORS_ORIGINS == ["http://localhost:3000", "http://localhost:8080"]
        assert config.MAX_CONCURRENT_ANALYSES == 5
        assert config.ANALYSIS_TIMEOUT == 300
    
    def test_environment_variable_override(self):
        """Test configuration override from environment variables."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        with patch.dict(os.environ, {
            'PMHELPER_HOST': '0.0.0.0',
            'PMHELPER_PORT': '9000',
            'PMHELPER_DEBUG': 'true',
            'PMHELPER_SECRET_KEY': 'test-secret-key',
            'PMHELPER_MAX_CONCURRENT_ANALYSES': '10'
        }):
            config = ServerConfig()
            
            assert config.HOST == "0.0.0.0"
            assert config.PORT == 9000
            assert config.DEBUG is True
            assert config.SECRET_KEY == "test-secret-key"
            assert config.MAX_CONCURRENT_ANALYSES == 10
    
    def test_database_url_generation(self):
        """Test database URL generation."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = ServerConfig()
            config.DATABASE_DIR = Path(temp_dir)
            
            expected_url = f"sqlite+aiosqlite:///{config.DATABASE_DIR / config.DATABASE_FILE}"
            assert config.DATABASE_URL == expected_url
    
    def test_boolean_environment_variables(self):
        """Test boolean environment variable parsing."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        # Test various boolean representations
        test_cases = [
            ('true', True),
            ('True', True),
            ('TRUE', True),
            ('1', True),
            ('yes', True),
            ('false', False),
            ('False', False),
            ('FALSE', False),
            ('0', False),
            ('no', False),
            ('', False),
            ('invalid', False)
        ]
        
        for env_value, expected in test_cases:
            with patch.dict(os.environ, {'PMHELPER_DEBUG': env_value}):
                config = ServerConfig()
                assert config.DEBUG == expected, f"Failed for value: {env_value}"
    
    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from environment."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        # Single origin
        with patch.dict(os.environ, {'PMHELPER_CORS_ORIGINS': 'http://example.com'}):
            config = ServerConfig()
            assert config.CORS_ORIGINS == ["http://example.com"]
        
        # Multiple origins (comma-separated)
        with patch.dict(os.environ, {
            'PMHELPER_CORS_ORIGINS': 'http://example.com,https://api.example.com,http://localhost:3000'
        }):
            config = ServerConfig()
            expected = ["http://example.com", "https://api.example.com", "http://localhost:3000"]
            assert config.CORS_ORIGINS == expected
        
        # Origins with spaces (should be stripped)
        with patch.dict(os.environ, {
            'PMHELPER_CORS_ORIGINS': 'http://example.com , https://api.example.com , http://localhost:3000'
        }):
            config = ServerConfig()
            expected = ["http://example.com", "https://api.example.com", "http://localhost:3000"]
            assert config.CORS_ORIGINS == expected
    
    def test_integer_environment_variables(self):
        """Test integer environment variable parsing."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        # Valid integers
        with patch.dict(os.environ, {
            'PMHELPER_PORT': '5000',
            'PMHELPER_MAX_CONCURRENT_ANALYSES': '15',
            'PMHELPER_ANALYSIS_TIMEOUT': '600'
        }):
            config = ServerConfig()
            assert config.PORT == 5000
            assert config.MAX_CONCURRENT_ANALYSES == 15
            assert config.ANALYSIS_TIMEOUT == 600
        
        # Invalid integers (should use defaults)
        with patch.dict(os.environ, {
            'PMHELPER_PORT': 'invalid',
            'PMHELPER_MAX_CONCURRENT_ANALYSES': 'not-a-number'
        }):
            config = ServerConfig()
            # Should fallback to defaults
            assert config.PORT == 8000  # Default value
            assert config.MAX_CONCURRENT_ANALYSES == 5  # Default value
    
    def test_path_configuration(self):
        """Test path configuration."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = Path(temp_dir) / "test_db"
            
            with patch.dict(os.environ, {'PMHELPER_DATABASE_DIR': str(test_path)}):
                config = ServerConfig()
                assert config.DATABASE_DIR == test_path
    
    def test_config_validation(self):
        """Test configuration validation."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        config = ServerConfig()
        
        # Test port range
        assert 1 <= config.PORT <= 65535
        
        # Test positive values
        assert config.MAX_CONCURRENT_ANALYSES > 0
        assert config.ANALYSIS_TIMEOUT > 0
        
        # Test required fields
        assert config.SECRET_KEY is not None
        assert len(config.SECRET_KEY) > 0
        assert config.DATABASE_FILE is not None
        assert len(config.DATABASE_FILE) > 0
    
    def test_production_config_warnings(self):
        """Test production configuration warnings."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        # In production mode with default secret key (should warn)
        with patch.dict(os.environ, {'PMHELPER_DEBUG': 'false'}):
            config = ServerConfig()
            
            # Default secret key in non-debug mode should be flagged
            if config.SECRET_KEY == "dev-secret-key-change-in-production":
                # This would trigger a warning in real application
                assert not config.DEBUG  # Ensure we're in non-debug mode


class TestGlobalConfig:
    """Test global configuration instance."""
    
    def test_global_config_instance(self):
        """Test global configuration instance."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        # Test that global config exists
        assert config is not None
        assert isinstance(config, ServerConfig)
        
        # Test that it has expected attributes
        assert hasattr(config, 'HOST')
        assert hasattr(config, 'PORT')
        assert hasattr(config, 'DEBUG')
        assert hasattr(config, 'DATABASE_URL')
    
    def test_config_immutability(self):
        """Test that certain config values maintain consistency."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        # Get initial values
        initial_host = config.HOST
        initial_port = config.PORT
        
        # These should remain consistent within the same process
        assert config.HOST == initial_host
        assert config.PORT == initial_port
    
    def test_config_string_representation(self):
        """Test config string representation (for debugging)."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        config_str = str(config)
        
        # Should contain key configuration info (but not sensitive data)
        assert "host" in config_str.lower()
        assert "port" in config_str.lower()
        
        # Should NOT contain sensitive information
        assert config.SECRET_KEY not in config_str


class TestConfigEdgeCases:
    """Test configuration edge cases and error handling."""
    
    def test_empty_environment_variables(self):
        """Test handling of empty environment variables."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        with patch.dict(os.environ, {
            'PMHELPER_HOST': '',
            'PMHELPER_SECRET_KEY': '',
            'PMHELPER_CORS_ORIGINS': ''
        }):
            config = ServerConfig()
            
            # Empty values should fall back to defaults
            assert config.HOST == "localhost"  # Default
            assert config.SECRET_KEY == "dev-secret-key-change-in-production"  # Default
            assert config.CORS_ORIGINS == ["http://localhost:3000", "http://localhost:8080"]  # Default
    
    def test_malformed_environment_variables(self):
        """Test handling of malformed environment variables."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        with patch.dict(os.environ, {
            'PMHELPER_PORT': '-1000',  # Negative port
            'PMHELPER_MAX_CONCURRENT_ANALYSES': '0',  # Zero concurrent analyses
            'PMHELPER_ANALYSIS_TIMEOUT': '-300'  # Negative timeout
        }):
            config = ServerConfig()
            
            # Should handle invalid values gracefully
            # (Implementation might clamp values or use defaults)
            assert config.PORT > 0
            assert config.MAX_CONCURRENT_ANALYSES > 0
            assert config.ANALYSIS_TIMEOUT > 0
    
    def test_unicode_environment_variables(self):
        """Test handling of unicode in environment variables."""
        if not CONFIG_AVAILABLE:
            pytest.skip("Server config not available")
        
        with patch.dict(os.environ, {
            'PMHELPER_SECRET_KEY': 'secret-key-with-unicode-密钥',
            'PMHELPER_HOST': 'localhost'  # Keep simple for host
        }):
            config = ServerConfig()
            
            # Should handle unicode characters
            assert 'unicode' in config.SECRET_KEY or '密钥' in config.SECRET_KEY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])