from flask import Flask, render_template, request, jsonify
import socket
import threading
from queue import Queue

app = Flask(__name__)

# --- SCANNER LOGIC ---
target_ip = ""
queue = Queue()
open_ports = []

def port_scan(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        s.connect((target_ip, port))
        open_ports.append(port)
        s.close()
    except:
        pass

def threader():
    while True:
        worker = queue.get()
        port_scan(worker)
        queue.task_done()

# --- WEB ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    global target_ip, open_ports

    open_ports = []  # reset list
    
    data = request.get_json()
    target_host = data['target']

    try:
        target_ip = socket.gethostbyname(target_host)
    except:
        return jsonify({"error": "Invalid Hostname or IP"})

    # launch threads
    for _ in range(50):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()

    # scan ports 1–500
    for port in range(1, 501):
        queue.put(port)

    queue.join()

    return jsonify({"ip": target_ip, "open_ports": sorted(open_ports)})

if __name__ == '__main__':
    app.run(debug=True)
