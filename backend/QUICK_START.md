# 🚀 Quick Start Guide - Backend Server

## Problem: "No module named 'fastapi'" or "No module named 'uvicorn'"

This happens when you're using the system Python instead of the virtual environment Python.

## ✅ Solution: Use Virtual Environment

### **Method 1: Activate Virtual Environment First (Recommended)**

```powershell
# Navigate to backend
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Now run the server
python -m uvicorn main:app --reload
```

### **Method 2: Use Virtual Environment Python Directly**

```powershell
# Navigate to backend
cd backend

# Run using venv Python directly
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

### **Method 3: Use main.py (if configured)**

```powershell
# Navigate to backend
cd backend

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run main.py
python main.py
```

---

## 🔍 How to Check if Virtual Environment is Active

When the virtual environment is active, you'll see `(venv)` at the start of your PowerShell prompt:

```powershell
(venv) PS D:\...\backend>
```

If you don't see `(venv)`, the virtual environment is not active.

---

## 📝 Complete Setup (First Time Only)

If dependencies are not installed:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🎯 Quick Commands Reference

| Task | Command |
|------|---------|
| Activate venv | `.\venv\Scripts\Activate.ps1` |
| Install deps | `pip install -r requirements.txt` |
| Start server | `python -m uvicorn main:app --reload` |
| Start server (direct) | `.\venv\Scripts\python.exe -m uvicorn main:app --reload` |

---

## ⚠️ Common Issues

### Issue 1: "Execution Policy" Error
If you get an execution policy error when activating:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: "Module not found" even after activation
Make sure you're in the `backend` directory and the venv is activated. Check with:

```powershell
python --version
where python
```

This should show the venv Python path.

---

## ✅ Server Running Successfully

When the server starts successfully, you'll see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

The API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

---

## 🧪 Test the Server

Open your browser and go to:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health (if available)

---

**Note**: The server is currently running in the background. To stop it, press `Ctrl+C` in the terminal where it's running.

