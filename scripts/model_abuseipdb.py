import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib

print("🚀 Starting ML modeling...")

# --- Load latest CSV file ---
data_folder = Path(__file__).resolve().parent.parent / "data"
latest_csv = max(data_folder.glob("abuseipdb_reports_*.csv"), key=lambda f: f.stat().st_mtime)
print("📂 Using dataset:", latest_csv)

df = pd.read_csv(latest_csv)
print("✅ Loaded", len(df), "records")

# --- Features available in your dataset ---
print("🧱 Columns found:", df.columns.tolist())

# We'll use only the columns you have
features = ["countryCode", "abuseConfidenceScore"]
df = df[features].copy()

# Encode countryCode (categorical → numeric)
le_country = LabelEncoder()
df["countryCode"] = le_country.fit_transform(df["countryCode"].astype(str))

# Create target variable:
# IPs with abuseConfidenceScore >= 75 → malicious (1)
# otherwise → benign (0)
df["malicious"] = (df["abuseConfidenceScore"] >= 75).astype(int)

# Split data into features (X) and target (y)
X = df[["countryCode", "abuseConfidenceScore"]]
y = df["malicious"]

# --- Train-test split ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Train Random Forest model ---
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# --- Evaluate model ---
y_pred = model.predict(X_test)

print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))

print("🧩 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# --- Feature importance ---
importances = pd.Series(model.feature_importances_, index=X.columns)
print("\n🔥 Feature Importances:")
print(importances.sort_values(ascending=False))

# --- Save trained model ---
model_path = data_folder / "rf_model_abuseipdb.pkl"
joblib.dump(model, model_path)
print(f"💾 Model saved to {model_path}")

