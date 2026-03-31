#region imports
from ResistorNetwork import ResistorNetwork, ResistorNetwork_2
#endregion

# region Function Definitions
def main():
    """
    This program solves for the unknown currents in the circuit of the homework assignment.
    :return: nothing
    """
    print("Network 1:")
    Net = ResistorNetwork()
    Net.BuildNetworkFromFile("ResistorNetwork.txt")
    Net.AnalyzeCircuit()

    print("\nNetwork 2:")
    Net_2 = ResistorNetwork_2()
    Net_2.BuildNetworkFromFile("ResistorNetwork_2.txt")
    Net_2.AnalyzeCircuit()
# endregion

# region function calls
if __name__ == "__main__":
    main()
# endregion