USE DATABASE COLLEGE_TRANSPORT;
USE SCHEMA RAW;

-- Create file format for CSV
CREATE OR REPLACE FILE FORMAT csv_format
  TYPE = CSV
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  NULL_IF = ('NULL', 'null', '')
  EMPTY_FIELD_AS_NULL = TRUE
  FIELD_OPTIONALLY_ENCLOSED_BY = '"';

-- Create internal stage
CREATE OR REPLACE STAGE transport_data_stage
  FILE_FORMAT = csv_format;

-- COPY INTO statements (Note: Requires data to be PUT into the stage first)
COPY INTO STUDENTS FROM @transport_data_stage/students.csv.gz;
COPY INTO BUSES FROM @transport_data_stage/buses.csv.gz;
COPY INTO STOPS FROM @transport_data_stage/stops.csv.gz;
COPY INTO BUS_USAGE FROM @transport_data_stage/bus_usage.csv.gz;
COPY INTO COMPLAINTS FROM @transport_data_stage/complaints.csv.gz;
