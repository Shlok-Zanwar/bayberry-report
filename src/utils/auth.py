"""Shared authentication module for all Streamlit pages."""
import streamlit as st
from abc import ABC, abstractmethod


class UserRole(ABC):
    """Base class for user roles and permissions."""
    
    @abstractmethod
    def get_allowed_segments(self) -> list:
        """Return list of segments this user can access."""
        pass

    @abstractmethod
    def can_access_page(self, page_name: str) -> bool:
        """Check if user can access a specific page."""
        pass

    @abstractmethod
    def get_role_name(self) -> str:
        """Return the name of the role."""
        pass


class AdminRole(UserRole):
    """Full access to all data and pages."""
    
    def get_allowed_segments(self) -> list:
        return ['PCD', 'THIRD PARTY', 'Internal', 'EXPORT']

    def can_access_page(self, page_name: str) -> bool:
        return True

    def get_role_name(self) -> str:
        return st.secrets.get("ADMIN_USERNAME")


class RestrictedRole(UserRole):
    """Restricted access to specific segments and pages."""
    
    def get_allowed_segments(self) -> list:
        return ['PCD']

    def can_access_page(self, page_name: str) -> bool:
        # Only allow Sales Profit Analysis
        return page_name == "Sales Profit Analysis"

    def get_role_name(self) -> str:
        return st.secrets.get("ROLE_1_USERNAME")


def require_password():
    """Require username and password authentication before showing any app content.
    
    This function should be called at the top of every page before any
    data loading, processing, or UI rendering occurs.
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user = None

    if not st.session_state.authenticated:
        st.markdown("### 🔒 Bayberry Data Analytics - Login Required")
        
        username = st.text_input("Username", key="username_input")
        password = st.text_input("Password", type="password", key="password_input")
        
        if st.button("Login"):
            # Check Admin Credentials
            if (username == st.secrets.get("ADMIN_USERNAME") and 
                password == st.secrets.get("ADMIN_PASSWORD")):
                st.session_state.authenticated = True
                st.session_state.user = AdminRole()
                st.success(f"✅ Welcome {username}! Loading Admin dashboard...")
                st.rerun()
            
            # Check Restricted Credentials
            elif (username == st.secrets.get("ROLE_1_USERNAME") and 
                  password == st.secrets.get("ROLE_1_PASSWORD")):
                st.session_state.authenticated = True
                st.session_state.user = RestrictedRole()
                st.success(f"✅ Welcome {username}! Loading restricted dashboard...")
                st.rerun()
            
            else:
                st.error("❌ Incorrect username or password")
        st.stop()
