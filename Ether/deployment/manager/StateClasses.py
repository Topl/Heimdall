class EthState:
    def __init__(self):
        self.withdrawals = {}
        self.owner = "0x0"
        self.ownerBalance = 0
        self.depositFee = 0
        self.contractOpen = False

    def __str__(self):
        r = str(self.withdrawals)\
            + "\n"\
            + str(self.owner)\
            + "\n"\
            + str(self.ownerBalance)\
            + "\n"\
            + str(self.depositFee)\
            + "\n"\
            + str(self.contractOpen)
        return r


class ToplState:
    def __init__(self):
        self.withdrawals = {}

    def __str__(self):
        r = str(self.withdrawals)
        return r
