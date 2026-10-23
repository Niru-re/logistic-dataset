

# 🥫 Food Expiry Days Prediction using Machine Learning
---

## 📌 Abstract

Food waste and spoilage are significant global challenges that affect both the economy and public health. Traditional **expiry dates** printed on food packages are static and fail to reflect **real-world conditions**, such as variations in storage temperature, packaging type, or the presence of preservatives.

This project leverages **machine learning**, specifically the **Random Forest Regressor**, to predict the **number of days a food item remains safe to consume**. By analyzing historical data for different food types, storage methods, and preservatives, the model provides **dynamic, data-driven predictions** that can reduce waste, optimize inventory, and enhance food safety.

**Primary Goals:**

* Reduce **food waste** by providing accurate expiry predictions
* Improve **consumer safety** and minimize foodborne illness risks
* Support **retailers and supply chains** in better inventory management

---

## 📖 Introduction

### Problem Statement

Many consumers and businesses rely on **static expiry dates**, which may overestimate or underestimate actual shelf life. Incorrect assumptions can lead to:

* **Premature disposal** of still-safe food → waste and economic loss
* **Consumption of spoiled food** → potential health hazards

A **dynamic, predictive model** can help address these issues by considering multiple variables that affect food shelf life.

### Solution Overview

* Utilize historical food data, including **food type, packaging, storage temperature, and preservatives**.
* Train a **Random Forest Regressor** to understand complex relationships between these features and actual expiry.
* Predict **expiry days** for new items or conditions, offering more reliable insights than static labels.

---

## 📂 Dataset

The dataset contains both **categorical** and **numerical** features.

| Feature               | Description                                          |
| --------------------- | ---------------------------------------------------- |
| `Food_type`           | Type of food (Snack, Fruit, Bakery, Vegetable, etc.) |
| `Packaging`           | Type of packaging (Vacuum, Glass, Paper, etc.)       |
| `Storage_temperature` | Temperature in °C at which food is stored            |
| `Preservatives`       | Whether preservatives are used (`Yes` / `No`)        |
| `Expiry_days`         | **Target variable** – number of days before expiry   |

### 🔹 Example Records

| Food_type | Packaging | Storage_temperature | Preservatives | Expiry_days |
| --------- | --------- | ------------------- | ------------- | ----------- |
| Snack     | Vacuum    | 17                  | No            | 203         |
| Fruit     | Vacuum    | 7                   | No            | 5           |
| Bakery    | Glass     | 21                  | No            | 4           |
| Snack     | Paper     | 3                   | Yes           | 68          |
| Vegetable | Paper     | 10                  | No            | 2           |

**Observations:**

* Different **food types** have significantly varying shelf lives.
* **Storage temperature** and **packaging** have a noticeable impact on expiry.
* Presence of **preservatives** generally increases shelf life.

---

## ⚙️ Data Preprocessing

Proper data preprocessing is essential to build an **accurate machine learning model**.

1. **Handling Missing Values:**

   * Missing categorical data is replaced with the **most frequent value (mode)**.
   * Ensures no null values exist during model training.

2. **Encoding Categorical Variables:**

   * Columns like `Food_type`, `Packaging`, and `Preservatives` are converted to numeric codes using **Label Encoding**.
   * Machine learning models require numerical input.

3. **Splitting Dataset:**

   * Data is divided into **training (80%)** and **testing (20%)** sets.
   * Training set → used to build the model
   * Testing set → used to evaluate model performance on unseen data

---

## 🤖 Model: Random Forest Regressor

**Why Random Forest?**

* An **ensemble learning technique** that combines multiple decision trees.
* Each tree makes a prediction; the final output is the **average** of all trees’ predictions.
* Captures **complex non-linear relationships** between features and the target.
* Handles both **categorical and numerical features**.
* **Reduces overfitting** compared to a single decision tree.

**Key Parameters Used:**

* `n_estimators=100` → Number of trees in the forest
* `random_state=42` → Ensures reproducibility
* Can be tuned further for better performance

---

## 📊 Model Evaluation

| Metric       | Value | Description                                                          |
| ------------ | ----- | -------------------------------------------------------------------- |
| **MAE**      | 6.21  | Average absolute difference between predicted and actual expiry days |
| **MSE**      | 96.70 | Penalizes larger errors more than smaller errors                     |
| **R² Score** | 0.69  | Explains ~70% of variance in expiry prediction                       |

**Interpretation:**

* On average, the model is **off by ~6 days**, which is reasonable for most applications.
* Explains most variability, making it a **reliable predictive tool**.

---

## 🧑‍💻 Example Usage

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Load dataset
data = pd.read_csv("food_expiry_dataset.csv")

# Encode categorical variables
label_encoder = LabelEncoder()
for col in ["Food_type", "Packaging", "Preservatives"]:
    data[col] = label_encoder.fit_transform(data[col])

# Features & target
X = data.drop("Expiry_days", axis=1)
y = data["Expiry_days"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train Random Forest model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict & evaluate
y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("MSE:", mean_squared_error(y_test, y_pred))
print("R² Score:", r2_score(y_test, y_pred))
```

---

## 🔄 Workflow Diagram

Raw Data (CSV)
      │
      ▼
Data Preprocessing
(Missing Values + Label Encoding)
      │
      ▼
Train-Test Split
      │
      ▼
Random Forest Regressor
      │
      ▼
Predictions (Expiry Days)
      │
      ▼
Evaluation (MAE, MSE, R²)



**Pipeline Steps:**

1. **Raw Data** → CSV file with historical food information
2. **Preprocessing** → Handle missing values + encode categorical features
3. **Train-Test Split** → Prepare data for training and evaluation
4. **Model Training** → Random Forest learns patterns from training data
5. **Prediction** → Generate expiry day predictions for new inputs
6. **Evaluation** → Assess performance with MAE, MSE, and R²

---

## 📌 Key Takeaways

* Provides **dynamic, data-driven expiry predictions**
* Helps **reduce food waste** and optimize inventory management
* Supports **consumer safety** and prevents foodborne illnesses
* Flexible enough to incorporate **additional features** like humidity, sunlight exposure, or storage method in future iterations

---

## 📂 Future Enhancements

1. Include **environmental features** like humidity and sunlight exposure.
2. Compare performance with **Gradient Boosting or XGBoost Regressors**.
3. Deploy as a **web or mobile app** for **real-time expiry predictions**.
4. Integrate **IoT sensors** in storage facilities for continuous data collection.

---


