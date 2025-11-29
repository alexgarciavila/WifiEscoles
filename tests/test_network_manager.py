"""Unit tests for NetworkManager class."""

import pytest
from unittest.mock import patch, MagicMock
import subprocess
from wifi_connector.network.manager import NetworkManager


@pytest.fixture
def network_manager():
    """Provide a NetworkManager instance for testing."""
    return NetworkManager()


@pytest.fixture
def mock_netsh_output_valid():
    """Provide sample valid netsh output with multiple networks."""
    return """
Interface name : Wi-Fi
There are 3 networks currently visible.

SSID 1 : gencat_ENS_EDU
    Network type            : Infrastructure
    Authentication          : WPA2-Enterprise
    Encryption              : CCMP

SSID 2 : OtherNetwork
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP

SSID 3 : TestNetwork
    Network type            : Infrastructure
    Authentication          : Open
    Encryption              : None
"""


@pytest.fixture
def mock_netsh_output_empty():
    """Provide sample netsh output with no networks."""
    return """
Interface name : Wi-Fi
There are 0 networks currently visible.
"""


@pytest.fixture
def mock_netsh_output_malformed():
    """Provide malformed netsh output."""
    return """
Some random text
No SSID information here
Just garbage data
"""


class TestGetAvailableNetworks:
    """Tests for get_available_networks() method."""
    
    @patch('subprocess.run')
    def test_returns_list_of_networks_from_valid_output(
        self,
        mock_run,
        network_manager,
        mock_netsh_output_valid
    ):
        """Test parsing valid netsh output returns correct network list."""
        mock_run.return_value = MagicMock(
            stdout=mock_netsh_output_valid,
            returncode=0
        )
        
        networks = network_manager.get_available_networks()
        
        assert len(networks) == 3
        assert "gencat_ENS_EDU" in networks
        assert "OtherNetwork" in networks
        assert "TestNetwork" in networks
    
    @patch('subprocess.run')
    def test_returns_empty_list_when_no_networks_found(
        self,
        mock_run,
        network_manager,
        mock_netsh_output_empty
    ):
        """Test that empty network list is returned when no networks found."""
        mock_run.return_value = MagicMock(
            stdout=mock_netsh_output_empty,
            returncode=0
        )
        
        networks = network_manager.get_available_networks()
        
        assert networks == []
    
    @patch('subprocess.run')
    def test_returns_empty_list_for_malformed_output(
        self,
        mock_run,
        network_manager,
        mock_netsh_output_malformed
    ):
        """Test that malformed output returns empty list."""
        mock_run.return_value = MagicMock(
            stdout=mock_netsh_output_malformed,
            returncode=0
        )
        
        networks = network_manager.get_available_networks()
        
        assert networks == []
    
    @patch('subprocess.run')
    def test_returns_empty_list_on_subprocess_error(
        self,
        mock_run,
        network_manager
    ):
        """Test that subprocess error returns empty list."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="netsh",
            output="Error"
        )
        
        networks = network_manager.get_available_networks()
        
        assert networks == []
    
    @patch('subprocess.run')
    def test_calls_netsh_with_correct_arguments(
        self,
        mock_run,
        network_manager,
        mock_netsh_output_valid
    ):
        """Test that netsh is called with correct arguments."""
        mock_run.return_value = MagicMock(
            stdout=mock_netsh_output_valid,
            returncode=0
        )
        
        network_manager.get_available_networks()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args == ["netsh", "wlan", "show", "networks"]
    
    @patch('subprocess.run')
    def test_uses_cp850_encoding(
        self,
        mock_run,
        network_manager,
        mock_netsh_output_valid
    ):
        """Test that CP850 encoding is used for netsh command."""
        mock_run.return_value = MagicMock(
            stdout=mock_netsh_output_valid,
            returncode=0
        )
        
        network_manager.get_available_networks()
        
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs.get('encoding') == 'cp850'


class TestIsNetworkAvailable:
    """Tests for is_network_available() method."""
    
    @patch('subprocess.run')
    def test_returns_true_when_network_is_available(
        self,
        mock_run,
        network_manager,
        mock_netsh_output_valid
    ):
        """Test that True is returned when network is in the list."""
        mock_run.return_value = MagicMock(
            stdout=mock_netsh_output_valid,
            returncode=0
        )
        
        result = network_manager.is_network_available("gencat_ENS_EDU")
        
        assert result is True
    
    @patch('subprocess.run')
    def test_returns_false_when_network_is_not_available(
        self,
        mock_run,
        network_manager,
        mock_netsh_output_valid
    ):
        """Test that False is returned when network is not in the list."""
        mock_run.return_value = MagicMock(
            stdout=mock_netsh_output_valid,
            returncode=0
        )
        
        result = network_manager.is_network_available("NonExistentNetwork")
        
        assert result is False
    
    @patch('subprocess.run')
    def test_returns_false_when_no_networks_available(
        self,
        mock_run,
        network_manager,
        mock_netsh_output_empty
    ):
        """Test that False is returned when no networks are available."""
        mock_run.return_value = MagicMock(
            stdout=mock_netsh_output_empty,
            returncode=0
        )
        
        result = network_manager.is_network_available("AnyNetwork")
        
        assert result is False


class TestDisconnect:
    """Tests for disconnect() method."""
    
    @patch('subprocess.run')
    def test_returns_true_on_successful_disconnect(
        self,
        mock_run,
        network_manager
    ):
        """Test that True is returned on successful disconnect."""
        mock_run.return_value = MagicMock(
            stdout="Disconnection request was completed successfully.",
            returncode=0
        )
        
        result = network_manager.disconnect()
        
        assert result is True
    
    @patch('subprocess.run')
    def test_calls_netsh_disconnect_command(
        self,
        mock_run,
        network_manager
    ):
        """Test that netsh disconnect command is called correctly."""
        mock_run.return_value = MagicMock(
            stdout="Success",
            returncode=0
        )
        
        network_manager.disconnect()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args == ["netsh", "wlan", "disconnect"]
    
    @patch('subprocess.run')
    def test_returns_false_on_subprocess_error(
        self,
        mock_run,
        network_manager
    ):
        """Test that False is returned when subprocess fails."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="netsh",
            output="Error"
        )
        
        result = network_manager.disconnect()
        
        assert result is False


class TestExecuteNetshCommand:
    """Tests for _execute_netsh_command() private method."""
    
    @patch('subprocess.run')
    def test_executes_command_with_netsh_prefix(
        self,
        mock_run,
        network_manager
    ):
        """Test that command is executed with netsh prefix."""
        mock_run.return_value = MagicMock(
            stdout="Success",
            returncode=0
        )
        
        network_manager._execute_netsh_command(["wlan", "show", "networks"])
        
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "netsh"
        assert call_args[1:] == ["wlan", "show", "networks"]
    
    @patch('subprocess.run')
    def test_returns_stdout_on_success(
        self,
        mock_run,
        network_manager
    ):
        """Test that stdout is returned on successful execution."""
        expected_output = "Command output"
        mock_run.return_value = MagicMock(
            stdout=expected_output,
            returncode=0
        )
        
        result = network_manager._execute_netsh_command(["test"])
        
        assert result == expected_output
    
    @patch('subprocess.run')
    def test_raises_exception_on_command_failure(
        self,
        mock_run,
        network_manager
    ):
        """Test that exception is raised when command fails."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="netsh",
            output="Error"
        )
        
        with pytest.raises(subprocess.CalledProcessError):
            network_manager._execute_netsh_command(["test"])
    
    @patch('subprocess.run')
    def test_uses_check_true_flag(
        self,
        mock_run,
        network_manager
    ):
        """Test that check=True is used in subprocess.run."""
        mock_run.return_value = MagicMock(
            stdout="Success",
            returncode=0
        )
        
        network_manager._execute_netsh_command(["test"])
        
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs.get('check') is True


class TestParseNetworkList:
    """Tests for _parse_network_list() private method."""
    
    def test_extracts_ssids_from_valid_output(
        self,
        network_manager,
        mock_netsh_output_valid
    ):
        """Test that SSIDs are correctly extracted from valid output."""
        networks = network_manager._parse_network_list(
            mock_netsh_output_valid
        )
        assert networks[0] == "gencat_ENS_EDU"
        assert networks[1] == "OtherNetwork"
        assert networks[2] == "TestNetwork"
    
    def test_returns_empty_list_for_no_networks(
        self,
        network_manager,
        mock_netsh_output_empty
    ):
        """Test that empty list is returned when no networks found."""
        networks = network_manager._parse_network_list(
            mock_netsh_output_empty
        )
        
        assert networks == []
    
    def test_returns_empty_list_for_malformed_output(
        self,
        network_manager,
        mock_netsh_output_malformed
    ):
        """Test that empty list is returned for malformed output."""
        networks = network_manager._parse_network_list(
            mock_netsh_output_malformed
        )
        
        assert networks == []
    
    def test_filters_duplicate_ssids(self, network_manager):
        """Test that duplicate SSIDs are filtered out."""
        output = """
SSID 1 : NetworkA
SSID 2 : NetworkB
SSID 3 : NetworkA
"""
        networks = network_manager._parse_network_list(output)
        
        assert len(networks) == 2
        assert networks == ["NetworkA", "NetworkB"]
    
    def test_filters_empty_ssids(self, network_manager):
        """Test that empty SSIDs are filtered out."""
        output = """
SSID 1 : 
SSID 2 : ValidNetwork
SSID 3 : 
"""
        networks = network_manager._parse_network_list(output)
        
        assert len(networks) == 1
        assert networks == ["ValidNetwork"]
    
    def test_handles_ssids_with_spaces(self, network_manager):
        """Test that SSIDs with spaces are correctly parsed."""
        output = """
SSID 1 : Network With Spaces
SSID 2 : Another Network
"""
        networks = network_manager._parse_network_list(output)
        
        assert len(networks) == 2
        assert networks[0] == "Network With Spaces"
        assert networks[1] == "Another Network"
    
    def test_handles_ssids_with_special_characters(self, network_manager):
        """Test that SSIDs with special characters are parsed."""
        output = """
SSID 1 : Network-123_Test
SSID 2 : Network@Home
"""
        networks = network_manager._parse_network_list(output)
        
        assert len(networks) == 2
        assert networks[0] == "Network-123_Test"
        assert networks[1] == "Network@Home"
