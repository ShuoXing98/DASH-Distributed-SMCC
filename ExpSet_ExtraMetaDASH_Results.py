#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
# os.environ["OMP_NUM_THREADS"] = "1" # export OMP_NUM_THREADS=4
# os.environ["OPENBLAS_NUM_THREADS"] = "1" # export OPENBLAS_NUM_THREADS=4 
os.environ["MKL_NUM_THREADS"] = "1" # export MKL_NUM_THREADS=6
# os.environ["VECLIB_MAXIMUM_THREADS"] = "1" # export VECLIB_MAXIMUM_THREADS=4
os.environ["NUMEXPR_NUM_THREADS"] = "1" # export NUMEXPR_NUM_THREADS=6

import numpy as np
from datetime import datetime
import pandas as pd
from scipy import sparse
import networkx as nx
import random
import sys
#import ast
import os

# Disable  
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

from mpi4py import MPI

# # Load the Objective function classes 
from objectives import  NetCoverSparse,\
                        RevenueMaxOnNetSparse,\
                        InfluenceMaxSparse,\
                        ImageSummarizationMonotone

# Load our optimization algorithms and helper functions
from src import submodular_DASH_Centralized

def run_DASH(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP, nthreads=1, p_root=0, trials=1, gph = True):
    size_groundset = objective.A.shape[1]
    nT = objective.nThreads
    comm.barrier()
    algostring = 'DASH'
    algostring += '-'+str(size)+'-'+str(nT)
    if rank == p_root:
        print('Beginning ', algostring, 'for experiment: ', experiment_string)
    # eps = 0.007
    eps = 0.05
    val_vec = []
    queries_vec = []
    time_vec = []
    time_dist_vec = []
    time_post_vec = []
    sol_size_vec = []
    # Save data progressively.
    #STOP IF APPROX is reached
    stop_if_approx = False 
    
    for ii, kk in enumerate(k_vals_vec):

        for trial in range(trials):
            comm.barrier()

            # Free memory between trials
            sol = []
            sol_r = [] 
            time_r = []
            queries_r = []

            # Run the algorithm
            val, time, time_dist, time_post, sol = submodular_DASH_Centralized.DASH(objective, kk, eps, comm, rank, size, p_root=0, seed=seedP, stop_if_aprx=stop_if_approx, nthreads=nthreads)

            if rank == p_root:
                val_vec.append(val)
                time_vec.append(time)
                time_dist_vec.append(time_dist)
                time_post_vec.append(time_post)
                sol_size_vec.append(len(sol))

                ## Save data progressively
                dataset = pd.DataFrame({'f_of_S':  val_vec, \
                                        'Time':    time_vec, \
                                        'TimeDist':    time_dist_vec, \
                                        'TimePost':    time_post_vec, \
                                        'SolSize':    sol_size_vec, \
                                        'k':       np.concatenate([np.repeat(k_vals_vec[:ii], trials), [kk]*(trial+1)]), \
                                        'n':       [size_groundset]*(ii*trials+trial+1), \
                                        'nNodes':   [size]*(ii*trials+trial+1), \
                                        'nThreads':   [nT]*(ii*trials+trial+1), \
                                        'trial':   np.concatenate([np.tile(range(1,(trials+1)), ii), range(1, (trial+2))])
                                        })
                dataset.to_csv(path_or_buf = filepath_string + experiment_string +'_exp1_'+ algostring +".csv", index=False)


            if rank == p_root:
                print('f(S)=', val,  'time=', time, algostring, experiment_string, 'k=', kk)
                print('\n')


def run_PGB(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP, nthreads=1, p_root=0, trials=1, gph = True):
    
    size_groundset = objective.A.shape[1]
    nT = objective.nThreads
    
    comm.barrier();
    algostring = 'PGB'
    algostring += '-'+str(size)+'-'+str(nT)

    
    if rank == p_root:
        print('Beginning ', algostring, 'for experiment: ', experiment_string)
    eps = 0.05
    val_vec = []
    queries_vec = []
    time_vec = []
    sol_size_vec = []

    for ii, kk in enumerate(k_vals_vec):

        for trial in range(trials):
            comm.barrier()

            # Free memory between trials
            sol = []
            sol_r = [] 
            time_r = []
            queries_r = []

            # Run the algorithm
            val, time, sol, sol_r, time_r, queries_r = submodular_DASH_Centralized.ParallelGreedyBoost_Original_MultiNode(objective, kk, eps, comm, rank, size, p_root, seed=seedP, stop_if_approx=False );
            if rank == p_root:
            
                print('f(S)=', val,  'time=', time, algostring, experiment_string, 'with k=', kk)

                val_vec.append(val)
                time_vec.append(time)
                sol_size_vec.append(len(sol))
                ## Save data progressively
                dataset = pd.DataFrame({'f_of_S':  val_vec, \
                                        'Time':    time_vec, \
                                        'SolSize':    sol_size_vec, \
                                        'k':       np.concatenate([np.repeat(k_vals_vec[:ii], trials), [kk]*(trial+1)]), \
                                        'n':       [size_groundset]*(ii*trials+trial+1), \
                                        'nNodes':   [size]*(ii*trials+trial+1), \
                                        'nThreads':   [nT]*(ii*trials+trial+1), \
                                        'trial':   np.concatenate([np.tile(range(1,(trials+1)), ii), range(1, (trial+2))])
                                        })
                dataset.to_csv(path_or_buf = filepath_string + experiment_string +'_exp1_'+ algostring +".csv", index=False)    


def run_MEDDASH(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP, nthreads=1, p_root=0, trials=1, gph = True):
    size_groundset = objective.A.shape[1]
    nT = objective.nThreads
    comm.barrier()
    algostring = 'MEDDASH'
    algostring += '-'+str(size)+'-'+str(nT)
    if rank == p_root:
        print('Beginning ', algostring, 'for experiment: ', experiment_string)
    # eps = 0.007
    eps = 0.05
    val_vec = []
    queries_vec = []
    time_vec = []
    time_dist_vec = []
    time_post_vec = []
    sol_size_vec = []
    # Save data progressively.
    #STOP IF APPROX is reached
    stop_if_approx = False 
    
    for ii, kk in enumerate(k_vals_vec):

        for trial in range(trials):
            comm.barrier()

            # Free memory between trials
            sol = []
            sol_r = [] 
            time_r = []
            queries_r = []

            # Run the algorithm
            val, time, time_dist, time_post, sol = submodular_DASH_Centralized.MEDDASH(objective, kk, eps, comm, rank, size, p_root=0, seed=seedP, nthreads=nthreads)

            if rank == p_root:
                val_vec.append(val)
                time_vec.append(time)
                time_dist_vec.append(time_dist)
                time_post_vec.append(time_post)
                sol_size_vec.append(len(sol))

                ## Save data progressively
                dataset = pd.DataFrame({'f_of_S':  val_vec, \
                                        'Time':    time_vec, \
                                        'TimeDist':    time_dist_vec, \
                                        'TimePost':    time_post_vec, \
                                        'SolSize':    sol_size_vec, \
                                        'k':       np.concatenate([np.repeat(k_vals_vec[:ii], trials), [kk]*(trial+1)]), \
                                        'n':       [size_groundset]*(ii*trials+trial+1), \
                                        'nNodes':   [size]*(ii*trials+trial+1), \
                                        'nThreads':   [nT]*(ii*trials+trial+1), \
                                        'trial':   np.concatenate([np.tile(range(1,(trials+1)), ii), range(1, (trial+2))])
                                        })
                dataset.to_csv(path_or_buf = filepath_string + experiment_string +'_exp1_'+ algostring +".csv", index=False)


            if rank == p_root:
                print('f(S)=', val,  'time=', time, algostring, experiment_string, 'k=', kk)
                print('\n')


def run_MEDRG(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP, nthreads=1, p_root=0, trials=1, gph = True):
    size_groundset = objective.A.shape[1]
    nT = objective.nThreads
    comm.barrier()
    algostring = 'MEDRG'
    algostring += '-'+str(size)+'-'+str(nT)
    if rank == p_root:
        print('Beginning ', algostring, 'for experiment: ', experiment_string)
    # eps = 0.007
    eps = 0.05
    val_vec = []
    queries_vec = []
    time_vec = []
    time_dist_vec = []
    time_post_vec = []
    sol_size_vec = []
    # Save data progressively.
    #STOP IF APPROX is reached
    stop_if_approx = False 
    
    for ii, kk in enumerate(k_vals_vec):

        for trial in range(trials):
            comm.barrier()

            # Free memory between trials
            sol = []
            sol_r = [] 
            time_r = []
            queries_r = []

            # Run the algorithm
            val, time, time_dist, time_post, sol = submodular_DASH_Centralized.MEDRG(objective, kk, eps, comm, rank, size, p_root=0, seed=seedP, nthreads=nthreads)

            if rank == p_root:
                val_vec.append(val)
                time_vec.append(time)
                time_dist_vec.append(time_dist)
                time_post_vec.append(time_post)
                sol_size_vec.append(len(sol))

                ## Save data progressively
                dataset = pd.DataFrame({'f_of_S':  val_vec, \
                                        'Time':    time_vec, \
                                        'TimeDist':    time_dist_vec, \
                                        'TimePost':    time_post_vec, \
                                        'SolSize':    sol_size_vec, \
                                        'k':       np.concatenate([np.repeat(k_vals_vec[:ii], trials), [kk]*(trial+1)]), \
                                        'n':       [size_groundset]*(ii*trials+trial+1), \
                                        'nNodes':   [size]*(ii*trials+trial+1), \
                                        'nThreads':   [nT]*(ii*trials+trial+1), \
                                        'trial':   np.concatenate([np.tile(range(1,(trials+1)), ii), range(1, (trial+2))])
                                        })
                dataset.to_csv(path_or_buf = filepath_string + experiment_string +'_exp1_'+ algostring +".csv", index=False)


            if rank == p_root:
                print('f(S)=', val,  'time=', time, algostring, experiment_string, 'k=', kk)
                print('\n')


def run_RandGreedI(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP, nthreads=1, p_root=0, trials=1, gph = True):
    size_groundset = objective.A.shape[1]
    nT = objective.nThreads
    comm.barrier();
    algostring = 'RandGreedI'
    algostring += '-'+str(size)+'-'+str(nT)
    if rank == p_root:
        print('Beginning ', algostring, 'for experiment: ', experiment_string)
    eps = 0.05
    val_vec = []
    queries_vec = []
    time_vec = []
    time_dist_vec = []
    time_post_vec = []
    sol_size_vec = []

    for ii, kk in enumerate(k_vals_vec):

        for trial in range(trials):
            comm.barrier()

            # Free memory between trials
            sol = []
            sol_r = [] 
            time_r = []
            queries_r = []

            # Run the algorithm
            val, time, time_dist, time_post, sol, sol_r, time_r, queries_r = submodular_DASH_Centralized.RandGreedI(objective, kk, eps, comm, rank, size, p_root=0, seed=seedP, nthreads=nthreads)
            
            if rank == p_root:
            
                print('f(S)=', val,  'time=', time, algostring, experiment_string, 'with k=', kk)

                val_vec.append(val)
                time_vec.append(time)
                time_dist_vec.append(time_dist)
                time_post_vec.append(time_post)
                sol_size_vec.append(len(sol))

                ## Save data progressively
                dataset = pd.DataFrame({'f_of_S':  val_vec, \
                                        'Time':    time_vec, \
                                        'TimeDist':    time_dist_vec, \
                                        'TimePost':    time_post_vec, \
                                        'SolSize':    sol_size_vec, \
                                        'k':       np.concatenate([np.repeat(k_vals_vec[:ii], trials), [kk]*(trial+1)]), \
                                        'n':       [size_groundset]*(ii*trials+trial+1), \
                                        'nNodes':   [size]*(ii*trials+trial+1), \
                                        'nThreads':   [nT]*(ii*trials+trial+1), \
                                        'trial':   np.concatenate([np.tile(range(1,(trials+1)), ii), range(1, (trial+2))])
                                        })
                dataset.to_csv(path_or_buf = filepath_string + experiment_string +'_exp1_'+ algostring +".csv", index=False)    


def run_RandGreedI_LAG(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP, nthreads=1, p_root=0, trials=1, gph = True):
    size_groundset = objective.A.shape[1]
    nT = objective.nThreads
    comm.barrier();
    algostring = 'RandGreedILAG'
    algostring += '-'+str(size)+'-'+str(nT)
    if rank == p_root:
        print('Beginning ', algostring, 'for experiment: ', experiment_string)
    eps = 0.05
    val_vec = []
    queries_vec = []
    time_vec = []
    time_dist_vec = []
    time_post_vec = []
    sol_size_vec = []

    for ii, kk in enumerate(k_vals_vec):

        for trial in range(trials):
            comm.barrier()

            # Free memory between trials
            sol = []
            sol_r = [] 
            time_r = []
            queries_r = []

            # Run the algorithm
            val, time, time_dist, time_post, sol, sol_r, time_r, queries_r = submodular_DASH_Centralized.RandGreedI_LAG(objective, kk, eps, comm, rank, size, p_root=0, seed=seedP, nthreads=nthreads)
            
            if rank == p_root:
            
                print('f(S)=', val,  'time=', time, algostring, experiment_string, 'with k=', kk)

                val_vec.append(val)
                time_vec.append(time)
                time_dist_vec.append(time_dist)
                time_post_vec.append(time_post)
                sol_size_vec.append(len(sol))

                ## Save data progressively
                dataset = pd.DataFrame({'f_of_S':  val_vec, \
                                        'Time':    time_vec, \
                                        'TimeDist':    time_dist_vec, \
                                        'TimePost':    time_post_vec, \
                                        'SolSize':    sol_size_vec, \
                                        'k':       np.concatenate([np.repeat(k_vals_vec[:ii], trials), [kk]*(trial+1)]), \
                                        'n':       [size_groundset]*(ii*trials+trial+1), \
                                        'nNodes':   [size]*(ii*trials+trial+1), \
                                        'nThreads':   [nT]*(ii*trials+trial+1), \
                                        'trial':   np.concatenate([np.tile(range(1,(trials+1)), ii), range(1, (trial+2))])
                                        })
                dataset.to_csv(path_or_buf = filepath_string + experiment_string +'_exp1_'+ algostring +".csv", index=False)    


def run_BiCriteriaGreedy(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP, nthreads=1, p_root=0, trials=1, gph = True):
    size_groundset = objective.A.shape[1]
    nT = objective.nThreads
    comm.barrier()
    algostring = 'BiCriteriaGreedy'
    algostring += '-'+str(size)+'-'+str(nT)
    if rank == p_root:
        print('Beginning ', algostring, 'for experiment: ', experiment_string)
    # eps = 0.007
    eps = 0.05
    val_vec = []
    queries_vec = []
    time_vec = []
    time_dist_vec = []
    time_post_vec = []
    sol_size_vec = []
    # Save data progressively.
    #STOP IF APPROX is reached
    stop_if_approx = False  
    for ii, kk in enumerate(k_vals_vec):

        for trial in range(trials):
            comm.barrier()

            # Free memory between trials
            sol = []
            sol_r = [] 
            time_r = []
            queries_r = []

            # Run the algorithm
            val, time, time_dist, time_post, sol = submodular_DASH_Centralized.BiCriteriaGreedy(objective, kk, eps, comm, rank, size, p_root=0, seed=seedP, nthreads=nthreads, run_Full=False)

            if rank == p_root:
                val_vec.append(val)
                time_vec.append(time)
                time_dist_vec.append(time_dist)
                time_post_vec.append(time_post)
                sol_size_vec.append(len(sol))

                ## Save data progressively
                dataset = pd.DataFrame({'f_of_S':  val_vec, \
                                        'Time':    time_vec, \
                                        'TimeDist':    time_dist_vec, \
                                        'TimePost':    time_post_vec, \
                                        'SolSize':    sol_size_vec, \
                                        'k':       np.concatenate([np.repeat(k_vals_vec[:ii], trials), [kk]*(trial+1)]), \
                                        'n':       [size_groundset]*(ii*trials+trial+1), \
                                        'nNodes':   [size]*(ii*trials+trial+1), \
                                        'nThreads':   [nT]*(ii*trials+trial+1), \
                                        'trial':   np.concatenate([np.tile(range(1,(trials+1)), ii), range(1, (trial+2))])
                                        })
                dataset.to_csv(path_or_buf = filepath_string + experiment_string +'_exp1_'+ algostring +".csv", index=False)


            if rank == p_root:
                print('f(S)=', val,  'time=', time, algostring, experiment_string, 'k=', kk)
                print('\n')


def run_LTLG_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, algo = "ALL", nthreads=1, p_root=0, trials=1):
    """ Parallel MPI function to run all benchmark algorithms over all values of k for a given objective function and 
    save CSV files of data and runtimes """
    blockPrint()
    # run_RS(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, nthreads=nthreads)
    seed = 42 #  8, 14, 25, 35, 42
    if(algo=="BCG"):
        run_BiCriteriaGreedy(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP=seed, nthreads=objective.nThreads)


    if(algo=="RGGB"):    
        run_RandGreedI(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP=seed, nthreads=objective.nThreads)

    
    if(algo=="RGLAG"):    
        run_RandGreedI_LAG(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP=seed, nthreads=objective.nThreads)

    
    if(algo=="DASH"):
        run_DASH(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP=seed, nthreads=objective.nThreads)


    if(algo=="MEDDASH"):
        run_MEDDASH(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP=seed, nthreads=objective.nThreads)

    
    if(algo=="MEDRG"):
        run_MEDRG(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP=seed, nthreads=objective.nThreads)


    if(algo=="PGBD"):
        run_PGB(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, seedP=seed)

    enablePrint()
    comm.barrier()
        
    if rank == p_root:
        print('EXP 1 FINISHED\n')
    comm.barrier()

    return

if __name__ == '__main__':

    start_runtime = datetime.now()

    p_root = 0

    filepath_string = "experiment_results_output_data/ExpApp/"
    
    obj = str( sys.argv[1] );
    algoIn = str( sys.argv[2] );
    nthreads = int( sys.argv[3])
    directory = 'data/data_exp1/'
    # Start MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    if rank == p_root:
        print('Initializing run')

    
    k_vals_vec_tmp = [1, 2, 3, 4, 5]   

    # ################################################################
    # ## MaxCover - BA Graph #####################
    # ################################################################
    if(obj=="BA"):
        comm.barrier()
        if rank == p_root:
            print( 'Initializing BA Objective' )
        experiment_string = 'BA_100k'
        size_of_ground_set = 100000
    
        if rank == p_root:
    
            G = nx.barabasi_albert_graph(size_of_ground_set, 5, seed=42)
            try:
                G.remove_edges_from(G.selfloop_edges())
            except:
                G.remove_edges_from(nx.selfloop_edges(G)) #Later version of networkx prefers this syntax
    
            if size_of_ground_set < 100:
                A = np.asarray( nx.to_numpy_matrix(G) )
                A.fill_diagonal(1)
                A.astype('bool_')
                objective_rootprocessor = NetCover.NetCover(A)
    
            else:
                A = nx.to_scipy_sparse_matrix(G, format='csr')
                A.setdiag(1)
                # Generate our NetCover class containing the function
                objective_rootprocessor = NetCoverSparse.NetCoverSparse(A, nthreads)
            
    
        # Send class to all processors
        if rank != 0:
            objective_rootprocessor = None
        objective = comm.bcast(objective_rootprocessor, root=0)

        k_p = np.ceil(len(objective.groundset)/(size*size))
        k_vals_vec = [int(i * k_p) for i in k_vals_vec_tmp]
         
        if rank == p_root:
            print( 'BA Objective initialized. Beginning tests.' )
        comm.barrier()
        run_LTLG_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, algo=algoIn, nthreads=nthreads)
    
        comm.barrier()
    
    
    # ################################################################
    # ##           InfluenceMax - EPINIONS NETWORK      ##############
    # ################################################################
    if(obj=="IFM3"):
        comm.barrier()
        if rank == p_root:
            print( 'Initializing influence max Objective' )
    
        experiment_string = 'INFLUENCEEPINIONS'
    
        # Undirected Facebook Network. Format as an adjacency matrix
        filename_net = directory+"soc-epinions.csv"
    
    
        edgelist = pd.read_csv(filename_net)
        net_nx = nx.from_pandas_edgelist(edgelist, source='source', target='target', edge_attr=None, create_using=None)
        net_nx = net_nx.to_undirected()
        try:
            net_nx.remove_edges_from(net_nx.selfloop_edges())
        except:
            net_nx.remove_edges_from(nx.selfloop_edges(net_nx)) #Later version of networkx prefers this syntax
    
    
        #A = np.asarray( nx.adjacency_matrix(net_nx).todense() )
        if rank == p_root:
            print( 'Loaded data. Generating sparse adjacency matrix' )
        A = nx.to_scipy_sparse_matrix(net_nx, format='csr')
        A.setdiag(1)
    
        #objective = NetCover.NetCover(A)
        p = 0.01
        objective = InfluenceMaxSparse.InfluenceMaxSparse(A, p, nthreads)
        k_p = np.ceil(len(objective.groundset)/(size*size))
        k_vals_vec = [int(i * k_p) for i in k_vals_vec_tmp]
        if rank == p_root:
            print( 'EPINIONS Objective of', A.shape[0], 'elements initialized. Beginning tests.' )
    
        comm.barrier()
        run_LTLG_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, algo=algoIn)





    # ################################################################
    # ## YOUTUBE 2000 REVENUE MAXIMIZATION EXAMPLE ####################
    # ################################################################
    if(obj=="RVM3"):
        comm.barrier()
        if rank == p_root:
            print( 'Initializing Youtube Objective' )
        experiment_string = 'YOUTUBE2000'
    
        edgelist = pd.read_csv(directory+'youtube_2000rand_edgelist.csv', delimiter=',')
        A = edgelist.pivot(index = "source", columns = "target", values = "weight_draw")
        A = A.values
        A[np.isnan(A)] = 0
        A[A>0] = A[A>0] + 1.0
        # A.setdiag(0)
        np.fill_diagonal(A, 0)
        # Set the power between 0 and 1. More towards 0 means revenue is more subadditive as a node gets more influences
        alpha = 0.3
        A = sparse.csr_matrix(A)
        # Generate class containing our f(S)
        objective = RevenueMaxOnNetSparse.RevenueMaxOnNetSparse(A, alpha, nthreads)
        k_p = np.ceil(len(objective.groundset)/(size*size))
        k_vals_vec = [int(i * k_p) for i in k_vals_vec_tmp]
        if rank == p_root:
            print( 'YOUTUBE Objective initialized. Adjacency matrix shape is:', A.shape, ' Beginning tests.' )
    
        comm.barrier()
        run_LTLG_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, algo=algoIn)
    


    # ################################################################
    # ###     Image Summarisation  - CIFAR 10           ##############
    # ################################################################
    # Load the image data and generate the image pairwise distance matrix Dist
    #Download the "images_10K_mat.csv" file from "https://file.io/w0PEXw4j5Xcx" and place it in "data/data_exp1" #
    
    if(obj=="IS"):
        comm.barrier()
        if rank == p_root:
            print( 'Initializing image summ Objective' )
    
        experiment_string = 'IMAGESUMM'
    
        # Undirected Facebook Network. Format as an adjacency matrix
        filename_net = directory+"images_10K_mat.csv"
        
        # Sim = ImageSummarizationMonotone.load_image_similarity_matrix(filename_net)
        Sim = pd.read_csv(filename_net, header=None).values
        
        
        if rank == p_root:
            print( 'Loaded data. Generated adjacency matrix' )
        objective = ImageSummarizationMonotone.ImageSummarizationMonotone(Sim, nthreads)
        k_p = np.ceil(len(objective.groundset)/(size*size))
        k_vals_vec = [int(i * k_p) for i in k_vals_vec_tmp]
        if rank == p_root:
            print( ' Objective of', Sim.shape[0], 'images initialized. Beginning tests.' )
    
        comm.barrier()
        run_LTLG_experiments(objective, k_vals_vec, filepath_string, experiment_string, comm, rank, size, algo=algoIn, nthreads=nthreads)
    
    if rank == p_root:
        print ('\n\nALL EXPERIMENTS COMPLETE, total minutes elapsed =', (datetime.now()-start_runtime).total_seconds()/60.0,'\n\n')
