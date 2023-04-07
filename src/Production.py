from YapyGraph.src import Graph

#------------------------------------------------------------------------------
#   ____                _            _   _             
#  |  _ \ _ __ ___   __| |_   _  ___| |_(_) ___  _ __  
#  | |_) | '__/ _ \ / _` | | | |/ __| __| |/ _ \| '_ \ 
#  |  __/| | | (_) | (_| | |_| | (__| |_| | (_) | | | |
#  |_|   |_|  \___/ \__,_|\__,_|\___|\__|_|\___/|_| |_|
#                                               
class Production(object):
    """
    Represents a production consisting of a left-hand side and a right-hand
    side.
    """

    #------------------------------------------------------------------------------
    def __init__(self, lhs: Graph, rhs: Graph):
        """
        Constructor.
        Inputs:
            * lhs - Graph object on the LHS.
            * rhs - Graph object on the RHS.
        Outputs: N/A 
        """
        self._lhs = lhs
        self._rhs = rhs

    #------------------------------------------------------------------------------
    def __str__(self) -> str:
        return str(self._lhs) + ' ==> ' + str(self._rhs) + '\n'

    #------------------------------------------------------------------------------
    def lhs(self):
        return self._lhs

    def set_lhs(self, value):
        self._lhs = value

     #------------------------------------------------------------------------------
    def rhs(self):
        return self._rhs

    def set_rhs(self, value):
        self._rhs = value