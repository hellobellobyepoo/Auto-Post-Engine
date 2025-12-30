"""
TikTok Uploader - Uses Native Selenium 4.x Manager
Bypasses webdriver_manager to avoid network/compatibility issues
"""

import time
import os
import winreg  # Windows Registry access

# Try selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.edge.service import Service as EdgeService
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class TikTokUploader:
    def __init__(self):
        self.driver = None
        self.is_logged_in = False
        self.username = None
        self.password = None
        self.cancelled = False
        # "auto", "chrome", "edge", "brave"
        self.browser_type = "auto" 

    def cancel(self):
        self.cancelled = True

    def set_credentials(self, username, password):
        self.username = username
        self.password = password
        
    def set_browser_preference(self, browser_type):
        """Allow app to set restored preference"""
        if browser_type in ["chrome", "edge", "brave"]:
            self.browser_type = browser_type

    def _get_default_browser_windows(self):
        """Detect default browser execution path via Registry"""
        try:
            key_path = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                prog_id, _ = winreg.QueryValueEx(key, "ProgId")
            
            if "Chrome" in prog_id: return "chrome"
            if "MSEdge" in prog_id: return "edge"
            if "Brave" in prog_id: return "brave"
            return None
        except:
            return None

    def _find_binary(self, name):
        """Find executable path for specific browser"""
        paths = []
        if name == "chrome":
            paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ]
        elif name == "edge":
            paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
        elif name == "brave":
            paths = [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")
            ]
            
        for p in paths:
            if os.path.exists(p):
                return p
        return None

    def start_browser(self, progress_callback=None):
        """Start Chrome, Edge, or Brave using Native Selenium Manager"""
        if not SELENIUM_AVAILABLE:
            if progress_callback: progress_callback(0, "Selenium not installed")
            return False
            
        if self.driver:
            return True
        
        # Helper to launch specific browser
        def try_launch(b_type):
            try:
                binary = self._find_binary(b_type)
                msg = f"Launching {b_type.title()}..."
                if binary: msg += " (Native Mode)"
                if progress_callback: progress_callback(None, msg)

                # Configure Options
                driver = None
                
                if b_type == "chrome":
                    opts = webdriver.ChromeOptions()
                    if binary: opts.binary_location = binary
                    opts.add_argument("--start-maximized")
                    opts.add_argument("--disable-notifications")
                    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
                    
                    # Native Launch (Selenium 4.6+ handles driver automatically)
                    driver = webdriver.Chrome(options=opts)
                
                elif b_type == "brave":
                    # Brave uses Chrome Driver
                    if not binary:
                        # Cannot launch brave without binary path
                        binary = self._find_binary("brave")
                    
                    if not binary: return None
                        
                    opts = webdriver.ChromeOptions()
                    opts.binary_location = binary
                    opts.add_argument("--start-maximized")
                    opts.add_argument("--disable-notifications")
                    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
                    
                    # Native Launch for Brave
                    driver = webdriver.Chrome(options=opts)
                    
                elif b_type == "edge":
                    opts = webdriver.EdgeOptions()
                    if binary: opts.binary_location = binary
                    opts.add_argument("--start-maximized")
                    opts.add_argument("--disable-notifications")
                    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
                    
                    # Native Launch for Edge
                    driver = webdriver.Edge(options=opts)
                
                if driver:
                    # Anti-detect script
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    return driver
                return None
                
            except Exception as e:
                # Truncate error for cleaner logs
                err = str(e).split('\n')[0][:100]
                if progress_callback: progress_callback(None, f"Start {b_type} failed: {err}")
                return None

        # LOGIC:
        # 1. Determine priority list
        candidates = []
        
        # A. Explicit Preference
        if self.browser_type in ["chrome", "edge", "brave"]:
            candidates.append(self.browser_type)
            
        # B. Auto-Detect Default Browser
        default = self._get_default_browser_windows()
        if default and default not in candidates:
            candidates.append(default)
        
        # C. Fallbacks
        for b in ["chrome", "brave", "edge"]:
            if b not in candidates:
                candidates.append(b)

        # Launch Loop
        success_driver = None
        for browser in candidates:
            # Skip if binary missing (except for chrome which might happen via system path)
            if browser != "chrome" and not self._find_binary(browser):
                continue
                
            success_driver = try_launch(browser)
            if success_driver:
                self.browser_type = browser
                break
        
        if success_driver:
            self.driver = success_driver
            if progress_callback: progress_callback(None, f"Browser Ready ({self.browser_type.title()})")
            return True
        else:
            if progress_callback:
                progress_callback(0, "Could not launch any browser. Please ensure Chrome, Edge or Brave is installed.")
            return False

    def check_login_status(self):
        """Check if already logged in by going to upload page"""
        try:
            self.driver.get("https://www.tiktok.com/upload")
            time.sleep(3)
            
            if "/login" not in self.driver.current_url:
                self.is_logged_in = True
                return True
            return False
        except:
            return False

    def login(self, progress_callback=None):
        """Login to TikTok"""
        if not self.username or not self.password:
            if progress_callback:
                progress_callback(0, "No credentials provided")
            return False
        
        def report(pct, msg):
            if progress_callback:
                progress_callback(pct, msg)
        
        try:
            report(10, "Checking session...")
            # 1. First, check status via upload page as requested
            self.driver.get("https://www.tiktok.com/upload")
            time.sleep(3)
            
            # Check if already logged in (redirected to /upload or stays there)
            if "/login" not in self.driver.current_url:
                 self.is_logged_in = True
                 report(100, "Already logged in!")
                 return True

            # 2. If not logged in, go to SPECIFIC login page
            report(20, "Not logged in. Going to email login...")
            self.driver.get("https://www.tiktok.com/login/phone-or-email/email")
            time.sleep(4)
            
            # 3. Force check: If weird redirect, force back
            if "login/phone-or-email/email" not in self.driver.current_url:
                 self.driver.get("https://www.tiktok.com/login/phone-or-email/email")
                 time.sleep(3)
            
            report(30, "Entering credentials...")
            
            # Find username field
            try:
                username_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        "input[name='username'], input[placeholder*='Email'], input[placeholder*='email'], input[placeholder*='Phone']"))
                )
                username_input.clear()
                for char in self.username:
                    username_input.send_keys(char)
                    time.sleep(0.05)
            except Exception as e:
                report(0, f"Username field error: {e}")
                return False
            
            time.sleep(1)
            
            # Find password field
            try:
                password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                password_input.clear()
                # Fast typing for password
                password_input.send_keys(self.password)
            except Exception as e:
                report(0, f"Password field error: {e}")
                return False
            
            report(50, "Submitting login...")
            time.sleep(1)
            
            # Click login button
            try:
                login_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    "button[type='submit'], button[data-e2e='login-button']")
                clicked = False
                for btn in login_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        clicked = True
                        break
                if not clicked:
                     password_input.send_keys(Keys.RETURN)
            except:
                password_input.send_keys(Keys.RETURN)
            
            time.sleep(5)
            report(70, "Checking login result...")
            
            # Check for CAPTCHA
            page_source = self.driver.page_source.lower()
            if "captcha" in page_source or "verify" in self.driver.current_url:
                report(75, "CAPTCHA detected! Solve it manually (30s)...")
                time.sleep(30)
            
            # Verify login
            if self.check_login_status():
                report(100, "Login successful!")
                self.is_logged_in = True
                return True
            else:
                report(0, "Login failed - check credentials or captcha")
                return False
                
        except Exception as e:
            report(0, f"Login error: {e}")
            return False

    def upload_video(self, file_path, caption, hashtags="", progress_callback=None):
        """Upload video to TikTok"""
        if self.cancelled:
            return False
            
        def report(pct, msg):
            if progress_callback:
                progress_callback(pct, msg)
        
        if not self.driver:
            if not self.start_browser(progress_callback):
                return False
        
        # Check/do login
        if not self.is_logged_in:
            report(5, "Checking login status...")
            if self.check_login_status():
                report(10, "Already logged in")
            elif self.username and self.password:
                if not self.login(progress_callback):
                    return False
            else:
                report(0, "Not logged in and no credentials")
                return False
        
        abs_path = os.path.abspath(file_path)
        if not os.path.exists(abs_path):
            report(0, f"File not found: {file_path}")
            return False
        
        try:
            report(20, "Opening upload page...")
            self.driver.get("https://www.tiktok.com/upload")
            time.sleep(4)
            
            # Find file input element
            report(30, "Finding upload input...")
            file_input = None
            
            # Try direct input
            inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            for inp in inputs:
                if inp.is_enabled():
                    file_input = inp
                    break
            
            # Try iframe
            if not file_input:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    try:
                        self.driver.switch_to.frame(iframe)
                        inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                        for inp in inputs:
                            if inp.is_enabled():
                                file_input = inp
                                break
                        if file_input:
                            break
                        self.driver.switch_to.default_content()
                    except:
                        self.driver.switch_to.default_content()
            
            if not file_input:
                report(0, "Could not find file input")
                return False
            
            report(40, "Uploading video file...")
            file_input.send_keys(abs_path)
            
            report(50, "Waiting for processing...")
            time.sleep(15)
            
            self.driver.switch_to.default_content()
            
            # Find caption/description editor
            report(60, "Setting caption...")
            caption_set = False
            
            caption_selectors = [
                "div[contenteditable='true'][data-text='true']",
                "div.public-DraftEditor-content",
                "div[contenteditable='true']",
                "div[data-placeholder]",
                "[class*='DraftEditor']",
            ]
            
            for selector in caption_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed():
                            elem.click()
                            time.sleep(0.3)
                            # Clear existing text
                            elem.send_keys(Keys.CONTROL + "a")
                            elem.send_keys(Keys.DELETE)
                            
                            # Simple clean caption
                            full_caption = f"{caption} {hashtags}".strip()
                            elem.send_keys(full_caption)
                            caption_set = True
                            report(70, f"Caption: {full_caption[:40]}...")
                            break
                    if caption_set:
                        break
                except:
                    continue
            
            if not caption_set:
                report(65, "Caption field issue, check manually...")
            
            time.sleep(2)
            
            # Find and click Post button
            report(80, "Looking for Post button...")
            
            post_clicked = False
            
            # Method 1: Text search
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                try:
                    text = btn.text.strip().lower()
                    if text == "post":
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                        time.sleep(0.5)
                        btn.click()
                        post_clicked = True
                        report(90, "Post button clicked (Text Match)!")
                        break
                except:
                    continue
            
            # Method 2: Data attribute
            if not post_clicked:
                try:
                    post_btn = self.driver.find_element(By.CSS_SELECTOR, "[data-e2e='post-button']")
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", post_btn)
                    post_btn.click()
                    post_clicked = True
                    report(90, "Post button clicked (Attribute Match)!")
                except:
                    pass
            
            if not post_clicked:
                report(85, "WARNING: Auto-click failed. Please click POST manually.")
                time.sleep(15)
            else:
                time.sleep(8)
            
            report(100, "Upload cycle complete!")
            return True
            
        except Exception as e:
            report(0, f"Upload error: {e}")
            return False

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
