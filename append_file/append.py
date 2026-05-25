import os
from dotenv import load_dotenv
import gspread

load_dotenv()


class AppendValue():
    def __init__(self):
        self.qc = gspread.oauth(credentials_filename='credentials.json')
        self.sh = self.qc.open('QC_PARAM')
        self.ws = self.sh.sheet1
        
    # def get_file():
    #     ws.update_cell(1,1, {})
    #     pass
    
    def update_mte(self, mte):
        '''
        PARAM: MTE - FE takes pre-formatted strings, when a specific option is selected,
        this function is called and updates the MTE cell with the new value
        
        If an empty str is passed, the value is deleted and the algorithm reverts to it's default state on the next bar.
        '''
        
        self.ws.update_cell(2,1, mte)
        # val = self.ws.cell(1,2).value
        # val = self.ws.col_values(1)
        # val1 = self.ws.get_all_records()
        # return val

    def clear_mte(self):
        self.ws.update_cell(2,1, '')
        # val = self.ws.col_values(1)
        # return val
    
    def update_ste(self, ste):
        '''
        PARAM: MTE - FE takes pre-formatted strings, when a specific option is selected,
        this function is called and updates the MTE cell with the new value
        
        If an empty str is passed, the value is deleted and the algorithm reverts to it's default state on the next bar.
        '''
        self.ws.update_cell(2,2, ste)
        # val = self.ws.cell(2,2).value
        # val = self.ws.col_values(2)
        # val1 = self.ws.get_all_records()
        # return val
    
    
    def clear_ste(self):
        self.ws.update_cell(2,2, '')
        # val = self.ws.col_values(2)
        # return val

if __name__ == "__main__":
    print(AppendValue().clear_ste())
    
