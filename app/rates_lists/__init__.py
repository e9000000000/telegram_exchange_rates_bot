'''
Dir to put there modules for geting info about exchange rates.

All of modules shoud have async `rates` function that returns `dict[str: float]` 
where `str` is a currency code and float is a rate to USD.

'''