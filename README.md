# Auto Post Engine

<div align="center">

![Auto Post Engine](https://img.shields.io/badge/Windows%2011-Native%20UI-0078D4?style=for-the-badge&logo=windows11&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt6-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Automated video content pipeline for TikTok with authentic Windows 11 WinUI 3 design**

</div>

---

## ✨ Features

- 🎨 **Native Windows 11 UI** - Authentic WinUI 3 design with Mica backdrop
- 🎬 **YouTube Integration** - Download videos directly from YouTube URLs
- ✂️ **Smart Segmentation** - Automatically split videos into TikTok-ready parts
- 📱 **9:16 Crop** - Intelligent vertical cropping for mobile platforms
- 🚀 **Batch Processing** - Queue multiple videos for automated processing
- 📤 **Auto Upload** - Seamless TikTok upload with Selenium automation
- ⏸️ **Pause/Resume** - Full control over the automation pipeline
- 💾 **Session Recovery** - Resume interrupted sessions automatically
- 📊 **History Tracking** - Complete log of all processed content

## 🖼️ Design

Auto Post Engine features a complete Windows 11 native experience:

- **Mica Backdrop** - System-integrated translucent background
- **Fluent Icons** - Segoe Fluent Icons throughout the interface
- **Smooth Animations** - 167ms cubic-bezier transitions matching Windows 11
- **WinUI 3 Controls** - Authentic toggle switches, buttons, and dropdowns
- **Navigation View** - Windows 11 Settings-style navigation with animated indicator
- **Dark Theme** - Full dark mode with proper contrast ratios

## 📋 Requirements

- **Windows 10/11** (Windows 11 recommended for Mica effect)
- **Python 3.10+**
- **FFmpeg** (included in `bin/` folder)
- **Chrome, Brave, or Edge** browser for TikTok automation

## 🚀 Installation

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/Auto-Post-Engine.git
   cd Auto-Post-Engine
   ```

2. **Install dependencies**
   ```bash
   # Option A: Run the installer script
   install_deps.bat
   
   # Option B: Manual installation
   pip install -r requirements.txt
   ```

3. **Launch the application**
   ```bash
   # Option A: Use the launcher
   run_app.bat
   
   # Option B: Direct launch
   python gui/app.py
   ```

### Dependencies

```
PySide6          # Qt6 GUI framework
win32mica        # Windows 11 Mica effect
darkdetect       # System theme detection
yt-dlp           # YouTube video downloader
moviepy          # Video processing
selenium         # Browser automation
webdriver-manager # Automatic WebDriver management
```

## 📖 Usage

### Basic Workflow

1. **Add URLs** - Paste YouTube video or channel URLs into the queue
2. **Configure Settings**
   - Set part duration (30-300 seconds)
   - Enable/disable 9:16 crop
   - Configure upload throttling
3. **Enter Credentials** - Add your TikTok login details
4. **Start Batch** - Click "Start Batch" to begin automation

### Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Part Duration | Length of each video segment | 60s |
| Job Gap | Delay between uploads | 0 min |
| Fit 9:16 | Crop videos for vertical format | On |
| 1.25x Speed | Speed up to evade copyright | Off |
| Auto-Delete | Remove source files after upload | Off |

### First-Time TikTok Login

On first use, you may need to:
1. Complete a CAPTCHA in the automated browser window
2. Verify your login via email/SMS if prompted
3. The session will be saved for future use

## 📁 Project Structure

```
Auto-Post-Engine/
├── gui/
│   ├── app.py           # Main application (WinUI 3 UI)
│   ├── win_logo.png     # Application icon
│   └── assets/          # UI assets
├── modules/
│   ├── downloader.py    # YouTube download logic
│   ├── processor.py     # Video processing/segmentation
│   ├── uploader.py      # TikTok upload automation
│   ├── database.py      # History management
│   └── state_manager.py # Session state handling
├── bin/
│   ├── ffmpeg.exe       # FFmpeg binary
│   ├── ffplay.exe       # FFplay binary
│   └── ffprobe.exe      # FFprobe binary
├── logs/                # Session logs
├── downloads/           # Downloaded videos
├── processed/           # Processed segments
├── config.json          # User configuration
├── history.db           # SQLite history database
├── requirements.txt     # Python dependencies
├── install_deps.bat     # Dependency installer
└── run_app.bat          # Application launcher
```

## 🎨 UI Components

The application uses custom Windows 11 WinUI 3 components:

- `Win11Toggle` - Animated toggle switch with proper thumb scaling
- `Win11Button` - Standard and accent buttons with press animations
- `Win11ComboBox` - Dropdown with flyout menu
- `Win11NavButton` - Navigation view items
- `Win11NavIndicator` - Animated selection indicator
- `Win11Card` - Content cards with proper styling
- `Win11SettingsRow` - Settings-style label/control rows
- `Win11HeroCard` - Featured content card
- `Win11PasswordInput` - Password field with reveal button

## ⚙️ Configuration

Settings are automatically saved to `config.json`:

```json
{
    "title": "",
    "tags": "#fyp #viral",
    "dur": "60",
    "crop": true,
    "speed": false,
    "user": "your@email.com",
    "pwd": "********",
    "upload": true,
    "autodel": false,
    "throttle": "0"
}
```

## 🔧 Troubleshooting

### Application won't start
- Run `install_deps.bat` to reinstall dependencies
- Ensure Python 3.10+ is installed and in PATH

### Mica effect not working
- Requires Windows 11 Build 22000+
- Falls back to solid background on older systems

### Browser automation fails
- Ensure Chrome/Brave/Edge is installed
- Check that WebDriver is compatible with browser version
- Try clearing the browser profile folders

### Video processing errors
- Verify FFmpeg binaries are in `bin/` folder
- Check available disk space
- Review logs in `logs/` folder

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This tool is for educational purposes only. Users are responsible for ensuring their use complies with:
- YouTube's Terms of Service
- TikTok's Terms of Service
- Applicable copyright laws

---

<div align="center">

**Made with ❤️ for Windows 11**

</div>
