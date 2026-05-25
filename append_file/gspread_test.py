import gspread

gc = gspread.oauth(credentials_filename='credentials.json')

sh = gc.open("QC_PARAM")

if __name__ == "__main__":
    print(sh.sheet1.get('A1'))
    print(sh.worksheets())
