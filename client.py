import socket
import json
import os

HOST = '127.0.0.1' #localhost
PORT = 8719
CACHE_FILE = 'client_cache.txt'

def load_cache():
    cache = {}
    # incarcam istoricul daca fisierul exista deja
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            for line in f:
                if '=' in line:
                    k, v = line.strip().split('=')
                    cache[k] = v
    return cache

def save_cache(cache):
    # salvam in fisier ca sa ramana rezultatele si dupa ce inchidem programul
    with open(CACHE_FILE, 'w') as f:
        for k, v in cache.items():
            f.write(f"{k}={v}\n")

def main():
    cache = load_cache()
    
    while True:
        try:
            nume = input("> Introdu numele de rezolvat: ").strip()
            if not nume:
                continue
            
            # verificam mai intai daca il avem gata salvat local
            if nume in cache:
                print(f"[CACHE LOCAL] {nume} -> {cache[nume]}")
                continue
                
            # daca nu, deschidem conexiunea cu serverul ca sa intrebam
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((HOST, PORT))
                
                req = {"cmd": "resolve", "name": nume}
                sock.sendall(json.dumps(req).encode('utf-8'))
                
                data = sock.recv(1024).decode('utf-8')
                resp = json.loads(data)
                
                # luam IP-ul primit sau punem mesajul asta daca nu exista
                ip_rezolvat = resp.get("ip", "NOT_FOUND")
                
                # salvam in cache ca sa stim data viitoare
                cache[nume] = ip_rezolvat
                save_cache(cache)
                
                print(f"[SERVER] {nume} -> {ip_rezolvat}")
                sock.close()
            except Exception:
                print("Eroare: serverul nu e pornit.")
                
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()