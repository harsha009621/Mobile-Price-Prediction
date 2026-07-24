import pandas as pd
import numpy as np
import joblib

from django.shortcuts import render,redirect
from .models import Register
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor


MODEL_PATH = "mobile_price_model.pkl"
DATA_PATH = "media\mobiles_ (1).csv"


def home(request):
    return render(request, "users/home.html")
#Register
def register(request):
    if request.method=='POST':
        name=request.POST['name']
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password==confirm_password:
            user=Register(name=name,username=username,email=email,password=password,confirm_password=confirm_password)
            user.save()
            return redirect('register_success')
        else:
            return redirect('home')
        
    return render(request,'users/register.html')

#register success
def register_success(request):
    return render(request,'users/register_success.html')

def login(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=Register.objects.filter(username=username,password=password).first()
        if user.is_approved:
            return redirect('dashboard')
        else:
            error='your account is not approved by the Admin!!'
        return render(request,'login.html',{'error':error})
    return render(request,'users/userlogin.html')

#dashboard
def dashboard(request):
    return render(request,'users/userhome.html')

# =======================
# TRAINING FUNCTION
# =======================
def training():
    df = pd.read_csv(DATA_PATH)

    # -----------------------------
    # BASIC CLEANING
    # -----------------------------
    df.columns = df.columns.str.strip()

    # Price
    df["Price_clean"] = (
        df["Price"]
        .astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    # Brand
    df["Brand"] = df["Product Name"].str.split().str[0]

    # 5G
    df["5G"] = df["Product Name"].str.contains("5G", case=False).astype(str)

    # -----------------------------
    # RAM & ROM
    # -----------------------------
    df["RAM"] = df["RAM/ROM"].str.extract(r"(\d+)\s*GB")
    df["ROM"] = df["RAM/ROM"].str.extract(r"\|\s*(\d+)\s*GB")

    df["RAM_GB"] = df["RAM"].astype(float)
    df["ROM_GB"] = df["ROM"].astype(float)

    # -----------------------------
    # DISPLAY
    # -----------------------------
    df["Display_Size_cm"] = df["Display"].str.extract(r"(\d+\.?\d*)").astype(float)
    df["Display_Quality"] = df["Display"].str.split(")").str[-1].fillna("Unknown")

    # -----------------------------
    # CAMERA
    # -----------------------------
    df["Front_Camera_Main_MP"] = (
        df["Camera"].str.extract(r"(\d+)MP\s*Front").astype(float)
    )

    df["Rear_Camera_Main_MP"] = (
        df["Camera"].str.extract(r"(\d+)MP").astype(float)
    )

    # -----------------------------
    # BATTERY
    # -----------------------------
    df["Battery"] = df["Battery"].str.extract(r"(\d+)").astype(float)

    # -----------------------------
    # RATINGS COUNT
    # -----------------------------
    df["No.of_Ratings"] = (
        df["Rating Info"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.extract(r"(\d+)")
        .astype(float)
        .fillna(0)
    )

    # -----------------------------
    # WARRANTY
    # -----------------------------
    df["Device_Warranty_Years"] = df["Warranty"].str.extract(r"(\d+)\s*Year").astype(float).fillna(0)
    df["Other_Warranty_Years"] = 0

    # -----------------------------
    # PROCESSOR CATEGORY
    # -----------------------------
    def categorize_processor(p):
        if pd.isna(p):
            return "Other"
        p = p.lower()
        if "snapdragon" in p:
            return "Snapdragon"
        elif "dimensity" in p:
            return "Dimensity"
        elif "helio" in p:
            return "Helio"
        elif "unisoc" in p:
            return "Unisoc"
        else:
            return "Other"

    df["processor_category"] = df["Processor"].apply(categorize_processor)

    # -----------------------------
    # FINAL MODEL DATA
    # -----------------------------
    categorical_cols = ["Brand", "Display_Quality", "processor_category", "5G"]
    numerical_cols = [
        "RAM_GB", "ROM_GB", "Battery", "Display_Size_cm",
        "Front_Camera_Main_MP", "Rear_Camera_Main_MP",
        "Device_Warranty_Years", "Other_Warranty_Years",
        "No.of_Ratings", "Rating"
    ]

    X = df[categorical_cols + numerical_cols]
    y = df["Price_clean"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), numerical_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols)
    ])

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", XGBRegressor(
            n_estimators=200,
            random_state=42,
            objective="reg:squarederror"
        ))
    ])

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    joblib.dump(model, MODEL_PATH)

    return {
        "mae": round(mean_absolute_error(y_test, y_pred), 2),
        "rmse": round(np.sqrt(mean_squared_error(y_test, y_pred)), 2),
        "r2": round(r2_score(y_test, y_pred), 3)
    }


# =======================
# DJANGO VIEW
# =======================
def train_view(request):
    # Default metrics (shown before training)
    metrics = {
        "mae": "-",
        "rmse": "-",
        "r2": "-"
    }
    error = None

    if request.method == "POST":
        try:
            metrics = training()   # calls full feature-engineering + training
        except Exception as e:
            error = str(e)

    return render(
        request,
        "users/training.html",
        {
            "metrics": metrics,
            "error": error
        }
    )



# def predict_price(input_data):
#     # Load trained model
#     model = joblib.load(MODEL_PATH)

#     df = pd.DataFrame([input_data])

#     # ---------- SAME FEATURE ENGINEERING ----------
#     df["5G"] = df["Product Name"].str.contains("5G", case=False).astype(str)

#     df["Brand"] = df["Product Name"].str.split().str[0]

#     # RAM / ROM
#     df["RAM_GB"] = df["RAM/ROM"].str.extract(r"(\d+)\s*GB").astype(float)
#     df["ROM_GB"] = df["RAM/ROM"].str.extract(r"\|\s*(\d+)\s*GB").astype(float)

#     # Display
#     df["Display_Size_cm"] = df["Display"].str.extract(r"(\d+\.?\d*)").astype(float)
#     df["Display_Quality"] = df["Display"].str.split(")").str[-1].fillna("Unknown")

#     # Camera
#     df["Front_Camera_Main_MP"] = df["Camera"].str.extract(r"(\d+)MP\s*Front").astype(float)
#     df["Rear_Camera_Main_MP"] = df["Camera"].str.extract(r"(\d+)MP").astype(float)

#     # Battery
#     df["Battery"] = df["Battery"].str.extract(r"(\d+)").astype(float)

#     # Warranty
#     df["Device_Warranty_Years"] = df["Warranty"].str.extract(r"(\d+)\s*Year").astype(float).fillna(0)
#     df["Other_Warranty_Years"] = 0

#     # Processor category
#     def categorize_processor(p):
#         if pd.isna(p):
#             return "Other"
#         p = p.lower()
#         if "snapdragon" in p:
#             return "Snapdragon"
#         elif "dimensity" in p:
#             return "Dimensity"
#         elif "helio" in p:
#             return "Helio"
#         elif "unisoc" in p:
#             return "Unisoc"
#         else:
#             return "Other"

#     df["processor_category"] = df["Processor"].apply(categorize_processor)

#     # Ratings
#     df["No.of_Ratings"] = (
#         df["Rating Info"]
#         .astype(str)
#         .str.replace(",", "", regex=False)
#         .str.extract(r"(\d+)")
#         .astype(float)
#         .fillna(0)
#     )

#     df["Rating"] = df["Rating"].astype(float)

#     # ---------- FINAL MODEL INPUT ----------
#     final_cols = [
#         "Brand",
#         "Display_Quality",
#         "processor_category",
#         "5G",
#         "RAM_GB",
#         "ROM_GB",
#         "Battery",
#         "Display_Size_cm",
#         "Front_Camera_Main_MP",
#         "Rear_Camera_Main_MP",
#         "Device_Warranty_Years",
#         "Other_Warranty_Years",
#         "No.of_Ratings",
#         "Rating"
#     ]

#     prediction = model.predict(df[final_cols])[0]
#     return round(prediction, 2)
# def predict_view(request):
#     predicted_price = None
#     error = None
#     form_data = {}

#     if request.method == "POST":
#         try:
#             form_data = request.POST.dict()  # 👈 capture entered values

#             input_data = {
#                 "Product Name": request.POST["Product_Name"],
#                 "RAM/ROM": request.POST["RAM_ROM"],
#                 "Display": request.POST["Display"],
#                 "Camera": request.POST["Camera"],
#                 "Battery": request.POST["Battery"],
#                 "Processor": request.POST["Processor"],
#                 "Warranty": request.POST["Warranty"],
#                 "Rating Info": request.POST["Rating_Info"],
#                 "Rating": request.POST["Rating"]
#             }

#             predicted_price = predict_price(input_data)

#         except Exception as e:
#             error = str(e)

#     return render(
#         request,
#         "users/prediction.html",
#         {
#             "prediction": predicted_price,
#             "error": error,
#             "form_data": form_data   # 👈 send back to template
#         }
#     )

import os
import re
import google.generativeai as genai
from django.shortcuts import render
import google.generativeai as genai

# 🔐 Hardcoded key (NOT recommended for production)
genai.configure(api_key="AIzaSyAMpg6wEYU8n-7CslNwWT3vwlLjteDPsOg")


def load_dropdown_options():
    options = {
        "product_name_options": [],
        "ram_rom_options": [],
        "display_options": [],
        "camera_options": [],
        "battery_options": [],
        "processor_options": [],
        "rating_options": [],
    }
    try:
        df = pd.read_csv(DATA_PATH)
        df.columns = df.columns.str.strip()

        def unique_values(col_name):
            if col_name not in df.columns:
                return []
            return sorted(
                {
                    str(v).strip()
                    for v in df[col_name].dropna().tolist()
                    if str(v).strip()
                }
            )

        options["product_name_options"] = unique_values("Product Name")
        options["ram_rom_options"] = unique_values("RAM/ROM")
        options["display_options"] = unique_values("Display")
        options["camera_options"] = unique_values("Camera")
        options["battery_options"] = unique_values("Battery")
        options["processor_options"] = unique_values("Processor")
        options["rating_options"] = unique_values("Rating")
    except Exception:
        # Keep form usable even if dataset is missing/corrupted.
        pass

    return options


def predict_price(input_data):

    # ----------- RAW INPUT FIELDS -----------
    product_name = input_data["Product Name"]
    ram_rom = input_data["RAM/ROM"]
    display = input_data["Display"]
    camera = input_data["Camera"]
    battery = input_data["Battery"]
    processor = input_data["Processor"]
    rating = input_data["Rating"]   # ✅ We accept it (but won't use it)

    # ----------- FEATURE ENGINEERING -----------

    is_5g = "5g" in product_name.lower()
    brand = product_name.split()[0]

    ram_match = re.search(r"(\d+)\s*GB", ram_rom)
    ram_gb = float(ram_match.group(1)) if ram_match else 0

    # ----------- GEMINI PROMPT (Rating Removed) -----------

    prompt = f"""
    You are a real-time Indian ecommerce smartphone pricing engine.

    Based on:
    - Brand: {brand}
    - Full Product Name: {product_name}
    - RAM: {ram_gb} GB
    - 5G Support: {is_5g}

    Estimate the CURRENT realistic selling price in India (2026).

    Consider:
    - Brand market positioning
    - RAM variant pricing differences
    - 5G pricing impact
    - Indian smartphone pricing trends
    - Budget / Midrange / Premium category logic

    Rules:
    - Return ONLY numeric value
    - No ₹ symbol
    - No commas
    - No explanation
    """

    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(
        prompt,
        generation_config={"temperature": 0}
    )

    if not response.text:
        raise ValueError("Empty response from Gemini")

    numbers = re.findall(r"\d+\.?\d*", response.text.strip())

    if numbers:
        return round(float(numbers[0]), 2)
    else:
        raise ValueError("Could not extract numeric price.")


def predict_view(request):

    predicted_price = None
    error = None
    form_data = {}
    dropdown_options = load_dropdown_options()

    if request.method == "POST":
        try:
            form_data = request.POST.dict()

            input_data = {
                "Product Name": request.POST["Product_Name"],
                "RAM/ROM": request.POST["RAM_ROM"],
                "Display": request.POST["Display"],
                "Camera": request.POST["Camera"],
                "Battery": request.POST["Battery"],
                "Processor": request.POST["Processor"],
                "Rating": request.POST["Rating"],  # ✅ Still accepted
            }

            predicted_price = predict_price(input_data)

        except Exception as e:
            error = str(e)

    return render(
        request,
        "users/prediction.html",
        {
            "prediction": predicted_price,
            "error": error,
            "form_data": form_data,
            **dropdown_options,
        }
    )