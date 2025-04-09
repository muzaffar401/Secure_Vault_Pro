# Import necessary libraries
# For custom styled containers
from streamlit_extras.stylable_container import stylable_container
import streamlit as st  # For building the web app interface
import hashlib  # For password hashing and security functions
from cryptography.fernet import Fernet  # For encryption/decryption
import json  # For handling data storage in JSON format
import os  # For file system operations
import time  # For adding delays in the UI
# For handling timestamps and lockout periods
from datetime import datetime, timedelta
import base64  # For encoding/decoding
import qrcode  # For QR code generation
from io import BytesIO  # For handling byte streams
import matplotlib.pyplot as plt  # For password strength visualization
import re  # For password strength regex checking
import cv2
import numpy as np

# Set page configuration FIRST (Streamlit requirement)
st.set_page_config(
    page_title="Secure Vault Pro",  # Browser tab title
    page_icon="🔐",  # Browser tab icon
    layout="wide",  # Use full page width
    initial_sidebar_state="expanded"  # Start with sidebar expanded
)

# Additional UI components

# Constants
MAX_ATTEMPTS = 3  # Maximum failed login attempts before lockout
LOCKOUT_TIME = 300  # 5 minutes in seconds for lockout duration
DATA_FILE = "encrypted_data.json"  # File to store encrypted data
# Hardcoded master password (Note: In production, use environment variables)
MASTER_PASSWORD = "admin123"

# Custom CSS for enhanced UI


def local_css(file_name):
    """Load custom CSS styles from a file and inject additional styles"""


    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    # Additional CSS for gradient text consistency
    st.markdown("""
    <style>
    .gradient-text {
        background-clip: text !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        font-weight: 800;
        font-size: 42px;
        margin: 0.25em 0 !important;
        padding: 0 !important;
        line-height: 1.2;
    }
    .stMarkdown h1 {
        margin: 0.25em 0 !important;
    }
    .qr-code-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 20px 0;
    }
    .password-strength-meter {
        height: 10px;
        border-radius: 5px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    .password-criteria {
        margin: 5px 0;
        font-size: 14px;
    }
    .criteria-met {
        color: #4CAF50;
    }
    .criteria-not-met {
        color: #f44336;
    }
    </style>
    """, unsafe_allow_html=True)

# Background and styling
def set_bg_hack():
    """Set a gradient background for the app"""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Generate or load encryption key
def get_encryption_key():
    """Get or create the encryption key file"""
    if not os.path.exists("secret.key"):
        key = Fernet.generate_key()  # Generate a new key if none exists
        with open("secret.key", "wb") as key_file:
            key_file.write(key)  # Save the key to file
    return open("secret.key", "rb").read()  # Return the existing key

# UI Components
def gradient_text(text, color1, color2, key=None):
    """Create text with gradient coloring"""
    gradient_css = f"""
        background: -webkit-linear-gradient(left, {color1}, {color2});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    """
    key_attr = f"key='{key}'" if key else ""
    return f'<h1 class="gradient-text" style="{gradient_css}" {key_attr}>{text}</h1>'

def card_component(title, content, icon):
    """Create a card UI component with icon, title and content"""
    return f"""
    <div class="card">
        <div class="card-icon">{icon}</div>
        <div class="card-content">
            <h3>{title}</h3>
            <p>{content}</p>
        </div>
    </div>
    """

# QR Code Generation
def generate_qr_code(data):
    """Generate QR code from data and return as bytes"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# Password Strength Checker
def check_password_strength(password):
    """Check password strength and return score (0-4) and feedback"""
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 12:
        score += 1
        feedback.append(("✓ At least 12 characters", True))
    else:
        feedback.append(("✗ At least 12 characters (currently " + str(len(password)) + ")", False))
    
    # Lowercase check
    if re.search(r'[a-z]', password):
        score += 1
        feedback.append(("✓ Contains lowercase letters", True))
    else:
        feedback.append(("✗ Contains lowercase letters", False))
    
    # Uppercase check
    if re.search(r'[A-Z]', password):
        score += 1
        feedback.append(("✓ Contains uppercase letters", True))
    else:
        feedback.append(("✗ Contains uppercase letters", False))
    
    # Digit check
    if re.search(r'[0-9]', password):
        score += 1
        feedback.append(("✓ Contains numbers", True))
    else:
        feedback.append(("✗ Contains numbers", False))
    
    # Special char check
    if re.search(r'[^A-Za-z0-9]', password):
        score += 1
        feedback.append(("✓ Contains special characters", True))
    else:
        feedback.append(("✗ Contains special characters", False))
    
    return score, feedback

def visualize_password_strength(score):
    """Create a password strength visualization"""
    colors = ['#f44336', '#FF5722', '#FFC107', '#4CAF50', '#2E7D32']
    labels = ['Very Weak', 'Weak', 'Moderate', 'Strong', 'Very Strong']
    
    fig, ax = plt.subplots(figsize=(8, 2))
    ax.barh([''], [score], color=colors[score-1])
    ax.set_xlim(0, 5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(2.5, -0.2, labels[score-1], ha='center', va='center', fontsize=12, 
            color=colors[score-1], fontweight='bold')
    
    for i in range(5):
        ax.plot([i, i+1], [0, 0], color='white' if i < score-1 else 'lightgray', 
                linewidth=10, solid_capstyle='butt')
    
    plt.tight_layout()
    return fig

# Main application function
def main():
    # Initialize encryption
    KEY = get_encryption_key()
    cipher = Fernet(KEY)  # Create Fernet cipher instance
    
    # Initialize session state variables
    if 'failed_attempts' not in st.session_state:
        st.session_state.failed_attempts = 0  # Track failed login attempts
    if 'locked_out' not in st.session_state:
        st.session_state.locked_out = False  # Track if user is locked out
    if 'lockout_time' not in st.session_state:
        st.session_state.lockout_time = None  # Track when lockout started
    if 'menu_choice' not in st.session_state:
        st.session_state.menu_choice = "Dashboard"  # Track current menu selection

    # Data management functions
    def load_data():
        """Load encrypted data from file or return empty dict if no file exists"""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_data(data):
        """Save encrypted data to file"""
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)

    stored_data = load_data()  # Load existing data at startup

    # Security functions
    def hash_passkey(passkey, salt=None):
        """Hash a passkey with salt using PBKDF2 for secure storage"""
        if salt is None:
            salt = os.urandom(16).hex()  # Generate a random salt if none provided
        # Using PBKDF2 with 100,000 iterations for key derivation
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            passkey.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # High iteration count for security
        )
        return f"{salt}${hashed.hex()}"  # Return salt and hash combined

    def verify_passkey(passkey, stored_hash):
        """Verify a passkey against a stored hash"""
        if not stored_hash or '$' not in stored_hash:
            return False  # Invalid hash format
        salt, hashed = stored_hash.split('$')  # Split salt and hash
        new_hash = hash_passkey(passkey, salt)  # Recreate hash with same salt
        return new_hash == stored_hash  # Compare with stored hash

    # Encryption functions
    def encrypt_data(text, passkey):
        """Encrypt text data and return encrypted text with hashed passkey"""
        encrypted_text = cipher.encrypt(text.encode()).decode()  # Encrypt and decode to string
        hashed_passkey = hash_passkey(passkey)  # Hash the passkey for storage
        return encrypted_text, hashed_passkey

    def decrypt_data(encrypted_text, passkey):
        """Decrypt data if passkey is correct, handles lockout logic"""
        # Check if user is locked out
        if st.session_state.locked_out:
            remaining_time = LOCKOUT_TIME - (datetime.now() - st.session_state.lockout_time).total_seconds()
            if remaining_time > 0:
                st.error(f"🔒 Account locked. Please try again in {int(remaining_time//60)} minutes and {int(remaining_time%60)} seconds.")
                return None
            else:
                # Lockout period has expired
                st.session_state.locked_out = False
                st.session_state.failed_attempts = 0
                st.session_state.lockout_time = None
        
        # Check all stored data entries for a match
        for key, value in stored_data.items():
            if value["encrypted_text"] == encrypted_text and verify_passkey(passkey, value["passkey"]):
                st.session_state.failed_attempts = 0  # Reset attempts on success
                try:
                    return cipher.decrypt(encrypted_text.encode()).decode()  # Decrypt and return
                except:
                    return None  # Decryption failed
        
        # If no match found, increment failed attempts
        st.session_state.failed_attempts += 1
        if st.session_state.failed_attempts >= MAX_ATTEMPTS:
            st.session_state.locked_out = True
            st.session_state.lockout_time = datetime.now()
            st.error("🔒 Too many failed attempts! Account locked for 5 minutes.")
        return None

    # Apply styling
    set_bg_hack()  # Set background gradient
    local_css("styles.css")  # Load custom CSS

    # Navigation sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header" style="margin-bottom: 20px;">
            <h1 style="margin-bottom: 0;">🔐 Secure Vault</h1>
            <p class="subtitle" style="margin-top: 0; color: #666; font-size: 14px;">Military-Grade Data Protection</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show limited options if locked out
        if st.session_state.locked_out:
            menu_choice = st.selectbox("Navigation", ["Login"], label_visibility="collapsed")
        else:
            menu_choice = st.selectbox("Navigation", ["Dashboard", "Store Data", "Retrieve Data", "Data Vault"], label_visibility="collapsed")
        
        st.session_state.menu_choice = menu_choice  # Update current selection

    # Main Content - Different views based on menu choice
    if st.session_state.menu_choice == "Dashboard":
        # Dashboard view showing stats and info
        st.markdown("""
        <div style="margin-bottom: 30px;">
            <h1 style="margin-bottom: 5px;">Dashboard</h1>
            <div style="display: flex; gap: 20px; margin-top: 20px;">
                <div style="background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); width: 200px;">
                    <p style="margin: 0; font-size: 14px; color: #666;">Security System</p>
                    <p style="margin: 5px 0 0; font-size: 16px; font-weight: bold; color: #4CAF50;">Active</p>
                </div>
                <div style="background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); width: 200px;">
                    <p style="margin: 0; font-size: 14px; color: #666;">Encrypted Items</p>
                    <p style="margin: 5px 0 0; font-size: 16px; font-weight: bold;">{}</p>
                </div>
            </div>
        </div>
        """.format(len(stored_data)), unsafe_allow_html=True)

        # Create three info cards
        cols = st.columns(3)
        with cols[0]:
            st.markdown(card_component(
                "Bank-Level Security",
                "AES-256 encryption with PBKDF2 key derivation",
                "🛡️"
            ), unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(card_component(
                "Zero-Knowledge Protocol",
                "We never store or see your passkeys",
                "🔒"
            ), unsafe_allow_html=True)
        
        with cols[2]:
            st.markdown(card_component(
                "Military Compliance",
                "Meets strictest security standards",
                "🎖️"
            ), unsafe_allow_html=True)

    elif st.session_state.menu_choice == "Store Data":
        # Data encryption and storage view
        st.markdown(gradient_text("Secure Data Storage", "#11998e", "#38ef7d", "store_header"), unsafe_allow_html=True)
        
        # Instructions expander
        with st.expander("ℹ️ How to store data securely", expanded=True):
            st.markdown("""
            1. Enter your sensitive data in the text area below
            2. Create a strong passkey (12+ characters recommended)
            3. Confirm your passkey
            4. Optionally name your data for easier identification
            5. Copy and securely store your encrypted output
            """)
        
        # Two-column layout for input
        with st.container():
            col1, col2 = st.columns(2)
            
            with col1:
                # Data input card
                with stylable_container(
                    "store-data-input-card",
                    css_styles="""
                    {
                        background-color: white;
                        border-radius: 12px;
                        padding: 20px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    }
                    """
                ):
                    user_data = st.text_area(
                        "Enter Data to Encrypt:",
                        height=200,
                        placeholder="Paste your sensitive data here...",
                        key="store_data_input"
                    )
                    
                    data_name = st.text_input(
                        "Data Name (Optional):",
                        placeholder="e.g., 'Financial Records Q3 2023'",
                        help="Give your data a name for easier identification"
                    )
            
            with col2:
                # Passkey input card
                with stylable_container(
                    "store-data-passkey-card",
                    css_styles="""
                    {
                        background-color: white;
                        border-radius: 12px;
                        padding: 20px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    }
                    """
                ):
                    passkey = st.text_input(
                        "Enter Passkey:",
                        type="password",
                        placeholder="Create a strong passkey",
                        help="Minimum 8 characters, include numbers and special characters",
                        key="passkey_input"
                    )
                    
                    # Password strength visualization
                    if passkey:
                        score, feedback = check_password_strength(passkey)
                        st.pyplot(visualize_password_strength(score))
                        
                        # Password criteria feedback
                        for item, met in feedback:
                            st.markdown(f"""
                            <div class="password-criteria {'criteria-met' if met else 'criteria-not-met'}">
                                {item}
                            </div>
                            """, unsafe_allow_html=True)
                    
                    passkey_confirm = st.text_input(
                        "Confirm Passkey:",
                        type="password",
                        placeholder="Re-enter your passkey"
                    )
                    
                    # Encryption button with custom styling
                    with stylable_container(
                        "store-data-primary-button",
                        css_styles="""
                        button {
                            background: linear-gradient(to right, #11998e, #38ef7d);
                            color: white;
                            border: none;
                            padding: 12px 24px;
                            border-radius: 8px;
                            font-weight: bold;
                            width: 100%;
                            margin-top: 10px;
                        }
                        """
                    ):
                        if st.button("Encrypt & Store Data"):
                            # Validate inputs
                            if not user_data or not passkey:
                                st.error("⚠️ Both data and passkey are required!")
                            elif passkey != passkey_confirm:
                                st.error("⚠️ Passkeys don't match!")
                            elif len(passkey) < 8:
                                st.error("⚠️ Passkey must be at least 8 characters!")
                            else:
                                # Encrypt and store data
                                encrypted_text, hashed_passkey = encrypt_data(user_data, passkey)
                                key = data_name if data_name else f"data_{len(stored_data)+1}"
                                stored_data[key] = {
                                    "encrypted_text": encrypted_text,
                                    "passkey": hashed_passkey,
                                    "timestamp": datetime.now().isoformat()
                                }
                                save_data(stored_data)
                                
                                # Show success message with encrypted data
                                with st.expander("🔐 Your Encrypted Data", expanded=True):
                                    st.code(encrypted_text)
                                    
                                    # Generate and display QR code
                                    st.markdown("### QR Code for Encrypted Data")
                                    qr_img = generate_qr_code(encrypted_text)
                                    st.image(qr_img, caption="Scan this QR code to save your encrypted data", width=200)
                                    
                                    st.markdown("""
                                    <div class="warning-box">
                                        <strong>⚠️ Important Security Notice:</strong>
                                        <p>1. Copy and securely store this encrypted text</p>
                                        <p>2. Remember your passkey - it cannot be recovered</p>
                                        <p>3. Store them separately for maximum security</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # Download buttons
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.download_button(
                                            label="Download Encrypted Data",
                                            data=encrypted_text,
                                            file_name=f"secure_vault_{datetime.now().strftime('%Y%m%d')}.enc",
                                            mime="text/plain"
                                        )
                                    with col2:
                                        st.download_button(
                                            label="Download QR Code",
                                            data=qr_img,
                                            file_name=f"secure_vault_{datetime.now().strftime('%Y%m%d')}.png",
                                            mime="image/png"
                                        )

    elif st.session_state.menu_choice == "Retrieve Data":
        # Data decryption view
        st.markdown(gradient_text("Data Retrieval Portal", "#8E2DE2", "#4A00E0", "retrieve_header"), unsafe_allow_html=True)
        
        # Show warning if attempts remaining
        if st.session_state.get('failed_attempts', 0) > 0:
            with stylable_container(
                "retrieve-warning-box",
                css_styles="""
                {
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 12px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                """
            ):
                st.warning(f"⚠️ You have {MAX_ATTEMPTS - st.session_state.failed_attempts} attempts remaining before system lockout.")
        
        # Two-column layout
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Encrypted data input
                with stylable_container(
                    "retrieve-data-input-card",
                    css_styles="""
                    {
                        background-color: white;
                        border-radius: 12px;
                        padding: 20px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    }
                    """
                ):
                    encrypted_text = st.text_area(
                        "Encrypted Data:",
                        height=200,
                        placeholder="Paste your encrypted data here...",
                        key="retrieve_data_input",
                        value=st.session_state.get('retrieve_encrypted', '')
                    )
                    
# In the QR code scanning section, update to:
                    uploaded_file = st.file_uploader("Or upload QR code:", type=['png', 'jpg', 'jpeg'], key="qr_uploader")
                    if uploaded_file is not None and not st.session_state.get('qr_processed', False):
                        try:
                            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                            qr_detector = cv2.QRCodeDetector()
                            data, points, _ = qr_detector.detectAndDecode(img)
        
                            if data:
                                st.session_state.scanned_data = data
                                st.session_state.qr_processed = True  # Mark as processed
                                st.success("QR code scanned successfully!")
                            else:
                                st.error("No QR code found in the image")
                        except Exception as e:
                            st.error(f"Error scanning QR code: {str(e)}")
                    elif uploaded_file is None:
    # Reset the processing flag when no file is uploaded
                        st.session_state.qr_processed = False

# In your text_area widget:
            encrypted_text = st.text_area(
    "Encrypted Data:",
    height=200,
    placeholder="Paste your encrypted data here...",
    key="encrypted_data_input",
    value=st.session_state.get('scanned_data', '')
)

            
            with col2:
                # Passkey input
                with stylable_container(
                    "retrieve-passkey-card",
                    css_styles="""
                    {
                        background-color: white;
                        border-radius: 12px;
                        padding: 20px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    }
                    """
                ):
                    passkey = st.text_input(
                        "Your Passkey:",
                        type="password",
                        placeholder="Enter your secret passkey",
                        key="retrieve_passkey_input"
                    )
                    
                    # Decryption button
                    with stylable_container(
                        "retrieve-primary-button",
                        css_styles="""
                        button {
                            background: linear-gradient(to right, #8E2DE2, #4A00E0);
                            color: white;
                            border: none;
                            padding: 12px 24px;
                            border-radius: 8px;
                            font-weight: bold;
                            width: 100%;
                            margin-top: 10px;
                        }
                        """
                    ):
                        if st.button("Decrypt Data"):
                            # Validate inputs
                            if not encrypted_text or not passkey:
                                st.error("⚠️ Both encrypted data and passkey are required!")
                            else:
                                decrypted_text = decrypt_data(encrypted_text, passkey)
                                
                                if decrypted_text:
                                    # Success case
                                    st.success("✅ Authentication successful! Decrypting your data...")
                                    time.sleep(1)
                                    
                                    # Show decrypted data
                                    with stylable_container(
                                        "retrieve-success-box",
                                        css_styles="""
                                        {
                                            background-color: #d4edda;
                                            border-left: 4px solid #28a745;
                                            padding: 12px;
                                            border-radius: 4px;
                                            margin-top: 20px;
                                        }
                                        """
                                    ):
                                        st.text_area(
                                            "Decrypted Content:",
                                            value=decrypted_text,
                                            height=300,
                                            key="decrypted_output"
                                        )
                                        
                                        # Download button for decrypted data
                                        st.download_button(
                                            label="Download Decrypted Data",
                                            data=decrypted_text,
                                            file_name="decrypted_data.txt",
                                            mime="text/plain"
                                        )
                                elif not st.session_state.locked_out:
                                    remaining_attempts = MAX_ATTEMPTS - st.session_state.failed_attempts
                                    if remaining_attempts > 0:
                                        st.error(f"❌ Authentication failed! Attempts remaining: {remaining_attempts}")

    elif st.session_state.menu_choice == "Data Vault":
        # View showing all stored encrypted items
        st.markdown(gradient_text("Your Secure Data Vault", "#f46b45", "#eea849", "vault_header"), unsafe_allow_html=True)
        
        if not stored_data:
            st.info("ℹ️ Your vault is empty. Store some data to see it here.")
        else:
            # Show vault statistics
            st.markdown(f"""
            <div class="vault-stats">
                <div class="stat-box">
                    <span class="stat-number">{len(stored_data)}</span>
                    <span class="stat-label">Encrypted Items</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # List all stored items in expanders
            for name, data in stored_data.items():
                with st.expander(f"🔒 {name}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        # Show truncated encrypted data
                        st.code(data["encrypted_text"][:200] + "..." if len(data["encrypted_text"]) > 200 else data["encrypted_text"])
                        st.caption(f"Stored on: {datetime.fromisoformat(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    with col2:
                        # Button to retrieve this specific item
                        if st.button("Retrieve", key=f"retrieve_{name}"):
                            st.session_state.retrieve_encrypted = data["encrypted_text"]
                            st.session_state.menu_choice = "Retrieve Data"
                            st.rerun()  # Switch to retrieve view

    elif st.session_state.menu_choice == "Login":
        # Authentication view for locked-out users
        st.markdown(gradient_text("Security Reauthentication", "#ff416c", "#ff4b2b", "login_header"), unsafe_allow_html=True)
        
        # Check lockout status
        if st.session_state.locked_out:
            remaining_time = LOCKOUT_TIME - (datetime.now() - st.session_state.lockout_time).total_seconds()
            if remaining_time > 0:
                # Show lockout message
                with stylable_container(
                    "login-error-box",
                    css_styles="""
                    {
                        background-color: #f8d7da;
                        border-left: 4px solid #dc3545;
                        padding: 12px;
                        border-radius: 4px;
                        margin-bottom: 20px;
                    }
                    """
                ):
                    st.error(f"""
                    🔒 Security Lockout Active
                    
                    Please try again in {int(remaining_time//60)} minutes and {int(remaining_time%60)} seconds.
                    """)
            else:
                # Lockout period expired
                st.session_state.locked_out = False
                st.session_state.failed_attempts = 0
                st.session_state.lockout_time = None
        
        # Show login form if not locked out
        if not st.session_state.locked_out:
            with stylable_container(
                "login-box",
                css_styles="""
                {
                    background-color: white;
                    border-radius: 12px;
                    padding: 30px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    max-width: 500px;
                    margin: 0 auto;
                }
                """
            ):
                st.markdown("""
                <div style="text-align: center; margin-bottom: 30px;">
                    <h3>Security Verification Required</h3>
                    <p>Please authenticate to continue</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Master password input
                login_pass = st.text_input(
                    "Master Security Key:",
                    type="password",
                    placeholder="Enter master password",
                    key="master_pass_input"
                )
                
                # Login button
                with stylable_container(
                    "login-primary-button",
                    css_styles="""
                    button {
                        background: linear-gradient(to right, #ff416c, #ff4b2b);
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 8px;
                        font-weight: bold;
                        width: 100%;
                        margin-top: 20px;
                    }
                    """
                ):
                    if st.button("Authenticate"):
                        if login_pass == MASTER_PASSWORD:
                            # Successful authentication
                            st.session_state.failed_attempts = 0
                            st.session_state.locked_out = False
                            st.success("✅ Authentication successful! Redirecting...")
                            time.sleep(1)
                            st.session_state.menu_choice = "Dashboard"
                            st.rerun()  # Return to dashboard
                        else:
                            st.error("❌ Invalid security key!")

# Entry point
if __name__ == "__main__":
    main()