#!/usr/bin/env python3
from ..util import _straight_line_vertices, issparse
import numpy as np
try:
    import networkx as nx
except:
    import warnings
    warnings.warn("Networkx not found, please install network to use its layouts")
    nx = None

class NetworkxCoordinates:
    def __init__(self, graph, layout=None, *args, **kwargs):
        """
        Converts :graph: into a layout. Can be used in conjunction with networkx layouts or using raw 2D-numpy arrays.

        Parameters
        ----------
        graph : a networkx graph.
        layout : the requested input.
        - When :layout: is s string, a lookup will be performed in the networkx avaiable layouts.
        - When :layout: is a dict, it will be assumed that it takes the shape (key, value) = (node_id, 2D-coordinate).
        - When :layout: is numpy array it is assumed it takes the shape (number_of_nodes, 2).


        Yields
        ------
        (node_vertices, line_vertices, arrow_vertices) : tuple
        Yields the node and line vertices in a tuple. This layout only yields a
        single time, and has no builtin animation
        """
        self.graph = graph
        self.positions = np.zeros((len(graph), 2), dtype = np.float32)
        # default random positions
        if type(layout) is type(None):
            self.positions = np.random.rand(*self.positions.shape)

        # check for networkx
        elif isinstance(layout, str):
            if nx:
                if not layout.endswith("_layout"):
                    layout += "_layout" # append for nx
                layout_function = getattr(nx, layout)
                if layout_function:
                    self.positions = np.asarray([i for i in dict(layout_function(graph, **kwargs)).values()])
                else:
                    raise ValueError("Check networkx for layouts")
            else:
                raise ValueError("networkx not found")
        # assume dict from networkx; values are 2-array
        elif isinstance(layout, dict):
            self.positions = np.asarray([i for i in layout.values()])

        # assume given values
        elif isinstance(layout, np.ndarray):
            assert layout.ndim == 2
            assert layout.shape[0] == len(graph)
            self.positions = layout
        else:
            raise ValueError("Input not understood")

        # normalize coordinates
        self.positions = (self.positions - self.positions.min()) / (self.positions.max() - self.positions.min())
        self.positions = self.positions.astype(np.float32)

    def __call__(self, adjacency_mat, directed = False):
        """
        adjacency_mat : sparse adjacency matrix.
        directed : bool for assertig whether the graph is directed.
        """
        if issparse(adjacency_mat):
            adjacency_mat = adjacency_mat.tocoo()
        line_vertices, arrows = _straight_line_vertices(adjacency_mat, self.positions, directed)

        yield self.positions, line_vertices, arrows

    @property
    def adj(self):
        """
        Convenient storage and holder of the adjacency matrix for the :scene.visuals.Graph: function.
        """
        return nx.adjacency_matrix(self.graph)
