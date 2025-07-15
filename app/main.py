from pathlib import Path
from fastapi import FastAPI
from fastapi import Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from app.core.modbus_client import read_modbus_data, test_modbus_connection
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = FastAPI()
templates = Jinja2Templates(Path(__file__).resolve().parent/ "ui" / "templates")
app.mount("/static", StaticFiles(directory=Path(__file__).resolve().parent / "ui" / "static"), name="static")


@app.get("/test_connection")
def test_connection(
    mode: str = Query(...),
    host: str = None,
    port: int = 502,
    serial_port: str = None,
    baudrate: int = 9600,
    parity: str = "N",
    stopbits: int = 1,
    bytesize: int = 8,
    unit_id: int = 1
):
    success = test_modbus_connection(
    mode, host, port, serial_port, baudrate, unit_id=unit_id,
    parity=parity, stopbits=stopbits, bytesize=bytesize
)
    return {
        "success": success,
        "mode": mode,
        "host": host,
        "serial_port": serial_port,
        "unit_id": unit_id
    }

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/connection_tester", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("connection_tester.html", {"request": request})


@app.get("/read")
def read_registers(
    host: str = "192.168.200.5",
    port: int = 502,
    address: int = 0,
    count: int = 2,
    function: str = "holding_registers"
):
    return read_modbus_data(host, port, address, count, function)

# @app.get("/dashboard", response_class=HTMLResponse)
# def dashboard():
#     return """
#     <html>
#     <head>
#         <title>Live Modbus Dashboard</title>
#         <script>
#             async function fetchData() {
#                 const host = document.getElementById("host").value;
#                 const port = document.getElementById("port").value;
#                 const address = document.getElementById("address").value;
#                 const count = document.getElementById("count").value;
#                 const func = document.getElementById("function").value;

#                 const res = await fetch(`/read?host=${host}&port=${port}&address=${address}&count=${count}&function=${func}`);
#                 const data = await res.json();

#                 const output = document.getElementById("output");
#                 if (data.values) {
#                     output.innerHTML = data.values.map((val, idx) =>
#                         `Address ${parseInt(address)+idx}: ${val}`
#                     ).join("<br>");
#                 } else {
#                     output.innerHTML = `<span style='color:red;'>${data.error}</span>`;
#                 }
#             }
#             setInterval(fetchData, 2000);
#         </script>
#     </head>
#     <body>
#         <h2>Live Modbus Dashboard</h2>
#         <label>Host: <input id="host" value="192.168.200.5"></label><br/>
#         <label>Port: <input id="port" value="502"></label><br/>
#         <label>Function:
#             <select id="function">
#                 <option value="coils">Coils (0x01)</option>
#                 <option value="discrete_inputs">Discrete Inputs (0x02)</option>
#                 <option value="holding_registers">Holding Registers (0x03)</option>
#                 <option value="input_registers">Input Registers (0x04)</option>
#             </select>
#         </label><br/><br/>
#         <label>Address: <input id="address" value="0"></label><br/>
#         <label>Count: <input id="count" value="4"></label><br/>
#         <div>
#             <strong>Live Values:</strong><br/>
#             <div id="output" style="font-family: monospace; padding-top: 10px;"></div>
#         </div>
#     </body>
#     </html>
#     """
