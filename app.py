from flask import Flask, request, render_template
import joblib
import pandas as pd
import numpy as np
from transformers import pipeline

app = Flask(__name__)

# Load the trained model
try:
    print("Loading model...")
    model = joblib.load("water_quality_model.pkl")
    print("Model loaded successfully.")
except Exception as e:
    print(f"Model load failed: {e}")
    model = None

# Define feature names
feature_names = ["ph_normalized", "Solids", "Chloramines", "Sulfate", "Turbidity"]

# Store submissions
submissions = []

# Safe thresholds for water quality
THRESHOLDS = {
    "ph": (6.5, 8.5),
    "Solids": (0, 10000),
    "Chloramines": (0, 4),
    "Sulfate": (0, 250),
    "Turbidity": (0, 5)
}

# Load NLP model
try:
    print("Loading NLP model...")
    generator = pipeline("text-generation", model="gpt2", max_length=150, temperature=1.2)
    print("NLP model loaded successfully.")
except Exception as e:
    print(f"NLP load failed: {e}")
    generator = None

def is_coherent_and_relevant(text, parameter):
    # Check for coherence and relevance to water quality
    invalid_phrases = ["http", "gallons", "equestration", "salad", "mucous", "membrane", "mercury"]
    required_terms = {"ph": ["ph", "alkaline", "acid"], "Solids": ["solids", "filter"], 
                      "Chloramines": ["chloramines", "carbon", "filter"], 
                      "Sulfate": ["sulfate", "ion", "resin"], 
                      "Turbidity": ["turbidity", "clarify", "filter"]}
    return (all(phrase.lower() not in text.lower() for phrase in invalid_phrases) and 
            len(text.split()) >= 12 and 
            any(term in text.lower() for term in required_terms.get(parameter, [])))

def generate_suggestion(issue, parameter, value, threshold):
    if generator is None:
        # Dynamic fallback with multiple options
        fallback_options = {
            "ph_low": [
                f"To raise the pH from {value} to {threshold}, add calcium hydroxide and mix thoroughly. Test with a pH meter, adjusting gradually to stay between 6.5 and 8.5.",
                f"To increase pH from {value} to {threshold}, use sodium carbonate with good stirring. Check levels with a pH tester to maintain 6.5–8.5."
            ],
            "ph_high": [
                f"To lower the pH from {value} to {threshold}, add diluted phosphoric acid slowly. Monitor with a pH meter to keep it between 6.5 and 8.5.",
                f"To reduce pH from {value} to {threshold}, introduce vinegar in small amounts. Verify with a pH sensor to stabilize at 6.5–8.5."
            ],
            "Solids_high": [
                f"To reduce solids from {value} ppm to below {threshold} ppm, install a reverse osmosis filter. Clean it monthly and check with a TDS meter.",
                f"To lower solids from {value} ppm to below {threshold} ppm, use an ultrafiltration system. Maintain weekly and test water quality regularly."
            ],
            "Chloramines_high": [
                f"To decrease chloramines from {value} ppm to below {threshold} ppm, use an activated carbon filter. Replace every 6 months and test with a chlorine kit.",
                f"To reduce chloramines from {value} ppm to below {threshold} ppm, install a catalytic carbon unit. Check monthly with a test strip and replace yearly."
            ],
            "Sulfate_high": [
                f"To lower sulfate from {value} mg/L to below {threshold} mg/L, use an ion exchange resin. Regenerate with salt and monitor levels regularly.",
                f"To reduce sulfate from {value} mg/L to below {threshold} mg/L, apply reverse osmosis. Maintain the system and check with a sulfate test kit."
            ],
            "Turbidity_high": [
                f"To reduce turbidity from {value} NTU to below {threshold} NTU, add alum to coagulate, then filter. Use a turbidity meter to confirm clarity.",
                f"To clear turbidity from {value} NTU to below {threshold} NTU, use a flocculant, let it settle, and filter. Verify with a turbidity sensor."
            ]
        }
        issue_key = f"{parameter}_low" if "too low" in issue else f"{parameter}_high" if "too high" in issue else f"{parameter}_high"
        return fallback_options.get(issue_key, [f"Adjust {parameter} from {value} to {threshold} with a suitable treatment."])[np.random.randint(0, 2)]

    # Dynamic prompts to encourage varied phrasing
    prompt_base = {
        "ph_low": f"Write a 3-sentence paragraph on increasing the pH of water from {value} to {threshold}. Use creative phrasings to describe adding a base (e.g., calcium hydroxide, sodium carbonate) and testing with a pH tool to reach 6.5–8.5. Focus only on water quality adjustment.",
        "ph_high": f"Write a 3-sentence paragraph on decreasing the pH of water from {value} to {threshold}. Use creative phrasings to describe adding an acid (e.g., phosphoric acid, vinegar) and testing with a pH device to stabilize at 6.5–8.5. Focus only on water quality adjustment.",
        "Solids_high": f"Write a 3-sentence paragraph on reducing solids in water from {value} ppm to below {threshold} ppm. Use creative phrasings to describe filtration (e.g., reverse osmosis, ultrafiltration) and maintenance checks. Focus only on water quality adjustment.",
        "Chloramines_high": f"Write a 3-sentence paragraph on reducing chloramines in water from {value} ppm to below {threshold} ppm. Use creative phrasings to describe carbon-based treatment (e.g., activated carbon, catalytic carbon) and testing methods. Focus only on water quality adjustment.",
        "Sulfate_high": f"Write a 3-sentence paragraph on reducing sulfate in water from {value} mg/L to below {threshold} mg/L. Use creative phrasings to describe ion exchange or reverse osmosis and monitoring steps. Focus only on water quality adjustment.",
        "Turbidity_high": f"Write a 3-sentence paragraph on reducing turbidity in water from {value} NTU to below {threshold} NTU. Use creative phrasings to describe coagulation or sedimentation and testing methods. Focus only on water quality adjustment."
    }
    issue_key = f"{parameter}_low" if "too low" in issue else f"{parameter}_high" if "too high" in issue else f"{parameter}_high"
    prompt = prompt_base.get(issue_key, f"Write a 3-sentence paragraph on adjusting {parameter} from {value} to {threshold}. Focus only on water quality adjustment.")

    try:
        # Generate multiple options and pick the best coherent one
        result = generator(prompt, num_return_sequences=5, max_length=150, temperature=1.2)
        for res in result:
            suggestion = res["generated_text"].replace(prompt, "").strip()
            print(f"Raw NLP Suggestion for {parameter} (attempt): {suggestion}")
            if is_coherent_and_relevant(suggestion, parameter):
                return suggestion
        raise ValueError("No coherent suggestion generated")
    except Exception as e:
        print(f"NLP generation failed for {parameter}: {e}")
        fallback_options = {
            "ph_low": [
                f"To raise the pH from {value} to {threshold}, add calcium hydroxide and mix thoroughly. Test with a pH meter, adjusting gradually to stay between 6.5 and 8.5.",
                f"To increase pH from {value} to {threshold}, use sodium carbonate with good stirring. Check levels with a pH tester to maintain 6.5–8.5."
            ],
            "ph_high": [
                f"To lower the pH from {value} to {threshold}, add diluted phosphoric acid slowly. Monitor with a pH meter to keep it between 6.5 and 8.5.",
                f"To reduce pH from {value} to {threshold}, introduce vinegar in small amounts. Verify with a pH sensor to stabilize at 6.5–8.5."
            ],
            "Solids_high": [
                f"To reduce solids from {value} ppm to below {threshold} ppm, install a reverse osmosis filter. Clean it monthly and check with a TDS meter.",
                f"To lower solids from {value} ppm to below {threshold} ppm, use an ultrafiltration system. Maintain weekly and test water quality regularly."
            ],
            "Chloramines_high": [
                f"To decrease chloramines from {value} ppm to below {threshold} ppm, use an activated carbon filter. Replace every 6 months and test with a chlorine kit.",
                f"To reduce chloramines from {value} ppm to below {threshold} ppm, install a catalytic carbon unit. Check monthly with a test strip and replace yearly."
            ],
            "Sulfate_high": [
                f"To lower sulfate from {value} mg/L to below {threshold} mg/L, use an ion exchange resin. Regenerate with salt and monitor levels regularly.",
                f"To reduce sulfate from {value} mg/L to below {threshold} mg/L, apply reverse osmosis. Maintain the system and check with a sulfate test kit."
            ],
            "Turbidity_high": [
                f"To reduce turbidity from {value} NTU to below {threshold} NTU, add alum to coagulate, then filter. Use a turbidity meter to confirm clarity.",
                f"To clear turbidity from {value} NTU to below {threshold} NTU, use a flocculant, let it settle, and filter. Verify with a turbidity sensor."
            ]
        }
        issue_key = f"{parameter}_low" if "too low" in issue else f"{parameter}_high" if "too high" in issue else f"{parameter}_high"
        return fallback_options.get(issue_key, [f"Adjust {parameter} from {value} to {threshold} with a suitable treatment."])[np.random.randint(0, 2)]

@app.route("/", methods=["GET", "POST"])
def predict():
    prediction = None
    reasons = []
    suggestions = []
    form_data = {"ph": "", "solids": "", "chloramines": "", "sulfate": "", "turbidity": ""}

    if request.method == "POST":
        print("POST request received...")
        try:
            # Get input values
            ph = float(request.form["ph"])
            solids = float(request.form["solids"])
            chloramines = float(request.form["chloramines"])
            sulfate = float(request.form["sulfate"])
            turbidity = float(request.form["turbidity"])
            print(f"Input values: ph={ph}, solids={solids}, chloramines={chloramines}, sulfate={sulfate}, turbidity={turbidity}")

            # Store form data to pre-fill
            form_data = {
                "ph": ph,
                "solids": solids,
                "chloramines": chloramines,
                "sulfate": sulfate,
                "turbidity": turbidity
            }

            # Cap and normalize pH, clip Sulfate
            ph_capped = min(max(ph, 5), 9)
            ph_normalized = (ph_capped - 5) / (9 - 5) * 0.1
            sulfate_capped = min(max(sulfate, 100), 300)
            print(f"Normalized: ph_normalized={ph_normalized}, sulfate_capped={sulfate_capped}")

            # Prepare input data
            input_data = pd.DataFrame([[ph_normalized, solids, chloramines, sulfate_capped, turbidity]],
                                      columns=feature_names)
            print("Input data prepared.")

            # Predict
            if model is not None:
                print("Making prediction...")
                prediction = model.predict(input_data)[0]
                result = "Potable" if prediction == 1 else "Not Potable"
                print(f"Prediction: {result}")
            else:
                print("No model loaded, defaulting to 'Not Potable'.")
                result = "Not Potable"

            # Store submission
            submissions.append({
                "ph": ph_capped,
                "Solids": solids,
                "Chloramines": chloramines,
                "Sulfate": sulfate_capped,
                "Turbidity": turbidity,
                "Potability": result
            })
            print("Submission stored.")

            # Reasons for non-potable
            if result == "Not Potable":
                if ph < THRESHOLDS["ph"][0]:
                    reasons.append(f"pH is too low at {ph:.1f} (should be 6.5–8.5).")
                    suggestions.append(generate_suggestion(f"pH is too low at {ph:.1f}", "pH", ph, "6.5–8.5"))
                elif ph > THRESHOLDS["ph"][1]:
                    reasons.append(f"pH is too high at {ph:.1f} (should be 6.5–8.5).")
                    suggestions.append(generate_suggestion(f"pH is too high at {ph:.1f}", "pH", ph, "6.5–8.5"))
                if solids > THRESHOLDS["Solids"][1]:
                    reasons.append(f"Solids are too high at {solids:.1f} ppm (should be below 10000 ppm).")
                    suggestions.append(generate_suggestion(f"Solids are too high at {solids:.1f} ppm", "Solids", solids, "10000"))
                if chloramines > THRESHOLDS["Chloramines"][1]:
                    reasons.append(f"Chloramines are too high at {chloramines:.1f} ppm (should be below 4 ppm).")
                    suggestions.append(generate_suggestion(f"Chloramines are too high at {chloramines:.1f} ppm", "Chloramines", chloramines, "4"))
                if sulfate > THRESHOLDS["Sulfate"][1]:
                    reasons.append(f"Sulfate is too high at {sulfate:.1f} mg/L (should be below 250 mg/L).")
                    suggestions.append(generate_suggestion(f"Sulfate is too high at {sulfate:.1f} mg/L", "Sulfate", sulfate, "250"))
                if turbidity > THRESHOLDS["Turbidity"][1]:
                    reasons.append(f"Turbidity is too high at {turbidity:.1f} NTU (should be below 5 NTU).")
                    suggestions.append(generate_suggestion(f"Turbidity is too high at {turbidity:.1f} NTU", "Turbidity", turbidity, "5"))
                print(f"Reasons: {reasons}, Suggestions: {suggestions}")

            return render_template(
                "index.html",
                prediction=result,
                reasons=reasons,
                suggestions=suggestions,
                form_data=form_data
            )

        except ValueError as ve:
            print(f"ValueError: {ve}")
            return render_template(
                "index.html",
                prediction=None,
                reasons=["Invalid input. Please enter valid numbers."],
                suggestions=[],
                form_data=form_data
            )
        except Exception as e:
            print(f"Unexpected error: {e}")
            return render_template(
                "index.html",
                prediction=None,
                reasons=[f"An error occurred: {e}"],
                suggestions=[],
                form_data=form_data
            )

    return render_template("index.html", prediction=None, reasons=[], suggestions=[], form_data=form_data)

if __name__ == "__main__":
    app.run(debug=True)