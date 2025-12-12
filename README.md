## 🚀 Live Deployment

**Backend API:**  
https://org-management-backend.onrender.com/

**Swagger API Documentation:**  
https://org-management-backend.onrender.com/docs

**GitHub Repository:**  
https://github.com/TEJPAL221/org-management-backend




# **Organization Management Backend (FastAPI · Multi-Tenant Architecture)**

This backend provides APIs for managing organizations in a **multi-tenant system** using FastAPI, MongoDB, and JWT authentication.
It supports creating, updating, and deleting organizations, where each organization receives its own isolated tenant collection for improved scalability and data security.

---

## **1. High-Level Architecture**

```mermaid
flowchart TD
A[Client / Admin User] --> B[FastAPI Backend Service]

B --> C[Master Database<br/>Admin Accounts + Org Metadata]

B --> D1[Tenant Collection: org_alpha]
B --> D2[org_beta]
B --> D3[org_gamma]

C --> |Org → Tenant Mapping| B
```

### **How It Works**

* The **Master DB** stores:

  * Admin credentials
  * Organization metadata
  * Mapping to tenant collections

* Each organization has a **separate MongoDB collection** for isolated storage.

* Backend dynamically routes DB operations based on the admin’s organization.

This structure is commonly used in SaaS platforms to provide data isolation and scalability.

---

## **2. Design Choices & Trade-Offs**

### **Why Collection-Per-Tenant Multi-Tenancy?**

This architecture provides strong isolation between organizations. Each tenant maintains its own collection such as:

```
org_google
org_amazon
org_tesla
```

**Benefits**

* Better performance isolation
* Easy deletion/archiving of a tenant
* Large tenants do not impact smaller ones
* Cleaner backups and restore operations

**Trade-Offs**

* Too many collections can create metadata overhead
* Schema migrations must be applied across multiple collections
* Backend logic becomes more dynamic and slightly more complex

This design balances scalability and simplicity, making it well-suited for applications managing multiple independent organizations.

---

## **3. Project Structure**

```
app/
 ├── api/v1/
 │   ├── admin_router.py
 │   └── org_router.py
 ├── core/
 │   ├── deps.py
 │   └── security.py
 ├── models/
 │   └── pydantic_models.py
 ├── repositories/
 │   ├── master_repo.py
 │   └── tenant_repo.py
 ├── services/
 │   ├── auth_service.py
 │   └── org_service.py
 ├── config.py
 ├── db.py
 └── main.py
```

Backend follows a clean **class-based architecture** (Service + Repository pattern).

---

## **4. Environment Variables**

Create a `.env` file:

```
MONGO_URI=<your MongoDB Atlas URI>
MONGO_DB=org_master
JWT_SECRET=<choose-a-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=60
```

Do not commit `.env` to Git.
Use `.env.example` for reference.

---

## **5. Running the Project Locally**

### Install Dependencies

```
pip install -r requirements.txt
```

### Start the Server

```
uvicorn app.main:app --reload
```

API docs available at:

```
http://localhost:8000/docs
```

### Run Using Docker (Optional)

```
docker build -t org-backend .
docker run -p 8000:8000 --env-file .env org-backend
```

### Docker Compose (Local MongoDB + Backend)

```
docker-compose up --build
```

---

## **6. Deployment Guide (Render)**

Render is a free hosting service ideal for FastAPI.

### **Step 1: Push the project to GitHub**

(You already completed this.)

### **Step 2: Create a MongoDB Atlas Cluster**

Copy the connection string:

```
mongodb+srv://username:password@cluster0.mongodb.net/
```

### **Step 3: Create Render Web Service**

* Connect your GitHub repo
* Select branch `main`
* Choose Free Plan

### **Build Command**

```
pip install -r requirements.txt
```

### **Start Command**

```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### **Environment Variables (Render Dashboard)**

```
MONGO_URI=<Atlas URI>
MONGO_DB=org_master
JWT_SECRET=<your-secret>
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=60
```


---

## **7. API Endpoints**

### **Admin**

| Method | Endpoint       | Description                             |
| ------ | -------------- | --------------------------------------- |
| POST   | `/admin/login` | Admin authentication and JWT generation |

### **Organization**

| Method | Endpoint      | Description             |
| ------ | ------------- | ----------------------- |
| POST   | `/org/create` | Create new organization |
| POST   | `/org/update` | Update organization     |
| POST   | `/org/delete` | Delete organization     |

All organization APIs require **Bearer Token** authorization.

---

## **8. Technology Stack**

* **FastAPI** (Python async backend)
* **Motor** (Async MongoDB driver)
* **Pydantic** (Data validation)
* **Uvicorn** (ASGI server)
* **JWT Authentication**
## 📸 Project Screenshots

### Architecture Diagram
![Architecture](assets/project-architecture.png)

### Swagger API Overview
![Swagger UI](assets/api.png)

### Create Organization Example
![Create Org](assets/deployment.png)


