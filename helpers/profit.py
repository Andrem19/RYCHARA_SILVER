import shared_vars as sv

def profit_counter(taker_maker: bool, open_price: float, buy: bool, close_price: float, amount: int) -> float:
    if taker_maker == True:
        comission = amount /100 * 0.14
    else:
        comission = amount /100 * 0.14


    if open_price != 0:
        coins = amount / open_price
        profit_or_loss = 0
        isProf = None

        sell_pr = coins * close_price
        pr =  amount - sell_pr
        profit_or_loss = abs(pr)
        if buy:
            if open_price < close_price:
                isProf = True
                profit_or_loss -= comission
            elif close_price <= open_price:
                isProf = False
                profit_or_loss += comission
        else:
            if open_price <= close_price:
                isProf = False
                profit_or_loss += comission
            elif close_price < open_price:
                isProf = True
                profit_or_loss -= comission
        
        if isProf:
            return abs(round(profit_or_loss, 4))
        else:
            return -abs(round(profit_or_loss, 4))
    else: return 0
