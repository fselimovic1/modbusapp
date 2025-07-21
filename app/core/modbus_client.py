from pymodbus.exceptions import ModbusIOException
from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
ZERO_ADDRESS = 0;
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def try_modbus_operations(client, unit_id):
    for func in ['read_coils', 'read_discrete_inputs', 'read_holding_registers', 'read_input_registers']:
        try:
            method = getattr(client, func)
            response = method(ZERO_ADDRESS, count=1, unit=unit_id)
            print(response)
            if response.encode():
                return True, "Success!";
        except Exception:
            continue
    return False, "No valid Modbus response received"

def test_modbus_connection(mode, host=None, port=502, serial_port=None, baudrate=9600, unit_id=1,
                           parity="N", stopbits=1, bytesize=8):
    try:
        if mode == "tcp":
            client = ModbusTcpClient(host=host, port=port)
        elif mode == "rtu":
            client = ModbusSerialClient(
                method="rtu",
                port=serial_port,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=0.1
            )
        if not client.connect():
            return False, "Connection error!"
        ok, msg = try_modbus_operations(client, unit_id=unit_id)
        return ok, msg

    except Exception as e:
        return False, f"Exception occurred: {str(e)}"
    finally:
        if client:
            client.close()


def read_modbus_data(host, port, address, count, function):
    client = ModbusTcpClient(host, port)
    if not client.connect():
        return {"error": f"Could not connect to {host}:{port}"}
    try:
        if function == "coils":
            response = client.read_coils(address, count, unit=1)
        elif function == "discrete_inputs":
            response = client.read_discrete_inputs(address, count, unit=1)
        elif function == "input_registers":
            response = client.read_input_registers(address, count, unit=1)
        elif function == "holding_registers":
            response = client.read_holding_registers(address, count, unit=1)
        else:
            return {"error": "Invalid function"}
        if response.isError():
            return {"error": str(response)}
        return {"values": response.bits if hasattr(response, 'bits') else response.registers}
    except ModbusIOException as e:
        return {"error": str(e)}
    finally:
        client.close()
