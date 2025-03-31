# 🏃🚴‍♂️🏊 Strava Training Dashboard

**Visualize your Strava activities like never before with this fully interactive Streamlit dashboard.**  
Whether you're a runner, cyclist, swimmer—or just a data-loving athlete—this tool helps you explore your training with clarity and style.

---

## 🔍 Overview

This dashboard turns your raw Strava export into an intuitive visual story of your fitness.  
You can analyze patterns, track performance, and celebrate achievements across Running, Cycling, and Swimming.

**Key Features:**
- 📊 General overview across all sports
- 🏃 Dedicated tabs for Running, Swimming, and Cycling
- 📅 Activity heatmaps by month or week
- 📈 Cumulative distance/time tracking
- 📍 Scatter plots (pace vs. distance, speed vs. distance...)
- ❤️‍🔥 Heart rate distribution histograms
- 🥇 Personal bests: top 3 longest and fastest workouts
- 🎛️ Filters: time range, activity type, metrics, and more

---

## 📁 How to Use

### 1. Export your Strava data
- Go to [Strava Settings → My Account → Download or Delete Your Account](https://www.strava.com/settings/account)
- Request your archive and unzip the `.zip`
- Look for the file called `activities.csv`

### 2. Run the app locally

```bash
git clone https://github.com/alexgasconn/Strava-dashboard.git
cd Strava-dashboard
pip install -r requirements.txt
streamlit run app.py
```

### 3. Upload your `activities.csv` via the sidebar

Once uploaded, the dashboard will automatically display your training data.

---

## 📸 Dashboard Preview

<img src="https://github.com/alexgasconn/Strava-dashboard/raw/main/assets/preview_general.png" width="100%" />
<img src="https://github.com/alexgasconn/Strava-dashboard/raw/main/assets/preview_running.png" width="100%" />
<img src="https://github.com/alexgasconn/Strava-dashboard/raw/main/assets/preview_swimming.png" width="100%" />
<img src="https://github.com/alexgasconn/Strava-dashboard/raw/main/assets/preview_cycling.png" width="100%" />

> *(Add actual images in `/assets` or use relative paths as needed.)*

---
## 🌐 Online view
- [Dashboard](https://triathlon-dashboard.streamlit.app/) – Online tool

## 🧠 Technologies

- [Streamlit](https://streamlit.io/) – interactive UI
- [Pandas](https://pandas.pydata.org/) – data wrangling
- [Altair](https://altair-viz.github.io/) – beautiful charts
- [Plotly](https://plotly.com/) – optional interactive graphs

---

## ✨ Dashboard Sections

### 📍 General Tab
- Activity heatmap (monthly/weekly)
- Pie chart of sport distribution
- Total stats summary by sport
- Flexible metric and time granularity selector
- Multi-year/month cumulative line plots

### 🏃 Running Tab
- Pace vs. distance scatterplot (color: HR)
- Heart rate histogram
- Cumulative training time graph
- Distance distribution
- Top 3 longest & fastest runs
- Weekly rolling mileage chart

### 🏊 Swimming Tab
- Pace (per 100m) vs. distance scatterplot
- HR distribution
- Monthly cumulative training curve
- Distance distribution
- Longest & fastest swims
- Rolling weekly swim load

### 🚴 Cycling Tab
- Speed vs. distance scatterplot
- HR histogram
- Cumulative hours on the saddle
- Distance histogram
- Top 3 longest rides & most elevation
- Weekly cycling load graph

---

## 🧩 Customization

Feel free to customize or expand:
- Add new sport categories
- Integrate elevation, power, cadence
- Build comparisons across timeframes
- Deploy to the cloud (Streamlit Cloud, HuggingFace, etc.)

---

## 💬 Credits

Built with ❤️ by [@alexgasconn](https://github.com/alexgasconn)

---

## 📢 License

This project is open-source under the MIT License.  
Use it, fork it, improve it—and share it with your training group.
