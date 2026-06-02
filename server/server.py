from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# ============================================================
# EMOTION RESPONSIVE SMART HOME - MIDDLEWARE SERVER
# ============================================================
# This server acts as a bridge between:
# - AI Assistant (Python) sends device control commands
# - ESP8266/ESP32 (polls for state changes)
#
# Device states are stored in memory and served to ESP32
# ============================================================

PORT = 8000

# Store all device states
device_states = {
    "led": {"device": "led", "action": "off"},
    "rgb": {"device": "rgb", "r": 0, "g": 0, "b": 0},
    "fan": {"device": "fan", "speed": 0}
}


class SimpleHandler(BaseHTTPRequestHandler):
    """HTTP request handler for device control."""

    def _set_headers(self, code=200):
        """Set standard HTTP response headers."""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_POST(self):
        """Receive device control JSON commands from Python AI."""
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data)
            device = data.get("device")

            if device in device_states:
                # Update stored state
                device_states[device].update(data)
                print(f"[UPDATE] {device}: {device_states[device]}")
                response = {"status": "success", "updated": device_states[device]}
                self._set_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "status": "error",
                    "message": f"Unknown device '{device}'"
                }).encode())

        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"status": "error", "message": "Invalid JSON"}).encode())

    def do_GET(self):
        """ESP32 polls this endpoint to get latest device states."""
        if self.path == "/get_command":
            # Return all device states
            self._set_headers()
            self.wfile.write(json.dumps(device_states).encode())
        elif self.path == "/ping":
            # Health check
            self._set_headers()
            self.wfile.write(json.dumps({"status": "alive"}).encode())
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        """Override logging to be more concise."""
        print(f"[{self.address_string()}] {format % args}")


def run_server():
    """Start the HTTP middleware server."""
    print(f"📡 Emotion Smart Home Server running on port {PORT}...")
    print(f"\nEndpoints:")
    print(f"  POST / - Receive device commands from AI")
    print(f"  GET /get_command - ESP32 polls for device states")
    print(f"  GET /ping - Health check\n")
    
    server = HTTPServer(("0.0.0.0", PORT), SimpleHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
