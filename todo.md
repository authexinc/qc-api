Build CMTE/SL update shit {cm:2026-05-23}
Finish algo actions {cm:2026-05-22}
Finish append.py {cm:2026-05-23}
Find solution for file imports from another dir {cm:2026-05-23}
For parse_data(), split list by ":" into two lists, then use this to create a dict. {cm:2026-05-23} - This will allow for easy API outputs {cm:2026-05-23}
Create input params in the API endpoint {cm:2026-05-23}
Modify the dataframe to have an empty cell instead of NaN if no param is passed {cm:2026-05-23}
Add logic for the update endpoints to accept empty strings to clear values {cm:2026-05-23}
Strip the whitespace in "value" in the output dict {cm:2026-05-24}

Need to paramaterize Project/AlgorithmID so it can be passed in the API call

Create db file {cm:2026-05-25}

TV DataFeed

Every time log data is called, add values to db {cm:2026-05-28}

Fix the log list index in parse_data() to capture all values {cm:2026-05-28}

## For DB, need to convert datetime to proper datetime format and use that as the key {cm:2026-05-28}

For the output - JSON containing OHLC, ema values - JSON containing meta data like invested, p&l, equity, etc.

Strip dollar sign from OHLC, MTE, EMAs, LTEs {cm:2026-05-28}

split the logs by "#" {cm:2026-05-28}

Add a table for algo state and link using datetime {cm:2026-05-28}

Add db append checks {cm:2026-05-28}

Add the top metadata bar to algo stats

Add order table