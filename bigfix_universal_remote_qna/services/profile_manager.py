import json
import os
from bigfix_universal_remote_qna.models.connection_profile import ConnectionProfile
from typing import List, Optional
from dataclasses import asdict
from tkinter import messagebox


class ProfileManager:
    """ProfileManager that saves to a specific JSON file"""
    
    def __init__(self, config_manager, security_manager, profiles_file: str = None):
        self.config_manager = config_manager
        self.security_manager = security_manager
        
        # Default profiles file location
        if profiles_file is None:
            profiles_file = os.path.join(
                os.path.expanduser("~"), 
                ".bigfix_profiles.json"
            )
        
        self.profiles_file = profiles_file
        
        # Ensure directory exists
        profiles_dir = os.path.dirname(self.profiles_file)
        if profiles_dir:
            os.makedirs(profiles_dir, exist_ok=True)
        
        # Create empty profiles file if it doesn't exist
        self._ensure_profiles_file_exists()
        
        print(f"✓ Profiles will be saved to: {self.profiles_file}")
    
    def _ensure_profiles_file_exists(self):
        """Create empty profiles file if it doesn't exist"""
        if not os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'w') as f:
                    json.dump([], f, indent=2)
                print(f"✓ Created empty profiles file: {self.profiles_file}")
            except Exception as e:
                print(f"✗ Could not create profiles file: {e}")
    
    def get_all_profiles(self) -> List[ConnectionProfile]:
        """Get all connection profiles from file"""
        try:
            with open(self.profiles_file, 'r') as f:
                profiles_data = json.load(f)
                return [ConnectionProfile(**profile) for profile in profiles_data]
        except (json.JSONDecodeError, TypeError, FileNotFoundError) as e:
            print(f"Error loading profiles: {e}")
            # If file is corrupted, recreate it
            self._ensure_profiles_file_exists()
            return []
    
    def save_profile(self, profile: ConnectionProfile) -> bool:
        """Save or update a connection profile to file"""
        profiles = self.get_all_profiles()
        
        # Check for existing profile
        existing_index = -1
        for i, existing_profile in enumerate(profiles):
            if existing_profile.name == profile.name:
                existing_index = i
                break
        
        if existing_index >= 0:
            if not messagebox.askyesno("Update Profile", 
                                     f"Profile '{profile.name}' already exists. Update it?"):
                return False
            profiles[existing_index] = profile
        else:
            profiles.append(profile)
        
        # Save to file
        try:
            profiles_data = [asdict(profile) for profile in profiles]
            with open(self.profiles_file, 'w') as f:
                json.dump(profiles_data, f, indent=2)
            
            print(f"✓ Profile '{profile.name}' saved to {self.profiles_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error saving profile: {e}")
            return False
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a connection profile from file"""
        profiles = self.get_all_profiles()
        original_count = len(profiles)
        profiles = [p for p in profiles if p.name != profile_name]
        
        if len(profiles) == original_count:
            print(f"✗ Profile '{profile_name}' not found")
            return False
        
        try:
            profiles_data = [asdict(profile) for profile in profiles]
            with open(self.profiles_file, 'w') as f:
                json.dump(profiles_data, f, indent=2)
            
            print(f"✓ Profile '{profile_name}' deleted from {self.profiles_file}")
            return True
            
        except Exception as e:
            print(f"✗ Error deleting profile: {e}")
            return False
    
    def get_profile_by_name(self, profile_name: str) -> Optional[ConnectionProfile]:
        """Get a specific profile by name from file"""
        profiles = self.get_all_profiles()
        for profile in profiles:
            if profile.name == profile_name:
                return profile
        return None