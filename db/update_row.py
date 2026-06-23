from .model import Session, ChartData, AlgoState, LiveStats, Order
import datetime


# def populate_chart(date_time_: datetime.datetime, open_: float, high_: float, low_: float,
#                    close_: float, volume_: int, ema_1min_: float,
#                    ema_middle_: float, mte_1_: float, mte_2_: float,
#                    mte_3_: float, mte_4_: float, ema_10_min_200_: float,
#                    lte_1_: float, lte_2_: float, mte1_L10_: float,
#                    mte1_L9_: float, mte1_L8_: float, mte1_L7_: float,
#                    mte1_L6_: float, mte1_L5_: float, mte1_L4_: float,
#                    mte1_L3_: float, mte1_L2_: float, mte1_L1_: float,
#                    mte4_L5_: float, mte4_L4_: float, mte4_L3_: float,
#                    mte4_L2_: float, mte4_L1_: float, mte4_L0_: float,
#                    mte4_nL1_: float, mte4_nL2_: float, mte4_nL3_: float,
#                    mte4_nL4_: float, mte4_nL5_: float, ema_1min_A_: float,
#                    ema_Middle_A_: float, ema_4min_100_A_: float, ema_4min_300_A_: float,
#                    ema_1min_60_: float, ema_3min_80_: float, ema_4min_100_: float,
#                    ema_4min_200_: float, ema_4min_300_: float
#                    ):

def populate_chart(
    date_time_: datetime.datetime, open_: float, high_: float, low_: float,
    close_: float, volume_: int, ema_1min_: float,
    ema_middle_: float, mte_1_: float, mte_2_: float,
    mte_3_: float, mte_4_: float, ema_10_min_200_: float,
    lte_1_: float, lte_2_: float, ema_1min_A_: float,
    ema_Middle_A_: float, ema_4min_100_A_: float, ema_4min_300_A_: float,
    ema_1min_60_: float, ema_3min_80_: float, ema_4min_100_: float,
    ema_4min_200_: float, ema_4min_300_: float, ema_30min_750_: float,
    ema_30min_2000_: float, ema_30min_2500_: float
):
    session = Session()

    try:
        new_chart_row = ChartData(datetime=date_time_, open=open_, high=high_, low=low_, close=close_,
                                  volume=volume_, ema_1min=ema_1min_,
                                  ema_middle=ema_middle_, mte_1=mte_1_, mte_2=mte_2_,
                                  mte_3=mte_3_, mte_4=mte_4_, ema_10_min_200=ema_10_min_200_,
                                  lte_1=lte_1_, lte_2=lte_2_, ema_1min_A=ema_1min_A_,
                                  ema_Middle_A=ema_Middle_A_, ema_4min_100_A=ema_4min_100_A_,
                                  ema_4min_300_A=ema_4min_300_A_, ema_1min_60=ema_1min_60_, ema_3min_80=ema_3min_80_,
                                  ema_4min_100=ema_4min_100_, ema_4min_200=ema_4min_200_, ema_4min_300=ema_4min_300_,
                                  ema_30min_750=ema_30min_750_, ema_30min_2000=ema_30min_2000_, ema_30min_2500=ema_30min_2500_
                                  )

        session.add(new_chart_row)
        session.commit()

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


# def populate_algo_state(datetime_: datetime.datetime, state_: str, gap_: str, strategy_:
#                         str, cmte_type_: str, cmte_val_: float, next_mte_: str, next_mte_val_: float,
#                         current_bie_val_: float, main_flow_state_: str, highest_sl_ema_type_: str,
#                         highest_sl_ema_val_: float, one_min_high_val_: float, one_min_high_G_: float,
#                         debs_main_buy_ok_: bool, debs_main_sell_ok_: bool, ema2min_buy_state_: str,
#                         ema2min_sell_state_: str, gap_up_ema_: float, gap_down_ema_: float,
#                         gbp_: float, gsp_: float, invested_: bool
#                         ):

def populate_algo_state(
    datetime_: datetime.datetime, one_min_high_val_: float, buy_in_price_: float,
    sell_price_: float, one_min_high_G_: float, gap_price_: float, current_state_: str
):
    session = Session()

    try:
        new_row = AlgoState(datetime=datetime_, one_min_high_val=one_min_high_val_, buy_in_price=buy_in_price_, sell_price=sell_price_,
                            one_min_high_G=one_min_high_G_, gap_price=gap_price_, current_state=current_state_
                            )

        session.add(new_row)
        session.commit()

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def populate_live_stats(
    datetime_: datetime.datetime, equity_: float, fees_: float, holdings_: float,
    net_profit_: float, sharpe_ratio_: float, return_pct_: float, unrealized_: float,
    volume_: float
):
    session = Session()

    try:
        new_row = LiveStats(
            datetime=datetime_,
            equity=equity_,
            fees=fees_,
            holdings=holdings_,
            net_profit=net_profit_,
            sharpe_ratio=sharpe_ratio_,
            return_pct=return_pct_,
            unrealized=unrealized_,
            volume=volume_
        )

        session.add(new_row)
        session.commit()

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def populate_order(
    order_id_: int, price_: float, time_: datetime.datetime,
    symbol_: str, algo_id_: str, datetime_: datetime.datetime
):
    session = Session()

    try:
        new_row = Order(
            order_id=order_id_,
            price=price_,
            time=time_,
            symbol=symbol_,
            algo_id=algo_id_,
            datetime=datetime_
        )

        session.add(new_row)
        session.commit()

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()

