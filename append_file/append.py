import os
from dotenv import load_dotenv
import gspread

load_dotenv()


class AppendValue():
    def __init__(self):
        self._ws = None

    @property
    def ws(self):
        if self._ws is None:
            self.qc = gspread.oauth(credentials_filename='credentials.json')
            self.sh = self.qc.open('QC_PARAM')
            self._ws = self.sh.sheet1
        return self._ws

    # def get_file():
    #     ws.update_cell(1,1, {})
    #     pass

    def update_mte(self, mte):
        '''
        PARAM: MTE - FE takes pre-formatted strings, when a specific option is selected,
        this function is called and updates the MTE cell with the new value

        If an empty str is passed, the value is deleted and the algorithm reverts to it's default state on the next bar.
        '''

        self.ws.update_cell(2, 1, mte)
        # val = self.ws.cell(1,2).value
        # val = self.ws.col_values(1)
        # val1 = self.ws.get_all_records()
        # return val

    def clear_mte(self):
        self.ws.update_cell(2, 1, '')
        # val = self.ws.col_values(1)
        # return val

    # def update_ste(self, ste):
    #     '''
    #     PARAM: MTE - FE takes pre-formatted strings, when a specific option is selected,
    #     this function is called and updates the MTE cell with the new value

    #     If an empty str is passed, the value is deleted and the algorithm reverts to it's default state on the next bar.
    #     '''
    #     self.ws.update_cell(2,2, ste)
    #     # val = self.ws.cell(2,2).value
    #     # val = self.ws.col_values(2)
    #     # val1 = self.ws.get_all_records()
    #     # return val

    # def clear_ste(self):
    #     self.ws.update_cell(2,2, '')
    #     # val = self.ws.col_values(2)
    #     # return val

    def buy_sell(self, action: int):
        """
        PARAM: Accepts type:int (0 or 1) to set invested state.
        """

        if action not in (0, 1):
            return f'{action} is not accepted, value must be 1 or 0'
        try:
            self.ws.update_cell(2, 2, 'True' if action == 1 else 'False')
        except Exception as e:
            return f'Failed to update cell: {e}'

    def one_min_reset(self, action: int):
        """
        PARAM: Accepts type:int (0 or 1) to reset 1minHigh.
        """

        if action not in (0, 1):
            return f'{action} is not accepted, value must be 1 or 0'
        try:
            self.ws.update_cell(2, 3, 'True' if action == 1 else 'False')
        except Exception as e:
            return f'Failed to update cell: {e}'


    def one_min_G_reset(self, action: int):
        if action not in (0, 1):
            return f'{action} is not accepted, value must be 1 or 0'
        try:
            self.ws.update_cell(2, 10, 'True' if action == 1 else 'False')
        except Exception as e:
            return f'Failed to update cell: {e}'


if __name__ == "__main__":
    AppendValue().buy_sell(0)
