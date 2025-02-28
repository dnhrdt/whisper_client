"""
Windows SendMessage API Test Script
Version: 1.1
Timestamp: 2025-02-28 18:16 CET
"""
import sys
import time
import win32gui
import win32con
import win32api
from pathlib import Path
import statistics

# Add project directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.text import TextManager, send_message
from src import logging
import config

# Configure logger for tests
logger = logging.get_logger()
config.LOG_LEVEL_CONSOLE = "DEBUG"

def get_vscode_window():
    """Find VS Code window handle"""
    result = []
    
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Visual Studio Code" in title:
                windows.append((hwnd, title))
        return True
    
    win32gui.EnumWindows(callback, result)
    
    if result:
        print(f"Found {len(result)} VS Code windows:")
        for i, (hwnd, title) in enumerate(result):
            print(f"  {i+1}. Handle: {hwnd}, Title: {title}")
        return result[0][0]  # Return the first VS Code window handle
    else:
        print("❌ No VS Code windows found")
        return None

def get_edit_control(parent_hwnd):
    """Find the edit control within VS Code"""
    result = []
    
    # VS Code uses a complex structure with Electron/Chromium
    # We need to search more deeply for potential edit areas
    def callback(hwnd, controls):
        class_name = win32gui.GetClassName(hwnd)
        # Log all controls for debugging
        text = win32gui.GetWindowText(hwnd)
        if text or class_name not in ["", "Static"]:
            print(f"Control: {hwnd}, Class: {class_name}, Text: {text[:20] + '...' if len(text) > 20 else text}")
        
        # Look for potential edit controls
        if class_name in ["Edit", "RichEdit", "RichEdit20W", "RICHEDIT50W"]:
            controls.append((hwnd, class_name, "standard_edit"))
        # VS Code's main editor might be in Chromium's structure
        elif class_name == "Chrome_RenderWidgetHostHWND":
            controls.append((hwnd, class_name, "chrome_render"))
        # Electron apps often use Atom as a base
        elif "Atom" in class_name:
            controls.append((hwnd, class_name, "atom"))
        # Look for the Monaco editor component
        elif "Monaco" in text or "monaco" in text.lower():
            controls.append((hwnd, class_name, "monaco"))
        return True
    
    # First try direct children
    win32gui.EnumChildWindows(parent_hwnd, callback, result)
    
    if not result:
        # If no results, try a recursive approach to find deeper controls
        def recursive_find(hwnd, depth=0, max_depth=5):
            if depth > max_depth:
                return
            
            try:
                win32gui.EnumChildWindows(hwnd, lambda child_hwnd, _: (
                    callback(child_hwnd, result),
                    recursive_find(child_hwnd, depth + 1, max_depth)
                ), None)
            except Exception:
                pass  # Some windows might not allow enumeration
        
        print("No direct edit controls found, searching recursively...")
        recursive_find(parent_hwnd)
    
    if result:
        print(f"Found {len(result)} potential edit controls:")
        for i, (hwnd, class_name, control_type) in enumerate(result):
            print(f"  {i+1}. Handle: {hwnd}, Class: {class_name}, Type: {control_type}")
        
        # Prioritize standard edit controls if found
        for hwnd, _, control_type in result:
            if control_type == "standard_edit":
                return hwnd
        
        # Otherwise return the first control found
        return result[0][0]
    else:
        print("❌ No potential edit controls found")
        # For testing purposes, we'll use the parent window as fallback
        print("Using parent window as fallback for testing")
        return parent_hwnd

def measure_performance(func, *args, iterations=5):
    """Measure performance of a function"""
    times = []
    for i in range(iterations):
        start_time = time.time()
        func(*args)
        end_time = time.time()
        times.append(end_time - start_time)
        time.sleep(0.5)  # Wait between iterations
    
    avg_time = sum(times) / len(times)
    median_time = statistics.median(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"Performance metrics ({iterations} iterations):")
    print(f"  Average time: {avg_time:.4f}s")
    print(f"  Median time: {median_time:.4f}s")
    print(f"  Min time: {min_time:.4f}s")
    print(f"  Max time: {max_time:.4f}s")
    
    return {
        "avg": avg_time,
        "median": median_time,
        "min": min_time,
        "max": max_time,
        "times": times
    }

def test_clipboard_method(text_manager, text):
    """Test the clipboard method"""
    print(f"\nTesting clipboard method with text: '{text}'")
    # Save original output mode
    original_mode = config.OUTPUT_MODE
    # Set to clipboard mode
    config.OUTPUT_MODE = config.OutputMode.CLIPBOARD
    
    try:
        text_manager.insert_text(text)
    finally:
        # Restore original mode
        config.OUTPUT_MODE = original_mode

def test_sendmessage_method(text_manager, text, hwnd):
    """Test the SendMessage method"""
    print(f"\nTesting SendMessage method with text: '{text}'")
    # Call send_message directly
    send_message(hwnd, text)

def test_sendmessage_api():
    """Test the Windows SendMessage API"""
    print("\n🧪 Testing Windows SendMessage API...")
    print("=" * 50)
    
    # Initialize TextManager in test mode to prevent actual text insertion
    manager = TextManager(test_mode=True)
    
    # Find VS Code window
    vscode_hwnd = get_vscode_window()
    if not vscode_hwnd:
        print("❌ Cannot proceed with test: No VS Code window found")
        return
    
    # Find edit control
    edit_hwnd = get_edit_control(vscode_hwnd)
    if not edit_hwnd:
        print("❌ Cannot proceed with test: No edit control found")
        return
    
    # Test with different text lengths
    test_texts = [
        "Short text for testing.",
        "Medium length text that spans multiple words and should be a bit longer than the short text.",
        "Longer text that would be more representative of actual transcription output. This text should be long enough to test performance with larger content that might be more challenging for different text insertion methods."
    ]
    
    print("\nTest 1: Performance Comparison")
    print("-" * 30)
    
    clipboard_results = []
    sendmessage_results = []
    
    for i, text in enumerate(test_texts):
        print(f"\nTest 1.{i+1}: Text length {len(text)} characters")
        
        # Test clipboard method
        print("\nClipboard method:")
        clipboard_result = measure_performance(test_clipboard_method, manager, text)
        clipboard_results.append(clipboard_result)
        
        # Test SendMessage method
        print("\nSendMessage method:")
        sendmessage_result = measure_performance(test_sendmessage_method, manager, text, edit_hwnd)
        sendmessage_results.append(sendmessage_result)
    
    # Compare results
    print("\n📊 Performance Comparison:")
    print("-" * 30)
    for i, text in enumerate(test_texts):
        print(f"\nText length: {len(text)} characters")
        clipboard_avg = clipboard_results[i]["avg"]
        sendmessage_avg = sendmessage_results[i]["avg"]
        
        print(f"Clipboard method average: {clipboard_avg:.4f}s")
        print(f"SendMessage method average: {sendmessage_avg:.4f}s")
        
        if sendmessage_avg < clipboard_avg:
            improvement = (clipboard_avg - sendmessage_avg) / clipboard_avg * 100
            print(f"SendMessage is {improvement:.2f}% faster")
        else:
            slowdown = (sendmessage_avg - clipboard_avg) / clipboard_avg * 100
            print(f"SendMessage is {slowdown:.2f}% slower")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_sendmessage_api()
