import pulp as plp
import matplotlib.pyplot as plt
import math
import networkx as nx


class GraphMappingProblem:
    def __init__(self, phy: nx.DiGraph, SLICE_SETS: list[list[nx.DiGraph]]) -> None:
        self.name = "graphmaping_problem"
        self.PHY = phy
        self.SFC_SET = SLICE_SETS
        self.solution = None
        self.solution_time = None
        self.obj_value = None
        self.status = None  # None=Unsolved, 1=Solved, 0=SolvedNoSolution, -1=ErrorOnSolve
        self.solution_status = None  # None=Unsolved, 1=OK, 0=NoSolution, -1=Invalid
    

                       
           