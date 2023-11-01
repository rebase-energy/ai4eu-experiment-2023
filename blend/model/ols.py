import cvxpy as cp
import numpy as np

def weighting_least_squares_abstact(n_row,n_col):
    
    # Define variables
    x = cp.Variable(n_col, name='x')
    # Define parameters
    A = cp.Parameter((n_row, n_col), name='A')
    b = cp.Parameter((n_row), name='b')
    # Define objective
    objective = cp.Minimize(cp.sum_squares(A @ x - b))
    # Define constraints
    constraints = [0 <= x, x <= 1, cp.sum(x) == 1]
    # Define model
    m = cp.Problem(objective, constraints)
    
    return m

def weighting_least_squares_concrete(A,b):
    
    # Construct the problem.
    x = cp.Variable(np.size(A,1), name='x')
    # Define objective
    objective = cp.Minimize(cp.sum_squares(A @ x - b))
    # Define constraints
    constraints = [0 <= x, x <= 1, sum(x) == 1]
    # Define model
    m = cp.Problem(objective, constraints)
    # Solve model
    m.solve(verbose=False)
    # Get solution
    weights = x.value
    optvalue = m.value

    return weights, optvalue

def linearcombination_abstact(n_row,n_col):
    
    # Define variables
    x = cp.Variable(n_col, name='x')
    x0 = cp.Variable(1, name='x0')
    # Define parameters
    A = cp.Parameter((n_row, n_col), name='A')
    b = cp.Parameter((n_row), name='b')
    # Define objective
    objective = cp.Minimize(cp.sum_squares(A @ x + x0 - b))
    # Define model
    m = cp.Problem(objective)
    
    return m, A, b

def linearcombination_concrete(A,b):
    
    # Define variables
    x = cp.Variable(np.size(A,1), name='x')
    x0 = cp.Variable(1, name='x0')
    # Define objective
    objective = cp.Minimize(cp.sum_squares(A @ x + x0 - b))
    # Define model
    m = cp.Problem(objective)
    # Solve model
    m.solve(verbose=False)
    # Get solution
    weights = x.value
    intercept = x0.value
    optvalue = m.value
    
    return weights, intercept, optvalue