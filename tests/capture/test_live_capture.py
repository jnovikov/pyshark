import sys

try:
    import mock
except ModuleNotFoundError:
    from unittest import mock
import pytest

import pyshark


@pytest.yield_fixture(params=[["wlan0"], ["wlan0mon", "wlan1mon"]])
def interfaces(request):
    with mock.patch("pyshark.tshark.tshark.get_tshark_interfaces", return_value=request.param):
        yield request.param


@pytest.fixture
def capture(interfaces):
    return pyshark.LiveCapture(interface=interfaces)


@pytest.mark.parametrize("monitoring", [True, False])
def test_get_dumpcap_interface_parameter(capture, monitoring, interfaces):
    # type: (pyshark.LiveCapture, bool, list) -> None
    capture.monitor_mode = monitoring
    dumpcap_parameters = capture._get_dumpcap_parameters()
    dumpcap_interfaces = [dumpcap_parameters[index + 1]
                          for index, value in enumerate(dumpcap_parameters)
                          if value == "-i"]
    assert dumpcap_interfaces == interfaces


def test_check_capture_filter_has_quotes(capture):
    sys = mock.MagicMock()
    sys.configure_mock(platform='win32')
    filter_string = "tcp port 80"
    capture.bpf_filter = filter_string
    assert filter_string in capture._get_dumpcap_parameters()
    sys.configure_mock(platform='linux2')
    capture.bpf_filter = filter_string
    quoted_filter = '"%s"' % filter_string
    assert quoted_filter in capture._get_dumpcap_parameters()
