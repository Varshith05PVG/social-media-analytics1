import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# 1. Load the real data from profiles.csv
df = pd.read_csv('data/profiles.csv')

# 2. Select the Features (The 'Signals')
# Using the features available in profiles.csv
features = ['followers', 'following', 'bio_len']
X = df[features]
y = df['is_scam']

# 3. Train the Random Forest (Fusion Layer)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 4. Save the Model
os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/scam_detector.pkl')

print("✅ Success: AI Brain trained on profiles.csv data!")
print(f"Model trained on {len(df)} profiles")
print(f"Features used: {features}")
print(f"Spam profiles: {y.sum()} / {len(y)}")