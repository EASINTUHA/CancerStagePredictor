from flask import Flask, request, render_template, jsonify
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

app = Flask(__name__)

# Load the saved model
model = joblib.load('cancer_stage_model.pkl')

# Load dataset to get unique categorical values
df = pd.read_csv('global_cancer_patients_2015_2024.csv')

# Define feature lists
numerical_features = ['Age', 'Genetic_Risk', 'Air_Pollution', 'Alcohol_Use', 'Smoking', 'Obesity_Level', 'Treatment_Cost_USD']
categorical_features = ['Gender', 'Country_Region', 'Cancer_Type', 'Target_Severity_Score']

# Get unique values for categorical features
genders = sorted(df['Gender'].unique().tolist())  # ['Female', 'Male', 'Other']
countries = sorted(df['Country_Region'].unique().tolist())  # ['Australia', 'Brazil', ...]
cancer_types = sorted(df['Cancer_Type'].unique().tolist())  # ['Breast', 'Cervical', ...]
severity_scores = sorted(df['Target_Severity_Score'].astype(str).unique().tolist())  # ['0.1', '0.2', ...]

# Create label encoders for categorical features
label_encoders = {}
for feature in categorical_features:
    le = LabelEncoder()
    le.fit(df[feature])
    label_encoders[feature] = le

@app.route('/')
def home():
    return render_template('index.html', 
                         numerical_features=numerical_features,
                         genders=genders,
                         countries=countries,
                         cancer_types=cancer_types,
                         severity_scores=severity_scores)

@app.route('/predict', methods=['POST'])
def predict():
    # Collect numerical features
    features = []
    for feature in numerical_features:
        value = float(request.form.get(feature, 0))
        features.append(value)
    
    # Collect and encode categorical features
    for feature in categorical_features:
        value = request.form.get(feature)
        try:
            encoded_value = label_encoders[feature].transform([value])[0]
            features.append(encoded_value)
        except ValueError:
            return jsonify({'error': f'Invalid value for {feature}'}), 400
    
    # Create a DataFrame with the correct feature order
    input_data = pd.DataFrame([features], columns=numerical_features + categorical_features)
    
    # Make prediction
    prediction = model.predict(input_data)[0]
    prediction_text = f'Stage {prediction}'
    
    # Check if request is AJAX (expects JSON)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'prediction': prediction_text})
    
    # Otherwise, render HTML
    return render_template('index.html', 
                         prediction_text=f'Predicted Cancer Stage: {prediction_text}',
                         numerical_features=numerical_features,
                         genders=genders,
                         countries=countries,
                         cancer_types=cancer_types,
                         severity_scores=severity_scores)

if __name__ == '__main__':
    app.run(debug=True)