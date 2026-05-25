# Distributed TCP DNS Resolver

A concurrent client-server distributed application simulating a Domain Name System (DNS) resolver, built with Python Sockets and containerized using Docker.

## 📌 How It Works

This system simulates a distributed network environment where a client needs to find the IP address associated with a domain name.

* **Client Caching:** Before contacting the server, the client checks its local cache file. If the domain was queried before, it responds instantly from memory.
* **Primary Resolution:** If the domain is not cached, the client connects to the Primary Server. The server checks its own local database for the domain.
* **Recursive Forwarding:** If the Primary Server doesn't recognize the domain, it acts as a client itself. It forwards the request to a Secondary Server responsible for that zone, retrieves the IP, and sends it back.
* **Persistence:** Both positive hits (valid IPs) and negative hits (`NOT_FOUND`) are saved automatically in local text files to optimize future queries.

#### Queries the distributed DNS system for the given domain.

Example: `pc1.principal.ro` (Resolved by the primary server)

Example: `pc1.secundar.ro` (Resolved via forwarding to the secondary server)

## 💻 Available Commands
Once the client script is running, simply type the domain name you want to resolve directly into the terminal prompt (>):

```bash
<domain_name>
```

## Run Instructions

### 1. Start the Server (Docker/Podman)
Open your terminal in the project directory where the `Dockerfile` and `server.py` are located.

**Build the image:**
```bash
docker build -t dns-server .
```
*If using Podman, replace `docker` with `podman`*

**Run the container**
```bash
docker run -p 8719:8719 dns-server
```
*The primary server is now listening on port 8719.*

### 2. Start the Secondary Server
Open a second terminal window. This acts as the `secondary DNS zone` for forwarded requests.

**Run the  script**
```bash
python3 server.py 8799
```
*You will be prompted to enter a unique username to join the server.*

### 3. Start the Client
Open a third terminal window for the user interface.

**Run the client script**
```bash
python3 client.py
```
*You will be prompted to enter a domain name to resolve.*
