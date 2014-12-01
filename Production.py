class Production(object):
    """
    Represents a production consisting of a left-hand side and a right-hand
    side.
    """

    def __init__(self, lhs, rhs):
        """
        Constructor.
        Inputs:
            * lhs - Graph object on the LHS.
            * rhs - Graph object on the RHS.
        Outputs: N/A 
        """
        self._lhs = lhs
        self._rhs = rhs

    def __str__(self):
        return str(self._lhs) + ' ==> ' + str(self._rhs) + '\n'

    @property
    def lhs(self):
        return self._lhs
    @lhs.setter
    def lhs(self, value):
        self._lhs = value

    @property
    def rhs(self):
        return self._rhs
    @rhs.setter
    def rhs(self, value):
        self._rhs = value