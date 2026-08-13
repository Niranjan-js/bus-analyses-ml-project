# ☁️ Snowflake Setup Guide

## Step 1: Create a Free Snowflake Account

1. Go to [signup.snowflake.com](https://signup.snowflake.com)
2. Sign up for a **30-day free trial**
3. Choose:
   - **Cloud Provider**: Any (AWS recommended)
   - **Region**: Closest to you
   - **Edition**: Standard (free)
4. Verify your email and log in

## Step 2: Your Snowflake Account

Your Snowflake account identifier: `QEJHMZX-GXB17254`
Your Snowflake URL: `https://QEJHMZX-GXB17254.snowflakecomputing.com`

## Step 3: Run SQL Scripts

Open a **Snowflake Worksheet** and run these scripts in order:

### 3.1 Database Setup
Open `sql/01_database_setup.sql` and run it.
This creates the `COLLEGE_TRANSPORT` database with `RAW` and `ANALYTICS` schemas.

### 3.2 Create Tables
Open `sql/02_create_tables.sql` and run it.
This creates all 5 tables: STUDENTS, BUSES, STOPS, BUS_USAGE, COMPLAINTS.

### 3.3 Load Data

**Option A: Using Snowsight UI (Easiest)**

1. In Snowsight, go to **Data** → **Databases** → **COLLEGE_TRANSPORT** → **RAW**
2. Click on each table → **Load Data**
3. Upload the corresponding CSV file from the `data/` folder
4. Set **Header rows to skip** = 1
5. Click **Load**

Repeat for all 5 tables:
- `students.csv` → `STUDENTS`
- `buses.csv` → `BUSES`
- `stops.csv` → `STOPS`
- `bus_usage.csv` → `BUS_USAGE`
- `complaints.csv` → `COMPLAINTS`

**Option B: Using SQL Stage**

Run `sql/03_load_data.sql` after uploading CSVs to the internal stage.

### 3.4 Validate Data

Run these queries to verify data loaded correctly:

```sql
SELECT 'STUDENTS' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM RAW.STUDENTS
UNION ALL
SELECT 'BUSES', COUNT(*) FROM RAW.BUSES
UNION ALL
SELECT 'STOPS', COUNT(*) FROM RAW.STOPS
UNION ALL
SELECT 'BUS_USAGE', COUNT(*) FROM RAW.BUS_USAGE
UNION ALL
SELECT 'COMPLAINTS', COUNT(*) FROM RAW.COMPLAINTS;
```

Expected results:
| Table | Rows |
|---|---:|
| STUDENTS | 120 |
| BUSES | 6 |
| STOPS | 12 |
| BUS_USAGE | 132 |
| COMPLAINTS | 90 |

### 3.5 Create Analytics Views

Run the remaining SQL scripts in order:
- `sql/04_bus_utilization.sql`
- `sql/05_delay_analysis.sql`
- `sql/06_route_analysis.sql`
- `sql/07_complaint_analysis.sql`
- `sql/08_student_analysis.sql`
- `sql/09_stop_analysis.sql`
- `sql/10_kpi_views.sql`
- `sql/11_ai_analytics.sql`

## Step 4: Configure the App

1. Copy `.env.example` to `.env`
2. Fill in your Snowflake credentials:

```
SNOWFLAKE_ACCOUNT=QEJHMZX-GXB17254
SNOWFLAKE_USER=your_snowflake_username
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_DATABASE=COLLEGE_TRANSPORT
SNOWFLAKE_SCHEMA=RAW
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
```

3. The app will automatically connect to Snowflake when these are set.

## Step 5: Run the App

```bash
cd app
streamlit run app.py
```

## Troubleshooting

- **Connection Error**: Make sure your account identifier is correct (format: `ORGID-ACCOUNTID`)
- **Table Not Found**: Make sure you ran the SQL scripts in order
- **No Data**: Verify data loaded with the validation query above
- **App works without Snowflake**: The app falls back to local CSV files if Snowflake is not configured
