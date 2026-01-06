import SimpleHTTPServer
import SocketServer

PORT = 8000

# This handler tells the server to serve files from the current directory
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

# Create the server instance
httpd = SocketServer.TCPServer(("", PORT), Handler)

print("Serving at port", PORT)
print("Press Ctrl+C to stop the server")

# Start the server and keep it running
httpd.serve_forever()