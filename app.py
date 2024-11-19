import os
from flask import Flask, request, jsonify

app = Flask(__name__)
@app.route('/')
def home():
    return "MamaMetric API is running!", 200

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

    # Determine the trimester and corresponding β_ffm
    if week <= 12:  # 1st trimester
        beta_ffm = 44.47
    elif week <= 27:  # 2nd trimester
        beta_ffm = 30.72
    else:  # 3rd trimester
        beta_ffm = 68.3

    # Define regression coefficients (example coefficients from the table)
    # Wang, et al. Reproductive Health (2017) DOI 10.1186/s12978-017-0308-3
    # coefficients for predicting FFM
    intercept = 68.3
    beta_bmi = 16.16
    beta_week = 11.35
    
    # Updated normalization constants based on the paper
    mean_ffm = 85  # Average FFM for normalization
    mean_bmi = 21  # Average BMI for normalization
    max_week = 40  # Full pregnancy duration in weeks
    
    # Calculate predicted FFM range
    predicted_ffm = (
        intercept 
        + beta_ffm * (ffm / mean_ffm) 
        + beta_bmi * (bmi / mean_bmi) 
        + beta_week * (week / max_week)
    )

    margin = 5 # Example margin for lower bound and upper bound
    lower_bound = predicted_ffm - margin  
    upper_bound = predicted_ffm + margin  

    # Predict current weight and fat mass
    avg_fat_mass = 40  # Average fat mass from dataset
    predicted_current_weight = predicted_ffm + avg_fat_mass
    predicted_fat_mass = avg_fat_mass

    # Check if the current FFM is within the healthy range
    # Message for whether the current FFM is within the range
    message = f"Recommended FFM range for week {week}: {round(lower_bound, 1)} - {round(upper_bound, 1)} lbs. "
    if lower_bound <= ffm <= upper_bound:
        message += f"Your current FFM {ffm} is in this range."
        guidance = "You're doing great. Keep up the good work!"
    else:
        message += f"Your current FFM {ffm} is NOT in this range."
        if ffm < lower_bound:
            guidance = "You may need to increase your FFM."
        else:
            guidance = "You may need to decrease your FFM."
        

    # Return the results
    return jsonify({
        "week": week,
        "pre_pregnancy_bmi": round(bmi, 2),
        "current_ffm": round(ffm, 2),
        "predicted_ffm": round(predicted_ffm, 2),
        "predicted_current_weight": round(predicted_current_weight, 2),
        "predicted_fat_mass": round(predicted_fat_mass, 2),
        "lower_bound": round(lower_bound, 2),
        "upper_bound": round(upper_bound, 2),
        "message": message,
        "guidance": guidance
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the PORT environment variable or default to 5000
    app.run(host='0.0.0.0', port=port)  # Bind to all interfaces (0.0.0.0)