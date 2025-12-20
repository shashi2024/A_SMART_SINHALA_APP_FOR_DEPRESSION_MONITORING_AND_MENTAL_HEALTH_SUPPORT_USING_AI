# 🌐 Run Flutter App in Google Chrome

## ✅ Quick Start

### Option 1: Run Directly in Chrome (Recommended)

```powershell
cd frontend
flutter run -d chrome
```

This will:
- ✅ Build the web app
- ✅ Launch Chrome automatically
- ✅ Open your app at `http://localhost:xxxxx`
- ✅ Enable hot reload (save files to see changes instantly)

---

### Option 2: Run with Specific Port

```powershell
cd frontend
flutter run -d chrome --web-port=8080
```

Opens at: `http://localhost:8080`

---

### Option 3: Run in Release Mode (Optimized)

```powershell
cd frontend
flutter run -d chrome --release
```

Faster performance, but no hot reload.

---

## 🚀 Step-by-Step

### 1. Navigate to Frontend Folder

```powershell
cd frontend
```

### 2. Get Dependencies (First Time)

```powershell
flutter pub get
```

### 3. Run in Chrome

```powershell
flutter run -d chrome
```

### 4. Wait for Build

You'll see:
```
Building flutter tool...
Running "flutter pub get" in frontend...
Launching lib/main.dart on Chrome in debug mode...
```

### 5. Chrome Opens Automatically

Your app will open in Chrome at `http://localhost:xxxxx`

---

## 🔧 Troubleshooting

### Error: "No devices found"

**Solution:**
```powershell
flutter devices
```

Should show:
```
Chrome (chrome) • chrome • web-javascript • Google Chrome
```

If not, enable web:
```powershell
flutter config --enable-web
```

### Error: "Chrome not found"

**Solution:**
1. Install Google Chrome
2. Or specify Chrome path:
```powershell
flutter run -d chrome --chrome-binary="C:\Program Files\Google\Chrome\Application\chrome.exe"
```

### Error: "Port already in use"

**Solution:**
```powershell
# Use different port
flutter run -d chrome --web-port=8081
```

### Error: "Firebase not initialized"

**Solution:**
Make sure:
1. `firebase_options.dart` exists
2. Firebase is initialized in `main.dart`
3. Backend server is running (for API calls)

---

## 📋 Useful Commands

### List Available Devices
```powershell
flutter devices
```

### Run with Hot Reload (Default)
```powershell
flutter run -d chrome
```
Press `r` to hot reload, `R` to hot restart

### Run in Release Mode
```powershell
flutter run -d chrome --release
```

### Build Web App (Without Running)
```powershell
flutter build web
```
Output: `build/web/` folder

### Serve Built Web App
```powershell
# After building
cd build/web
# Use any web server, e.g.:
python -m http.server 8080
```

---

## 🎯 Development Tips

### Hot Reload
- Press `r` in terminal to hot reload
- Press `R` to hot restart
- Press `q` to quit

### Debug Console
- Open Chrome DevTools (F12)
- See console logs
- Debug Flutter web code

### Network Tab
- Check API calls to backend
- Verify Firebase connections
- Monitor requests

---

## 🔗 URLs

### App URL
- Default: `http://localhost:xxxxx` (random port)
- Custom: `http://localhost:8080` (if using `--web-port=8080`)

### Backend API
- Make sure backend is running: `http://localhost:8000`
- Update `api_service.dart` if backend URL is different

---

## ✅ Checklist

Before running:
- [ ] Flutter installed and working
- [ ] Chrome installed
- [ ] `flutter pub get` completed
- [ ] Firebase configured (`firebase_options.dart` exists)
- [ ] Backend server running (for API calls)

---

## 🎉 Quick Command

```powershell
cd frontend
flutter pub get
flutter run -d chrome
```

That's it! Your app will open in Chrome! 🚀


