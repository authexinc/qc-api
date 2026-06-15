# import sqlalchemy
from sqlalchemy import Boolean, create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv('POSTGRES'))
Base = declarative_base()
Session = sessionmaker(bind=engine)


class ChartData(Base):
    __tablename__ = 'chart_values'

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime, unique=True)
    algo_state = relationship("AlgoState", back_populates="chart_data", uselist=False)

    # ------ OHLCv Data ------
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)

    # # ______ EMA Values ______
    # # ------ EMA 1min & MTE & 10min200 ------
    ema_1min = Column(Float)
    ema_middle = Column(Float)
    mte_1 = Column(Float)
    mte_2 = Column(Float)
    mte_3 = Column(Float)
    mte_4 = Column(Float)
    ema_10_min_200 = Column(Float)

    # # ------ LTE ------
    lte_1 = Column(Float)
    lte_2 = Column(Float)

    # # ------ MTE1 Levels 1-10 ------
    # mte1_L10 = Column(Float)
    # mte1_L9 = Column(Float)
    # mte1_L8 = Column(Float)
    # mte1_L7 = Column(Float)
    # mte1_L6 = Column(Float)
    # mte1_L5 = Column(Float)
    # mte1_L4 = Column(Float)
    # mte1_L3 = Column(Float)
    # mte1_L2 = Column(Float)
    # mte1_L1 = Column(Float)

    # # ------ MTE4 Levels L5 to -L5 ------
    # mte4_L5 = Column(Float)
    # mte4_L4 = Column(Float)
    # mte4_L3 = Column(Float)
    # mte4_L2 = Column(Float)
    # mte4_L1 = Column(Float)
    # mte4_L0 = Column(Float)
    # mte4_nL1 = Column(Float)
    # mte4_nL2 = Column(Float)
    # mte4_nL3 = Column(Float)
    # mte4_nL4 = Column(Float)
    # mte4_nL5 = Column(Float)

    # ------ Anchored EMAs ------
    ema_1min_A = Column(Float)
    ema_Middle_A = Column(Float)
    ema_4min_100_A = Column(Float)
    ema_4min_300_A = Column(Float)

    # ------ Remaining EMAs ------
    ema_1min_60 = Column(Float)
    ema_3min_80 = Column(Float)
    ema_4min_100 = Column(Float)
    ema_4min_200 = Column(Float)
    ema_4min_300 = Column(Float)
    ema_30min_750 = Column(Float)
    ema_30min_2000 = Column(Float)
    ema_30min_2500 = Column(Float)


class AlgoState(Base):
    __tablename__ = 'algo_state'
    
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime, ForeignKey('chart_values.datetime'))
    chart_data = relationship("ChartData", back_populates="algo_state")

    # state = Column(String(250))
    # gap = Column(String(250))
    # strategy = Column(String(250))
    # current_mte_type = Column(String(250))
    # current_mte_val = Column(Float)
    # next_mte = Column(String(250))
    # next_mte_val = Column(Float)
    # current_bie_val = Column(Float)
    # main_flow_state = Column(String(250))
    # highest_sl_ema_type = Column(String(250))
    # highest_sl_ema_val = Column(Float)
    one_min_high_val = Column(Float)
    buy_in_price = Column(Float)
    sell_price = Column(Float)
    one_min_high_G = Column(Float)
    gap_price = Column(Float)
    current_state = Column(String(250))
    # debs_main_buy_ok = Column(Boolean)
    # debs_main_sell_ok = Column(Boolean)
    # ema2min_buy_state = Column(String(250))
    # ema2min_sell_state = Column(String(250))
    # gap_up_ema = Column(Float)
    # gap_down_ema = Column(Float)
    # gbp = Column(Float)
    # gsp = Column(Float)
    # invested = Column(Boolean)
    
    
    
if __name__ == "__main__":
    Base.metadata.create_all(engine)
