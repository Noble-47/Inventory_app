# 📦 Inventory Service

The **Inventory Service** is a core component of the **Inventra** system, responsible for managing product inventory. It provides real-time visibility of available stock, enables stock level updates, and serves as the central system for tracking product availability within the application.

---

## ✨ Features

- **Add Products to Inventory**  
  Register new items with relevant details like SKU, name, description, quantity, and price.

- **Update Stock Levels**  
  Modify stock quantities during sales, restocking, or corrections.

- **Fetch Inventory Details**  
  Retrieve all or specific product information including current stock levels.

- **Low Stock Detection**  
  Support for identifying and flagging items that fall below a minimum threshold.

- **Integration-Ready**  

---

## 📁 Directory Structure

---

## API

---

## 🛠 API Endpoints

| Method | Endpoint           | Description                     |
|--------|--------------------|---------------------------------|
| GET    | `/inventory/`      | Get all inventory items         |
| GET    | `/inventory/{id}`  | Get item details by ID          |
| POST   | `/inventory/`      | Add a new item to inventory     |
| PUT    | `/inventory/{id}`  | Update an existing inventory item |
| DELETE | `/inventory/{id}`  | Remove an item from inventory   |

> Note: All endpoints are secured and require authentication.

---

## 📨 Events Published

---

## 🧪 Testing

Run unit and integration tests using:

```bash
pytest tests/
```
---

