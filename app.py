import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict-ffm', methods=['POST'])
def predict_ffm():
    # Extract user inputs from the API request
    data = request.json
    height_feet = data.get('height_feet')  # Height in feet
    height_inches = data.get('height_inches')  # Height in inches
    week = data.get('week')  # Week of pregnancy
    pre_pregnancy_weight = data.get('pre_pregnancy_weight')  # Pre-pregnancy weight (lbs)
    current_weight = data.get('current_weight')  # Current weight (lbs)
    fat_mass = data.get('fat_mass')  # Fat mass (lbs)

    # Convert height to total inches
    height_total_inches = (height_feet * 12) + height_inches

    # Convert height to meters (1 inch = 0.0254 meters)
    height_meters = height_total_inches * 0.0254

    # Calculate BMI (BMI = weight in kg / height in meters^2)
    pre_pregnancy_weight_kg = pre_pregnancy_weight * 0.453592  # Convert lbs to kg
    bmi = pre_pregnancy_weight_kg / (height_meters ** 2)

    # Calculate Fat-Free Mass (FFM = Current Weight - Fat Mass)
    ffm = current_weight - fat_mass

    # Define regression coefficients (example coefficients from your table)
    beta_ffm = 44.47
    beta_bmi = 16.16
    beta_week = 11.35
    intercept = 68.3

    # Calculate predicted FFM range
    predicted_ffm = intercept + beta_ffm * (ffm / 70) + beta_bmi * (bmi / 25) + beta_week * (week / 40)
    lower_bound = predicted_ffm - 5  # Example margin for lower bound
    upper_bound = predicted_ffm + 5  # Example margin for upper bound

    # Check if the current FFM is within the healthy range
    message = "Your FFM is within the healthy range!" if lower_bound <= ffm <= upper_bound else "Your FFM is outside the healthy range!"

    # Return the results
    return jsonify({
        "week": week,
        "pre_pregnancy_bmi": round(bmi, 2),
        "current_ffm": round(ffm, 2),
        "predicted_ffm": round(predicted_ffm, 2),
        "lower_bound": round(lower_bound, 2),
        "upper_bound": round(upper_bound, 2),
        "message": message
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the PORT environment variable or default to 5000
    app.run(host='0.0.0.0', port=port)  # Bind to all interfaces (0.0.0.0)