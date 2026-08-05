import streamlit as st
import requests
import joblib
import numpy as np
import os

# --- 1. LOAD THE TRAINED MODEL ---
model_path = 'models/scam_detector.pkl'

@st.cache_resource
def load_model():
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        st.warning("⚠️ Model not found! Please run train_model.py first to train the model.")
        return None

model = load_model()

# --- 2. THE SCRAPER (FETCH PROFILE DATA) ---
def fetch_profile_from_url(url):
    try:
        # Improved username extraction
        username = url.rstrip("/").split("/")[-1]
        api_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        headers = {
            "x-ig-app-id": "936619743392459",
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        user_data = response.json()['data']['user']
        return {"status": "Success", "data": user_data}
    except Exception as e:
        return {"status": "Error", "message": str(e)}

# --- 3. SPAM DETECTION (USING TRAINED MODEL) ---
def detect_spam(followers, following, bio_length):
    """Predict if a profile is spam and return spam score"""
    if model is None:
        return None, None
    
    # Prepare features for prediction
    features = np.array([[followers, following, bio_length]])
    
    # Get prediction (0 or 1)
    prediction = model.predict(features)[0]
    
    # Get prediction probability score (0 to 1)
    prediction_proba = model.predict_proba(features)[0]
    spam_score = prediction_proba[1]  # Probability of spam
    
    return prediction, spam_score

# --- 4. THE UI (DISPLAY LAYER) ---
st.title("🛡️ GuardianAI - Social Media Spam Detector")
st.markdown("Detect if a social media profile is spam using AI")

profile_url = st.text_input("Enter Instagram URL (e.g., https://instagram.com/username):")

if st.button("🚀 Analyze Profile"):
    if profile_url:
        with st.spinner("Fetching profile data..."):
            result = fetch_profile_from_url(profile_url)
            
            if result['status'] == "Success":
                user = result['data']
                
                # Extract required data
                followers = user['edge_followed_by']['count']
                following = user['edge_follow']['count']
                bio_length = len(user['biography'])
                profile_pic = user['profile_pic_url_hd']
                username = user['username']
                
                # --- 5. RUN SPAM DETECTION ---
                with st.spinner("Running spam detection..."):
                    is_spam, spam_score = detect_spam(followers, following, bio_length)
                
                # --- 6. DISPLAY RESULTS ---
                st.divider()
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(profile_pic, caption=f"Profile Pic - @{username}", use_column_width=True)
                
                with col2:
                    st.subheader(f"@{username}")
                    st.write(f"**Bio:** {user['biography']}")
                    
                    # Display metrics
                    metric_col1, metric_col2 = st.columns(2)
                    with metric_col1:
                        st.metric("👥 Followers", f"{followers:,}")
                    with metric_col2:
                        st.metric("🔗 Following", f"{following:,}")
                
                st.divider()
                
                # Spam Detection Result
                if is_spam == 1:
                    st.error(f"⚠️ **STATUS: SPAM DETECTED**")
                    st.metric("Spam Score", f"{spam_score:.2%}", delta=f"{(spam_score*100):.1f}% confidence")
                else:
                    st.success(f"✅ **STATUS: LEGITIMATE**")
                    st.metric("Spam Score", f"{spam_score:.2%}", delta=f"{((1-spam_score)*100):.1f}% confidence")
                
                # Additional details
                with st.expander("📊 Detailed Analysis"):
                    st.write(f"**Followers:** {followers:,}")
                    st.write(f"**Following:** {following:,}")
                    st.write(f"**Bio Length:** {bio_length} characters")
                    st.write(f"**Spam Probability Score:** {spam_score:.4f} (0.0 = Legitimate, 1.0 = Spam)")
            else:
                st.error(f"❌ Error: {result['message']}")
                st.info("Make sure the profile is public and the URL is correct.")
    else:
        st.warning("Please enter an Instagram URL to analyze.")