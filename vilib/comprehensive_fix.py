#!/usr/bin/env python3
"""
Comprehensive fix for vilib camera threading issues
This patches both camera_close and camera methods
"""

def apply_comprehensive_fix():
    # Read the original file
    with open('vilib.py', 'r') as f:
        content = f.read()
    
    # 1. Fix camera_close method
    old_camera_close = '''    @staticmethod
    def camera_close():
        if Vilib.camera_thread != None:
            Vilib.camera_run = False
            time.sleep(0.1)'''
    
    new_camera_close = '''    @staticmethod
    def camera_close():
        if Vilib.camera_thread != None:
            Vilib.camera_run = False
            time.sleep(0.2)
            # Wait for camera thread to finish
            if Vilib.camera_thread.is_alive():
                Vilib.camera_thread.join(timeout=3.0)
            
            # Properly close and reinitialize Picamera2
            try:
                if Vilib.picam2 is not None:
                    Vilib.picam2.close()
                    time.sleep(0.2)
                    
                # Recreate Picamera2 object completely fresh
                Vilib.picam2 = Picamera2()
                
            except Exception as e:
                print(f"Warning during camera cleanup: {e}")
                # Force recreation of Picamera2 object
                try:
                    Vilib.picam2 = Picamera2()
                except Exception as e2:
                    print(f"Failed to reinitialize camera: {e2}")
            
            # Reset thread reference
            Vilib.camera_thread = None'''
    
    # 2. Fix camera method to be more robust
    old_camera_start = '''        preview_config = picam2.preview_configuration
        # preview_config.size = (800, 600)
        preview_config.size = Vilib.camera_size'''
    
    new_camera_start = '''        # Ensure we have a fresh configuration
        try:
            preview_config = picam2.preview_configuration
            if preview_config is None:
                # Create new configuration if needed
                config = picam2.create_preview_configuration()
                picam2.configure(config)
                preview_config = picam2.preview_configuration
        except Exception as e:
            print(f"Error getting preview configuration: {e}")
            # Try to create a new configuration
            config = picam2.create_preview_configuration()
            picam2.configure(config)
            preview_config = picam2.preview_configuration
        
        # preview_config.size = (800, 600)
        if preview_config is not None:
            preview_config.size = Vilib.camera_size'''
    
    # Apply the fixes
    content = content.replace(old_camera_close, new_camera_close)
    content = content.replace(old_camera_start, new_camera_start)
    
    # Write the fixed file
    with open('vilib.py', 'w') as f:
        f.write(content)
    
    print("Applied comprehensive vilib fix!")
    return True

if __name__ == "__main__":
    apply_comprehensive_fix()
