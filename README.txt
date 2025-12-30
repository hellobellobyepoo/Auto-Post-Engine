========================================================================
             AUTO POST ENGINE (APE) - OFFICIAL MANUAL & SETUP
========================================================================

Welcome to Auto Post Engine (APE). This tool is designed to automate
the capture, processing, and uploading of video content to TikTok using 
Windows 11 Fluent Design principles.

------------------------------------------------------------------------
1. FIRST-TIME SETUP (CRITICAL)
------------------------------------------------------------------------
Before you can run the app, you MUST set up the Python environment and
install the required libraries.

   STEP A: Make sure Python is installed on your Windows machine.
   STEP B: Double-click 'install_deps.bat'.
   STEP C: Wait for the black window to finish (it installs 500MB+ data).
           When you see "[SUCCESS] Environment is ready!", you are set.
   STEP D: FFmpeg is required for merging high-quality video and audio. 
           The app now includes it automatically in the 'bin/' folder.

------------------------------------------------------------------------
2. HOW TO LAUNCH
------------------------------------------------------------------------
After the setup is complete:

   - Double-click 'run_app.bat'.
   - The app will launch in the background (no terminal window will stay 
     open on your taskbar).
   - Check your taskbar for the Palm Tree icon!

------------------------------------------------------------------------
3. USING THE APP (THE WORKFLOW)
------------------------------------------------------------------------
Follow these steps to start your first automation:

   A. CONTENT TAB (Left Side):
      - Hashtags: Type your tags (e.g., #viral #fyp).
      - Part Duration: Choose how long each segment should be (e.g., 60s).
      - Auto Crop: Keep this ON for TikTok (converts 16:9 to vertical).

   B. ACCOUNT TAB (Right Side):
      - Enter your TikTok Email and Password. 
      - NOTE: Your credentials are used for the Selenium browser login.
      - Click the "Eye" icon to verify your password typing.

   C. ACTIONS:
      - Paste a YouTube Video OR Channel Link into the URL field.
      - Click [START AUTOMATION].

------------------------------------------------------------------------
4. AUTOMATED UPLOADING (TIKTOK)
------------------------------------------------------------------------
When you click Start, APE will:
   1. Download the video from YouTube.
   2. Segment it into parts.
   3. Open an automated Chrome window.
   
   IMPORTANT: The first time you use it, you MAY need to solve a manual
   Captcha in the Chrome window if TikTok asks for one. Once you log in,
   APE will save your "Chrome Profile" and should not ask again.

------------------------------------------------------------------------
5. FILE MANAGEMENT
------------------------------------------------------------------------
   - All downloaded videos go to the 'downloads' folder.
   - All trimmed segments go to the 'processed' folder.
   - Use the [Refresh] button in the UI to see your local files.

------------------------------------------------------------------------
6. TROUBLESHOOTING
------------------------------------------------------------------------
   - App won't start? Run 'install_deps.bat' again to fix the environment.
   - Browser closing too fast? Check your internet connection or login
     credentials.
   - Icon not showing? Ensure 'icon.png' is in the main folder.

========================================================================
                THANK YOU FOR USING AUTO POST ENGINE 
========================================================================
