import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.title("📅 My Irrigation Scheduling App 📱")

###############################################################################
# Connect to Google Drive before this cell
path = '/content/drive/MyDrive/Copy of AWDN_ET_Memphis4N_2021.csv'
df = pd.read_csv(path)

###############################################################################
# Organize and reformat the date columns for streamlit dropdown selection
df['Date_String'] = df['Year'].astype(str) + '-' + df['Month'].astype(str) + '-' + df['Date'].astype(str)
df['Date_YMD'] = pd.to_datetime(df['Date_String'], format='%Y-%m-%d')
df['Month'] = df['Date_YMD'].dt.strftime('%B')
df['Day'] = df['Date_YMD'].dt.day
df.drop('Date_String', axis=1, inplace=True)
df.drop('Date', axis=1, inplace=True)
df.drop('Time', axis=1, inplace=True)
df = df.reindex(columns=['Date_YMD', 'Day'] + [col for col in df.columns if col not in ['Date_YMD', 'Day']])

df.insert(6, 'Temp_Avg', (df['Temperature_High_F'] + df['Temperature_Low_F'])/2)
df.insert(13, 'Precip_Cum', df['Precipitation_inches'].cumsum())
df.insert(14, 'ET_Cum', df['ET_inches'].cumsum())

fig1, ax1 = plt.subplots()

# Precipitation data (bar and line)
ax1.bar(df.index, df['Precipitation_inches'], label='daily precipitation', color='green')
ax1.plot(df['Precip_Cum'], label='cumulative precipitation', color='blue')
ax1.set_xlabel('Day in a year')
ax1.set_ylabel('Precipitation (inches)', color='green')
ax1.tick_params(axis='y', labelcolor='green')
# ax1.set_ylim(bottom=0)  # Set lower limit of y-axis to 0 for ax1
ax1.set_ylim(0, 60)
ax1.set_xlim(0, 400)

# Create a second y-axis (ax2) sharing the same x-axis
ax12 = ax1.twinx()

# ET data (lines)
ax12.plot(df.index, df['ET_Cum'], label='cumulative ET', color='red')
ax12.plot(df.index, df['ET_inches'], label='daily ET', color='orange')
ax12.set_ylabel('ET (inches)', color='red')
ax12.tick_params(axis='y', labelcolor='red')
# ax12.set_ylim(bottom=0)  # Set lower limit of y-axis to 0 for ax2
ax12.set_ylim(0, 60)
ax12.set_xlim(0, 400)

# Title and legend
plt.title('Daily & Cumulative Precipitation and ET')
fig1.legend(loc="upper left", bbox_to_anchor=(0,1), bbox_transform=ax1.transAxes)

ax1.grid(True)  # Turn on grid for ax1 (precipitation)
ax12.grid(True)  # Turn on grid for ax2 (ET)

plt.show()
# st.pyplot(fig1)


##############################################################################
# Irrigation decision making block here
# Goal is to add a 'Decision' column to the 'selected_day_data' dataframe for irrigate or not (0 or 1 inch)
# Basic irrigation scheduling:

df['Irrigation_daily'] = 0 # All zero elements
df['Irrigation_Cum'] = 0 # All zero elements

for i in range(len(df)):
  if i == 0:
    continue

  # a = df.iloc[i]['ET_Cum'] # not recommended
  a = df.loc[df.index[i], 'ET_Cum'] # recommended way https://pandas.pydata.org/docs/user_guide/10min.html#selection-by-label
  # b = df.iloc[i]['Precip_Cum']+df.iloc[i]['Irrigation_Cum'] # not recommended
  b = df.loc[df.index[i], 'Precip_Cum'] + df.loc[df.index[i-1], 'Irrigation_Cum']
  # if not using [i-1] but [i], the code would work only if using cumsum() below instead of sum()

  if a >= (b+1):
    # df.iloc[i]['Irrigation_daily'] = 1
    df.loc[df.index[i], 'Irrigation_daily'] = 1
    # print('irrigate 1 inch on day ', df.index[i])
  else:
    # df.iloc[i]['Irrigation_daily'] = 0
    df.loc[df.index[i], 'Irrigation_daily'] = 0 # Actually no need to have the "else" as Irrigation_daily is already all zeros

  # df['Irrigation_Cum'] = df['Irrigation_daily'].cumsum()
  df.loc[df.index[i], 'Irrigation_Cum'] = df['Irrigation_daily'].sum()
  # end of the for loop

df.insert(17, 'Irrig_Precip_Cum', (df['Precip_Cum'] + df['Irrigation_Cum']))

## Second graph of Cumulative Precipitation & Irrigation VS. ET

fig2, ax21 = plt.subplots()

# Precipitation data (bar and line)
ax21.plot(df.index, df['Irrig_Precip_Cum'], label='Sum of precipitation & irrigation', color='blue')
ax21.bar(df.index, df['Irrigation_daily'], label='Daily irrigation', color='green')
ax21.bar(df.index, df['Precipitation_inches'], label='Daily precipitation', color='orange')
ax21.set_xlabel('Day in a year')
ax21.set_ylabel('inches', color='blue')
ax21.tick_params(axis='y', labelcolor='blue')
# ax21.set_ylim(bottom=0)  # Set lower limit of y-axis to 0 for ax1
ax21.set_ylim(0, 60)
ax21.set_xlim(0, 400)

# Create a second y-axis (ax2) sharing the same x-axis
ax22 = ax21.twinx()

# ET data (lines)
ax22.plot(df.index, df['ET_Cum'], label='cumulative ET', color='red')
# ax22.plot(df.index, df['ET_inches'], label='daily ET', color='orange')
ax22.set_ylabel('ET (inches)', color='red')
ax22.tick_params(axis='y', labelcolor='red')
# ax22.set_ylim(bottom=0)  # Set lower limit of y-axis to 0 for ax2
ax22.set_ylim(0, 60)
ax22.set_xlim(0, 400)

# Title and legend
plt.title('Cumulative Precipitation & Irrigation VS. ET')
fig2.legend(loc="upper left", bbox_to_anchor=(0,1), bbox_transform=ax1.transAxes)

ax21.grid(True)  # Turn on grid for ax1 (precipitation)
ax22.grid(True)  # Turn on grid for ax2 (ET)

plt.show()
# st.pyplot(fig2)


###############################################################################
# User selects month and day
selected_month = st.selectbox("Select a month:", df['Month'].unique())
filtered_df = df[df['Month'] == selected_month]
selected_day = st.selectbox("Select a day:", filtered_df['Day'].unique())
# Filter the dataframe for the selected date
selected_day_data = filtered_df[filtered_df['Day'] == selected_day].iloc[0]

# Display decision
st.subheader("Irrigation Decision")
st.write(f"For {selected_month} {selected_day}, the decision is to apply **{selected_day_data['Irrigation_daily']}** inches of irrigation.")
# st.write(f"For {selected_month} {selected_day}, the ET is: **{selected_day_data['ET_inches']}** inches, the precipitation is: **{selected_day_data['Precipitation_inches']}** inches")
st.write(f"The ET is: **{selected_day_data['ET_inches']}** inches, the precipitation is: **{selected_day_data['Precipitation_inches']}** inches today.")

st.pyplot(fig1)
st.pyplot(fig2)
