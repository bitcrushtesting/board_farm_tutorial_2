import pytest
import asyncio
from bleak import BleakClient, BleakScanner

# UUIDs for the Heart Rate Service and Heart Rate Measurement Characteristic
HEART_RATE_SERVICE_UUID = "0000180d-0000-1000-8000-00805f9b34fb"
HEART_RATE_MEASUREMENT_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

@pytest.fixture(scope="module")
def event_loop():
    return asyncio.get_event_loop()

@pytest.fixture(scope="module")
async def heart_rate_monitor_address():
    devices = await BleakScanner.discover()
    for device in devices:
        if "Heart Rate" in device.name:
            return device.address
    pytest.fail("Heart Rate Monitor not found")

@pytest.fixture(scope="module")
async def heart_rate_client(heart_rate_monitor_address):
    client = BleakClient(heart_rate_monitor_address)
    try:
        await client.connect()
        yield client
    finally:
        await client.disconnect()

@pytest.mark.asyncio
async def test_heart_rate_service(heart_rate_client):
    services = await heart_rate_client.get_services()
    heart_rate_service = services.get_service(HEART_RATE_SERVICE_UUID)
    assert heart_rate_service is not None, "Heart Rate Service not found"

@pytest.mark.asyncio
async def test_heart_rate_measurement(heart_rate_client):
    def heart_rate_handler(sender, data):
        heart_rate = data[1]
        print(f"Heart Rate: {heart_rate}")
        assert 30 <= heart_rate <= 220, "Heart Rate out of expected range"

    await heart_rate_client.start_notify(HEART_RATE_MEASUREMENT_UUID, heart_rate_handler)
    await asyncio.sleep(10)
    await heart_rate_client.stop_notify(HEART_RATE_MEASUREMENT_UUID)
