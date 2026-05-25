import socket
import threading
import json
import sys
import os

# luam portul din terminal daca il dam, altfel ramanem pe 8719 by default
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8719
HOST = '0.0.0.0' # accepta orice conexiune
DB_FILE = f'server_db_{PORT}.txt'

# aici setam serverul secundar cu care comunicam
FORWARDING = {
    "secundar.ro": ("sys.ase.ro", 8799)
}

# ne asigura ca nu pica serverul daca scriu 2 clienti in acelasi fisier deodata
lock = threading.RLock()

def load_db():
    db = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=')
                    db[k] = v
    return db

def save_db(db):
    with open(DB_FILE, 'w') as f:
        for k, v in db.items():
            f.write(f"{k}={v}\n")

def forward_request(name):
    # cautam daca domeniul cerut apartine de celalalt server
    for domeniu, addr in FORWARDING.items():
        if name.endswith(domeniu):
            try:
                # sunam serverul secundar sa il intrebam IP-ul
                fsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                fsock.connect(addr)
                fsock.sendall(json.dumps({"cmd": "resolve", "name": name}).encode('utf-8'))
                
                data = fsock.recv(1024).decode('utf-8')
                fsock.close()
                return json.loads(data).get("ip", "NOT_FOUND")
            except:
                return "NOT_FOUND" # pica aici daca celalalt server e oprit
    return "NOT_FOUND"

def handle_client(conn):
    try:
        data = conn.recv(1024).decode('utf-8')
        if not data: return
        
        req = json.loads(data)
        if req.get("cmd") == "resolve":
            name = req.get("name")
            
            with lock:
                db = load_db()
                # daca stim noi raspunsul din prima, il trimitem clientului
                if name in db:
                    resp = {"ip": db[name]}
                    conn.sendall(json.dumps(resp).encode('utf-8'))
                    return
            
            # daca nu il stim, cerem ajutorul serverului secundar
            ip_gasit = forward_request(name)
            
            with lock:
                db = load_db()
                db[name] = ip_gasit # invatam si noi ce a zis secundarul ca sa stim pe viitor
                save_db(db)
                
            resp = {"ip": ip_gasit}
            conn.sendall(json.dumps(resp).encode('utf-8'))
            
    except Exception:
        pass
    finally:
        conn.close()

def main():
    # generam baza de date automat cu cate 3 domenii direct din cod
    if not os.path.exists(DB_FILE):
        if PORT == 8719:
            save_db({
                "pc1.principal.ro": "192.168.1.10",
                "pc2.principal.ro": "192.168.1.11",
                "pc3.principal.ro": "192.168.1.12"
            })
        elif PORT == 8799:
            save_db({
                "pc1.secundar.ro": "10.0.0.5",
                "pc2.secundar.ro": "10.0.0.6",
                "pc3.secundar.ro": "10.0.0.7"
            })

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server pornit pe portul {PORT}")
    
    while True:
        try:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn,)).start() # bagam fiecare client pe un thread separat ca sa mearga in paralel
        except RuntimeError:
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
