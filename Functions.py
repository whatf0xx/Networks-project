# -*- coding: utf-8 -*-
"""
Created on Wed Mar  9 19:22:27 2022

@author: whatf
"""

import networkx as nx
import numpy as np
import random

"""
Returns a complete graph with m+1 nodes.
"""

def seed(m: int):
    return nx.complete_graph(m+1)

"""
Set-up the list from which to randomly pick nodes for the BA algorithm steps,
taking as inputs:
    N - the eventual size of the BA graph.
    m - the standard constant for adding new edges at each time step.
This assumes that the seed graph for the BA model is given as above.
N.B. when calling from this list the slicing is very important - the array is
initialised to full length in order to stop memory re-allocation as the
algorithm runs, which means during the run the last half of the array is full
of 0s, which will corrupt how the code runs if they are left in the sliced
bin, while it is being used to calculate the preferential attachment.
"""

def make_list(N: int, m: int):
    length = m*(m+1) + 2*m*(N-m-1)
    node_list = np.zeros(length, dtype=np.uint16)
    for i in range(m+1):
        for j in range(m):
            node_list[i*(m)+j] = i
    
    return node_list

"""
The BA algorithm, iterated for one step. Takes a graph G, and the associated
degree bin, and performs a step, adding a node and m edges to the graph,
assigned by preferential attachment, and adding nodes which get edges added to
them to the degree bin.
"""

def BA_step(G, degree_bin, m, t):
    new_node = m+t+1 #new node is the (m+t+1)th, starting from t=0
    used_posns = m*(m+1) + 2*m*t
    G.add_node(new_node) 
    
    # bin_positions = [random.randint(0, used_posns) for i in range(m)]
    # #this step seems to do what it should for t=0
    
    # lucky_nodes = [int(degree_bin[b]) for b in bin_positions]
    # print(f"bin positions: {bin_positions}")
    # print(f"corresponding nodes: {lucky_nodes}")
    lucky_nodes = []
    trimmed_bin = degree_bin[:used_posns].copy()
    
    for i in range(m):
        node = random.choice(trimmed_bin)
        lucky_nodes.append(node)
        trimmed_bin = trimmed_bin[trimmed_bin != node]
    
    for i, l in enumerate(lucky_nodes):
        G.add_edge(new_node, l) #add edges to the lucky nodes
        degree_bin[used_posns + i] = l
        
    for i in range(m):
        degree_bin[used_posns + m + i] = new_node
        
"""
A neatly wrapped-up function to generate a BA graph with characteristic m and 
size N. If dist == True, also returns the degree for each node.
"""

def gen_BA(m, N, dist=False):
    
    G = seed(m)
    degree_bin = make_list(N, m)

    for t in range(N-m-1):
        BA_step(G, degree_bin, m, t)
        
    if dist:
        d = np.bincount(degree_bin)
        return G, d
        
    return G

"""
Same as above, but with some breaks in to output useful data to test the
algorithm is running correctly.
"""

def test_BA(m, N):
    
    G = seed(m)
    degree_bin = make_list(N, m)
    
    nodes = []                      #the number of nodes the graph has
    edges = []                      #the number of edges the graph has
    norm = []
    k_predict = []                  #calculated degree of picked nodes
    k_meas = []                     #actual average degree of picked nodes
    
    nodes.append(len(G.nodes))
    edges.append(len(G.edges))

    for t in range(N-m-1):
        used_posns = m*(m+1) + 2*m*t
        trimmed_bin = degree_bin[:used_posns].copy()
        d = np.bincount(trimmed_bin)
        norm.append(np.sum([k for k in d])/(2*len(G.edges)))
        k_squared = np.sum([k**2 for k in d])
        k_predict.append(k_squared/(2*len(G.edges)))
        lucky_nodes = BA_test_step(G, degree_bin, m, t)
        t = list(trimmed_bin)
        lucky_degrees = [t.count(l) for l in lucky_nodes]
        k_meas.append(np.mean(lucky_degrees))
        nodes.append(len(G.nodes))
        edges.append(len(G.edges))
        
    return nodes, edges, norm, k_predict, k_meas

"""
Another slightly modified function to lend itself to being used for testing.
"""

def BA_test_step(G, degree_bin, m, t):
    new_node = m+t+1 #new node is the (m+t+1)th, starting from t=0
    used_posns = m*(m+1) + 2*m*t
    G.add_node(new_node) 
    
    # bin_positions = [random.randint(0, used_posns) for i in range(m)]
    # #this step seems to do what it should for t=0
    
    # lucky_nodes = [int(degree_bin[b]) for b in bin_positions]
    # print(f"bin positions: {bin_positions}")
    # print(f"corresponding nodes: {lucky_nodes}")
    lucky_nodes = []
    trimmed_bin = degree_bin[:used_posns].copy()
    
    for i in range(m):
        node = random.choice(trimmed_bin)
        lucky_nodes.append(node)
        trimmed_bin = trimmed_bin[trimmed_bin != node]
    
    for i, l in enumerate(lucky_nodes):
        G.add_edge(new_node, l) #add edges to the lucky nodes
        degree_bin[used_posns + i] = l
        
    for i in range(m):
        degree_bin[used_posns + m + i] = new_node
        
    return lucky_nodes

"""
A test for the BA model based on the average degree at each time step.
"""

def test2_BA(m, N):
    
    mu_k = []
    G = seed(m)
    degree_bin = make_list(N, m)

    for t in range(N-m-1):
        used_posns = m*(m+1) + 2*m*t
        trimmed_bin = degree_bin[:used_posns].copy()
        degrees = np.bincount(trimmed_bin)
        mu_k.append(np.mean(degrees))
        BA_step(G, degree_bin, m, t)
    
    return mu_k