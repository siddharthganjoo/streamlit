import streamlit as st
# import jsonlines
import pandas as pd
# import matplotlib.pyplot as plt
# Translation mapping for outlier region labels
translation_map = {
   "Bloed": "Blood",
   "Eigeel": "Yolk",
   "Mest": "Feces",
   "Kneus": "Bruised",
   "Openbreuk": "OpenCrack",
   "Scheur": "Crack",
   "Rimpel": "Wrinkle",
   "Veer": "Feather",
   "Kalkspot": "CalciumSpot",
   "Stof": "Dust",
   "groep_Vervuild": "Group_Dirty",
   "groep_Beschadigd": "Group_Damaged",
   "groep_Schaalafwijking": "Group_ShellDeviation"
}
# Thresholds for each label
thresholds = {
   "Blood": 80,
   "Yolk": 120,
   "Feces": 130,
   "Bruised": 20,
   "OpenCrack": 20,
   "Crack": 175,
   "Wrinkle": 6500,
   "Feather": 100,
   "CalciumSpot": 100,
   "Dust": 150,
   "Group_Dirty": 20,
   "Group_Damaged": 20,
   "Group_ShellDeviation": 1000
}
# Streamlit UI
st.title("FN Analysis of Egg Batch")
st.write("Upload a JSONL file to analyze egg data against predefined thresholds.")
# File uploader
uploaded_file = st.file_uploader("Choose a JSONL file", type="jsonl")
if uploaded_file is not None:
   try:
       # Read and parse the JSONL file
       data = []
       with jsonlines.Reader(uploaded_file) as reader:
           for line in reader:
               if isinstance(line, list):
                   # Translate labels and construct a dictionary for each egg
                   egg_data = {translation_map.get(item['Label'], item['Label']): item['Value'] for item in line}
                   data.append(egg_data)
               else:
                   st.error("Each line in the JSONL file must be a list of dictionaries.")
                   st.stop()
       if not data:
           st.error("The uploaded file is empty or not in the expected format.")
       else:
           # Create a DataFrame
           df = pd.DataFrame(data)
           # Display the DataFrame
           st.subheader("Uploaded Data")
        #    st.dataframe(df)
           # Count total eggs
           total_eggs = len(df)
           # Initialize counters
           negatives_count = 0
           fn_counts = {f"{pct}%": 0 for pct in range(1, 11)}
           # Analyze each egg
           for _, row in df.iterrows():
               max_deviation = 0
               is_negative = False
               # Calculate the maximum deviation for this egg
               for label, threshold in thresholds.items():
                   value = row.get(label, 0)
                   deviation = ((value - threshold) / threshold) * 100
                   # If any label exceeds the threshold, it's a negative
                   if deviation > 0:
                       is_negative = True
                       max_deviation = max(max_deviation, deviation)
               # Count negatives
               if is_negative:
                   negatives_count += 1
               # Categorize the egg by its maximum deviation for FN
               for pct in range(1, 11):
                   if max_deviation > 0 and max_deviation <= pct:
                       fn_counts[f"{pct}%"] += 1
                       break  # Count each egg only once
           # Calculate FN percentages
           fn_percentages = {key: (count / total_eggs) * 100 for key, count in fn_counts.items()}
           fn_negatives_percentage = {key: (count / negatives_count) * 100 for key, count in fn_counts.items()}
           # Display Negatives Count
           st.write("### Negatives Count")
           st.metric(label="Total Negatives", value=negatives_count)
           st.metric(label="Negatives/Total Eggs (%)", value=f"{(negatives_count / total_eggs) * 100:.2f}%")
           # Display FN counts and percentages
        #    st.write("### FN Counts and Percentages")
        #    fn_df = pd.DataFrame({
        #        "FN Count": list(fn_counts.values()),
        #        "FN Percentage (Total Eggs)": list(fn_percentages.values()),
        #        "FN Percentage (Negatives)": list(fn_negatives_percentage.values())
        #    }, index=fn_counts.keys())
        #    st.table(fn_df)
        #    # Visualize FN Counts by Percentage Deviation
        #    st.write("### FN Counts by Percentage Deviation")
        #    fig, ax = plt.subplots()
        #    ax.bar(fn_counts.keys(), fn_counts.values(), color='tomato')
        #    ax.set_xlabel('Percentage Above Threshold')
        #    ax.set_ylabel('FN Count')
        #    ax.set_title('False Negatives by Percentage Deviation')
        #    st.pyplot(fig)
        #    # Visualize FN Percentage (Total Eggs)
        #    st.write("### FN Percentage of Total Eggs")
        #    fig, ax = plt.subplots()
        #    ax.bar(fn_percentages.keys(), fn_percentages.values(), color='dodgerblue')
        #    ax.set_xlabel('Percentage Above Threshold')
        #    ax.set_ylabel('FN Percentage (%)')
        #    ax.set_title('FN Percentage of Total Eggs')
        #    st.pyplot(fig)
        #    # Visualize FN Percentage (Negatives)
        #    st.write("### FN Percentage of Negatives")
        #    fig, ax = plt.subplots()
        #    ax.bar(fn_negatives_percentage.keys(), fn_negatives_percentage.values(), color='green')
        #    ax.set_xlabel('Percentage Above Threshold')
        #    ax.set_ylabel('FN/Negatives (%)')
        #    ax.set_title('FN Percentage of Negatives')
        #    st.pyplot(fig)
        #    # Display overall FN Ratios
        #    st.write("### Overall FN Ratios")
        #    overall_fn_count = sum(fn_counts.values())
        #    overall_fn_total_percentage = (overall_fn_count / total_eggs) * 100
        #    overall_fn_negatives_percentage = (overall_fn_count / negatives_count) * 100
        #    st.metric(label="Total FNs", value=overall_fn_count)
        #    st.metric(label="FN/Total Eggs (%)", value=f"{overall_fn_total_percentage:.2f}%")
        #    st.metric(label="FN/Negatives (%)", value=f"{overall_fn_negatives_percentage:.2f}%")
   except Exception as e:
       st.error(f"An error occurred while processing the file: {e}")


# Cumulative FN Analysis (Numbers Only)
st.subheader("Cumulative False Negative (FN) Analysis (Numbers Only)")
# Initialize counters
negatives_indices = set()
fn_counts = {f"{pct}%": 0 for pct in range(1, 11)}
cumulative_fn_counts = {f"{pct}%": 0 for pct in range(1, 11)}
# Count total eggs
total_eggs = len(df)
# Step 1: Calculate Negatives
for idx, row in df.iterrows():
   for label, threshold in thresholds.items():
       value = row.get(label, 0)
       if value > threshold:
           negatives_indices.add(idx)
           break  # Once negative, no need to check other labels
# Total Negatives
negatives_count = len(negatives_indices)
# Step 2: Calculate FNs from Negatives Only
for idx in negatives_indices:
   row = df.loc[idx]
   max_deviation = 0
   # Calculate the maximum deviation for this egg
   for label, threshold in thresholds.items():
       value = row.get(label, 0)
       deviation = ((value - threshold) / threshold) * 100
       # Only consider positive deviations (i.e., exceeding the threshold)
       if deviation > 0:
           max_deviation = max(max_deviation, deviation)
   # Categorize the egg by its maximum deviation for FN
   for pct in range(1, 11):
       if max_deviation > 0 and max_deviation <= pct:
           fn_counts[f"{pct}%"] += 1
           break  # Count each egg only once
# Step 3: Calculate Cumulative FN Counts
cumulative_sum = 0
for pct in range(1, 11):
   pct_key = f"{pct}%"
   cumulative_sum += fn_counts[pct_key]
   cumulative_fn_counts[pct_key] = cumulative_sum
# Calculate Cumulative FN Percentages
fn_percentages = {key: (count / total_eggs) * 100 for key, count in cumulative_fn_counts.items()}
fn_negatives_percentage = {key: (count / negatives_count) * 100 for key, count in cumulative_fn_counts.items()}
# Display Cumulative FN Counts and Percentages
st.write("### Cumulative FN Counts and Percentages")
fn_df = pd.DataFrame({
   "Cumulative FN Count": list(cumulative_fn_counts.values()),
   "Cumulative FN Percentage (Total Eggs)": list(fn_percentages.values()),
   "Cumulative FN Percentage (Negatives)": list(fn_negatives_percentage.values())
}, index=cumulative_fn_counts.keys())
st.table(fn_df)
# Display Logical Note
st.info("""
**How Cumulative FN is Calculated:**
- The count for each percentage bin includes all eggs from lower bins as well.
- For example:
   - `1%` → Eggs just above the threshold but not exceeding `1%`.
   - `2%` → All eggs from `1%` plus eggs between `1%` and `2%`.
   - `3%` → All eggs from `2%` plus eggs between `2%` and `3%`.
- This shows the cumulative count of eggs within each deviation range.
- Each egg is counted only once under its highest deviation bin.
- The numbers are cumulative but distinct, meaning no double counting.
""")
# Display overall Cumulative FN Ratios
st.write("### Overall Cumulative FN Ratios")
overall_fn_count = sum(fn_counts.values())
overall_fn_total_percentage = (overall_fn_count / total_eggs) * 100
overall_fn_negatives_percentage = (overall_fn_count / negatives_count) * 100
st.metric(label="Total Cumulative FNs", value=overall_fn_count)
st.metric(label="Cumulative FN/Total Eggs (%)", value=f"{overall_fn_total_percentage:.2f}%")
st.metric(label="Cumulative FN/Negatives (%)", value=f"{overall_fn_negatives_percentage:.2f}%")
