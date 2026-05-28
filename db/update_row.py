from .model import Session, ChartData, AlgoState
import datetime


def populate_chart(date_time_: datetime.datetime, open_: float, high_: float, low_: float,
                   close_: float, volume_: int, ema_1min_: float,
                   ema_middle_: float, mte_1_: float, mte_2_: float,
                   mte_3_: float, mte_4_: float, ema_10_min_200_: float,
                   lte_1_: float, lte_2_: float, mte1_L10_: float,
                   mte1_L9_: float, mte1_L8_: float, mte1_L7_: float,
                   mte1_L6_: float, mte1_L5_: float, mte1_L4_: float,
                   mte1_L3_: float, mte1_L2_: float, mte1_L1_: float,
                   mte4_L5_: float, mte4_L4_: float, mte4_L3_: float,
                   mte4_L2_: float, mte4_L1_: float, mte4_L0_: float,
                   mte4_nL1_: float, mte4_nL2_: float, mte4_nL3_: float,
                   mte4_nL4_: float, mte4_nL5_: float, ema_1min_A_: float,
                   ema_Middle_A_: float, ema_4min_100_A_: float, ema_4min_300_A_: float,
                   ema_1min_60_: float, ema_3min_80_: float, ema_4min_100_: float,
                   ema_4min_200_: float, ema_4min_300_: float
                   ):

    session = Session()

    try:
        new_chart_row = ChartData(datetime=date_time_, open=open_, high=high_, low=low_, close=close_,
                                  volume=volume_, ema_1min=ema_1min_,
                                  ema_middle=ema_middle_, mte_1=mte_1_, mte_2=mte_2_,
                                  mte_3=mte_3_, mte_4=mte_4_, ema_10_min_200=ema_10_min_200_,
                                  lte_1=lte_1_, lte_2=lte_2_, mte1_L10=mte1_L10_,
                                  mte1_L9=mte1_L9_, mte1_L8=mte1_L8_, mte1_L7=mte1_L7_,
                                  mte1_L6=mte1_L6_, mte1_L5=mte1_L5_, mte1_L4=mte1_L4_,
                                  mte1_L3=mte1_L3_, mte1_L2=mte1_L2_, mte1_L1=mte1_L1_,
                                  mte4_L5=mte4_L5_, mte4_L4=mte4_L4_, mte4_L3=mte4_L3_,
                                  mte4_L2=mte4_L2_, mte4_L1=mte4_L1_, mte4_L0=mte4_L0_,
                                  mte4_nL1=mte4_nL1_, mte4_nL2=mte4_nL2_, mte4_nL3=mte4_nL3_,
                                  mte4_nL4=mte4_nL4_, mte4_nL5=mte4_nL5_, ema_1min_A=ema_1min_A_,
                                  ema_Middle_A=ema_Middle_A_, ema_4min_100_A=ema_4min_100_A_,
                                  ema_4min_300_A=ema_4min_300_A_, ema_1min_60=ema_1min_60_, ema_3min_80=ema_3min_80_,
                                  ema_4min_100=ema_4min_100_, ema_4min_200=ema_4min_200_, ema_4min_300=ema_4min_300_
                                  )

        session.add(new_chart_row)
        session.commit()

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def populate_algo_state(datetime_: datetime.datetime, state_: str, gap_: str, strategy_:
                        str, cmte_type_: str, cmte_val_: float, next_mte_: str, next_mte_val_: float,
                        current_bie_val_: float, main_flow_state_: str, highest_sl_ema_type_: str,
                        highest_sl_ema_val_: float, one_min_high_val_: float, one_min_high_G_: float,
                        debs_main_buy_ok_: bool, debs_main_sell_ok_: bool, ema2min_buy_state_: str,
                        ema2min_sell_state_: str, gap_up_ema_: float, gap_down_ema_: float,
                        gbp_: float, gsp_: float, invested_: bool
                        ):

    session = Session()

    try:
        new_row = AlgoState(datetime=datetime_, state=state_, gap=gap_, strategy=strategy_,
                            current_mte_type=cmte_type_, current_mte_val=cmte_val_, next_mte=next_mte_, next_mte_val=next_mte_val_,
                            current_bie_val=current_bie_val_, main_flow_state=main_flow_state_, highest_sl_ema_type=highest_sl_ema_type_,
                            highest_sl_ema_val=highest_sl_ema_val_, one_min_high_val=one_min_high_val_, one_min_high_G=one_min_high_G_,
                            debs_main_buy_ok=debs_main_buy_ok_, debs_main_sell_ok=debs_main_sell_ok_, ema2min_buy_state=ema2min_buy_state_,
                            ema2min_sell_state=ema2min_sell_state_, gap_up_ema=gap_up_ema_, gap_down_ema=gap_down_ema_,
                            gbp=gbp_, gsp=gsp_, invested=invested_
                            )

        session.add(new_row)
        session.commit()

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()
