import json
from bigfix_universal_remote_qna.models.connection_profile import ConnectionProfile
from typing import List, Optional
from dataclasses import asdict
from tkinter import messagebox


class ProfileManager:
    """Manages connection profiles using ConfigManager"""
    
    def __init__(self, config_manager, security_manager):
        self.config_manager = config_manager
        self.security_manager = security_manager
    
    def get_all_profiles(self) -> List[ConnectionProfile]:
        """Get all connection profiles"""
        try:
            profiles_json = self.config_manager.get_setting("connection_profiles")
            profiles_data = json.loads(profiles_json) if profiles_json else []
            return [ConnectionProfile(**profile) for profile in profiles_data]
        except (json.JSONDecodeError, TypeError):
            return []
    
    def save_profile(self, profile: ConnectionProfile) -> bool:
        """Save or update a connection profile"""
        profiles = self.get_all_profiles()
        
        # Check for existing profile
        existing_index = -1
        for i, existing_profile in enumerate(profiles):
            if existing_profile.name == profile.name:
                existing_index = i
                break
        
        if existing_index >= 0:
            if messagebox.askyesno("Update Profile", 
                                 f"Profile '{profile.name}' already exists. Update it?"):
                profiles[existing_index] = profile
            else:
                return False
        else:
            profiles.append(profile)
        
        # Save back to config
        profiles_data = [asdict(profile) for profile in profiles]
        profiles_json = json.dumps(profiles_data)
        
        # Update the setting (assuming your ConfigManager has an update method)
        # If not, you might need to define a new setting or have an update_setting method
        try:
            # Try to update existing setting
            self.config_manager.define_setting(
                "connection_profiles", False, profiles_json, str,
                "JSON array of saved connection profiles"
            )
        except:
            pass  # Setting might already exist
        
        return True
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a connection profile"""
        profiles = self.get_all_profiles()
        profiles = [p for p in profiles if p.name != profile_name]
        
        profiles_data = [asdict(profile) for profile in profiles]
        profiles_json = json.dumps(profiles_data)
        
        try:
            self.config_manager.define_setting(
                "connection_profiles", False, profiles_json, str,
                "JSON array of saved connection profiles"
            )
        except:
            pass
        
        return True
    
    def get_profile_by_name(self, profile_name: str) -> Optional[ConnectionProfile]:
        """Get a specific profile by name"""
        profiles = self.get_all_profiles()
        for profile in profiles:
            if profile.name == profile_name:
                return profile
        return None
