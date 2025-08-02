# Testing Guide

Comprehensive testing guide for the HiDock Next project covering all three applications.

## Table of Contents

- [Overview](#overview)
- [Desktop Application Testing](#desktop-application-testing)
- [Web Application Testing](#web-application-testing)
- [Audio Insights Extractor Testing](#audio-insights-extractor-testing)
- [Integration Testing](#integration-testing)
- [CI/CD Testing](#cicd-testing)

## Overview

The HiDock Next project uses different testing frameworks for each application:

- **Desktop App:** pytest for Python
- **Web App:** Vitest for React/TypeScript
- **Audio Insights:** Vitest for React/TypeScript

### Testing Philosophy

1. **Unit Tests:** Test individual components/functions in isolation
2. **Integration Tests:** Test component interactions
3. **Device Tests:** Test actual HiDock hardware (when available)
4. **Mock Tests:** Test with simulated devices and AI providers

## Desktop Application Testing

### Setup

```bash
cd hidock-desktop-app
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_audio_player.py

# Run specific test
pytest tests/test_audio_player.py::test_play_audio

# Run with coverage
pytest --cov=. --cov-report=html

# Run by marker
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m device        # Device tests (requires hardware)
```

### Test Structure

```
hidock-desktop-app/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_audio_player.py
│   ├── test_device_communication.py
│   ├── test_file_operations.py
│   ├── test_gui_components.py
│   ├── test_main.py
│   └── test_transcription.py
└── pytest.ini               # pytest configuration
```

### Writing Tests

#### Unit Test Example

```python
import pytest
from audio_player import AudioPlayer

class TestAudioPlayer:
    @pytest.mark.unit
    def test_load_audio_file(self):
        player = AudioPlayer()
        result = player.load("test.wav")
        assert result is True

    @pytest.mark.unit
    def test_invalid_file_format(self):
        player = AudioPlayer()
        with pytest.raises(ValueError):
            player.load("test.xyz")
```

#### Integration Test Example

```python
@pytest.mark.integration
def test_device_to_player_integration(mock_device, audio_player):
    # Test that device can stream to player
    recording = mock_device.get_recording(0)
    audio_player.load_from_stream(recording.stream)
    assert audio_player.is_ready()
```

#### Device Test Example

```python
@pytest.mark.device
@pytest.mark.skipif(not has_device(), reason="No HiDock device connected")
def test_real_device_connection():
    device = HiDockDevice()
    assert device.connect() is True
    assert device.get_device_info() is not None
```

### Mocking

```python
# Mock AI providers
@pytest.fixture
def mock_ai_service(mocker):
    mock = mocker.patch('ai_service.AIService')
    mock.transcribe.return_value = "Mocked transcription"
    return mock

# Mock device
@pytest.fixture
def mock_device(mocker):
    mock = mocker.patch('hidock_device.HiDockDevice')
    mock.is_connected.return_value = True
    return mock
```

### Coverage Requirements

- Minimum coverage: 80%
- Critical paths: 95%
- CLI components: 90%

## Web Application Testing

### Setup

```bash
cd hidock-web-app
npm install
```

### Running Tests

```bash
# Run all tests
npm run test

# Watch mode
npm run test:watch

# With UI
npm run test:ui

# Coverage report
npm run test:coverage

# Specific file
npm run test src/services/deviceService.test.ts
```

### Test Structure

```
hidock-web-app/
├── src/
│   ├── test/
│   │   ├── setup.ts           # Test setup
│   │   └── utils.tsx          # Test utilities
│   ├── services/
│   │   ├── deviceService.test.ts
│   │   └── geminiService.test.ts
│   └── components/
│       └── __tests__/         # Component tests
└── vitest.config.ts           # Vitest configuration
```

### Writing Tests

#### Component Test Example

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { DeviceList } from '../DeviceList';

describe('DeviceList', () => {
  it('displays connected devices', () => {
    const devices = [
      { id: '1', name: 'HiDock H1', status: 'connected' }
    ];

    render(<DeviceList devices={devices} />);

    expect(screen.getByText('HiDock H1')).toBeInTheDocument();
    expect(screen.getByText('connected')).toBeInTheDocument();
  });

  it('handles device selection', () => {
    const onSelect = vi.fn();
    render(<DeviceList devices={devices} onSelect={onSelect} />);

    fireEvent.click(screen.getByText('HiDock H1'));
    expect(onSelect).toHaveBeenCalledWith('1');
  });
});
```

#### Service Test Example

```typescript
import { deviceService } from '../deviceService';
import { mockDevice } from '../test/utils';

describe('DeviceService', () => {
  it('connects to device', async () => {
    const device = mockDevice();
    const result = await deviceService.connect(device);

    expect(result.success).toBe(true);
    expect(result.device).toBeDefined();
  });

  it('handles connection errors', async () => {
    const device = mockDevice({ failConnection: true });
    const result = await deviceService.connect(device);

    expect(result.success).toBe(false);
    expect(result.error).toContain('Failed to connect');
  });
});
```

### Mocking WebUSB

```typescript
// Mock WebUSB API
global.navigator.usb = {
  requestDevice: vi.fn().mockResolvedValue(mockUSBDevice),
  getDevices: vi.fn().mockResolvedValue([]),
};

// Mock USB Device
const mockUSBDevice = {
  open: vi.fn().mockResolvedValue(undefined),
  selectConfiguration: vi.fn().mockResolvedValue(undefined),
  claimInterface: vi.fn().mockResolvedValue(undefined),
  transferIn: vi.fn().mockResolvedValue({ data: new DataView(new ArrayBuffer(64)) }),
  transferOut: vi.fn().mockResolvedValue({ status: 'ok' }),
};
```

## Audio Insights Extractor Testing

### Setup

```bash
cd audio-insights-extractor
npm install
```

### Running Tests

Similar to web app, using Vitest:

```bash
npm run test
npm run test:watch
npm run test:coverage
```

### Test Focus Areas

1. **Audio Processing:**
   - File upload handling
   - Format validation
   - Size limits

2. **AI Integration:**
   - Gemini API mocking
   - Error handling
   - Rate limiting

3. **UI Components:**
   - Audio waveform display
   - Transcription display
   - Error states

## Integration Testing

### Cross-Application Testing

```bash
# Run all application tests
npm run test:all

# Desktop + Web integration
pytest tests/integration/test_desktop_web_integration.py
```

### Device Integration Tests

```python
@pytest.mark.integration
@pytest.mark.device
def test_full_recording_workflow():
    """Test complete workflow from device to transcription"""
    # 1. Connect to device
    device = HiDockDevice()
    assert device.connect()

    # 2. List recordings
    recordings = device.list_recordings()
    assert len(recordings) > 0

    # 3. Download recording
    audio_data = device.download_recording(recordings[0])
    assert audio_data is not None

    # 4. Transcribe
    transcription = ai_service.transcribe(audio_data)
    assert transcription.text != ""
```

## CI/CD Testing

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: |
          cd hidock-desktop-app
          pip install -r requirements.txt
          pytest --cov=. --cov-report=xml

  test-web:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: |
          cd hidock-web-app
          npm ci
          npm run test:coverage
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Best Practices

### 1. Test Naming

- Be descriptive: `test_audio_player_handles_corrupt_file`
- Group related tests in classes
- Use consistent naming patterns

### 2. Test Data

```python
# Use fixtures for test data
@pytest.fixture
def sample_audio_file(tmp_path):
    file_path = tmp_path / "test.wav"
    # Create test file
    return file_path
```

### 3. Async Testing

```typescript
// Testing async operations
it('loads device data asynchronously', async () => {
  const promise = deviceService.loadDevices();

  // Assert loading state
  expect(deviceService.isLoading).toBe(true);

  const devices = await promise;

  // Assert loaded state
  expect(devices).toHaveLength(2);
  expect(deviceService.isLoading).toBe(false);
});
```

### 4. Error Testing

Always test error paths:

```python
def test_handles_device_disconnect():
    device = connect_device()
    device.disconnect()

    with pytest.raises(DeviceNotConnectedError):
        device.list_recordings()
```

### 5. Performance Testing

```python
@pytest.mark.performance
def test_large_file_processing(benchmark):
    large_file = create_large_audio_file(size_mb=100)

    result = benchmark(process_audio_file, large_file)

    assert result.duration < 5.0  # Should process in under 5 seconds
```

## Debugging Tests

### Python Debugging

```bash
# Run with pdb
pytest --pdb

# Run specific test with debugging
pytest -k test_name --pdb

# Add breakpoint in code
import pdb; pdb.set_trace()
```

### JavaScript Debugging

```typescript
// Add debugger statement
debugger;

// Run with Node debugging
node --inspect-brk ./node_modules/.bin/vitest
```

## Test Reports

### Coverage Reports

- **Python:** HTML reports in `htmlcov/`
- **JavaScript:** Coverage in `coverage/`

### CI Reports

- Test results posted as PR comments
- Coverage badges updated automatically
- Failed test logs available in Actions

## Troubleshooting Tests

### Common Issues

1. **Import errors:** Check PYTHONPATH and virtual environment
2. **Async timeouts:** Increase timeout for slow operations
3. **Mock conflicts:** Clear mocks between tests
4. **Flaky tests:** Use retry mechanisms for network/device tests

### Getting Help

- Check test output carefully
- Run single test in isolation
- Use verbose mode for more details
- Check CI logs for environment differences
