import numpy as np
from scipy.optimize import minimize


# NOTE: follow the docstrings. In-line comments can be followed, or replaced.
#       Hence, those are the steps, but if it does not match your approach feel
#       free to remove.

def linear_kernel(X1, X2):
    """    Matrix multiplication.

    Given two matrices, A (m X n) and B (n X p), multiply: AB = C (m X p).

    Recall from hw 1. Is there a more optimal way to implement using numpy?
    :param X1:  Matrix A
    type       np.array()
    :param X2:  Matrix B
    type       np.array()

    :return:    C Matrix.
    type       np.array()
    """

    return X1@X2


def nonlinear_kernel(X1, X2, sigma=0.5):
    """
     Compute the value of a nonlinear kernel function for a pair of input vectors.

     Args:
         X1 (numpy.ndarray): A vector of shape (n_features,) representing the first input vector.
         X2 (numpy.ndarray): A vector of shape (n_features,) representing the second input vector.
         sigma (float): The bandwidth parameter of the Gaussian kernel.

     Returns:
         The value of the nonlinear kernel function for the pair of input vectors.

     """


    # Compute the Euclidean distance between the input vectors
    dist = np.linalg.norm(X1 - X2)
    # Compute the value of the Gaussian kernel function
    gaussian = np.exp(-dist ** 2 / (2 * (sigma ** 2)))
    # Return the kernel value
    return gaussian


def objective_function(X, y, a, kernel):
    """
    Compute the value of the objective function for a given set of inputs.

    Args:
        X (numpy.ndarray): An array of shape (n_samples, n_features) representing the input data.
        y (numpy.ndarray): An array of shape (n_samples,) representing the labels for the input data.
        a (numpy.ndarray): An array of shape (n_samples,) representing the values of the Lagrange multipliers.
        kernel (callable): A function that takes two inputs X and Y and returns the kernel matrix of shape (n_samples, n_samples).

    Returns:
        The value of the objective function for the given inputs.
    """

    
    # Reshape a and y to be column vectors
    a = a.reshape(-1, 1) #a is the Lagrange multipliers
    y = y.reshape(-1, 1) #y is the labels for the input data
    # Compute the value of the objective function
    # The first term is the sum of all Lagrange multipliers
    term1 = np.sum(a)
    # The second term involves the kernel matrix, the labels and the Lagrange multipliers
    term2 = np.sum((a * y) @ (a * y).T*kernel(X, X.T))
    return term1 - 0.5*term2


class SVM(object):
    """
         Linear Support Vector Machine (SVM) classifier.

         Parameters
         ----------
         C : float, optional (default=1.0)
             Penalty parameter C of the error term.
         max_iter : int, optional (default=1000)
             Maximum number of iterations for the solver.

         Attributes
         ----------
         w : ndarray of shape (n_features,)
             Coefficient vector.
         b : float
             Intercept term.

         Methods
         -------
         fit(X, y)
             Fit the SVM model according to the given training data.

         predict(X)
             Perform classification on samples in X.

         outputs(X)
             Return the SVM outputs for samples in X.

         score(X, y)
             Return the mean accuracy on the given test data and labels.
         """

    def __init__(self, kernel=nonlinear_kernel, C=1.0, max_iter=1e3):
        """
        Initialize SVM

        Parameters
        ----------
        kernel : callable
          Specifies the kernel type to be used in the algorithm. If none is given,
          ‘rbf’ will be used. If a callable is given it is used to pre-compute 
          the kernel matrix from data matrices; that matrix should be an array 
          of shape (n_samples, n_samples).
        C : float, default=1.0
          Regularization parameter. The strength of the regularization is inversely
          proportional to C. Must be strictly positive. The penalty is a squared l2
          penalty.
        """
        self.kernel = kernel
        self.C = C
        self.max_iter = max_iter
        self.a = None
        self.w = None
        self.b = None

    def fit(self, X, y):
        """
        Fit the SVM model according to the given training data.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features) or (n_samples, n_samples)
          Training vectors, where n_samples is the number of samples and n_features 
          is the number of features. For kernel=”precomputed”, the expected shape 
          of X is (n_samples, n_samples).

        y : array-like of shape (n_samples,)
          Target values (class labels in classification, real numbers in regression).

        Returns
        -------
        self : object
          Fitted estimator.
        """
        # save alpha parameters, weights, and bias weight
        #self.a = None
        #self.w = None
        #self.b = None
        

        
        # constraints = ({'type': 'ineq', 'fun': ...},
        #                {'type': 'eq', 'fun': ...})
      
        constraints = ({'type': 'ineq', 'fun': lambda a: a},
                        {'type': 'ineq', 'fun': lambda a: self.C - a},
                        {'type': 'eq', 'fun': lambda a: np.sum(a * y)})
        

        
        # res = minimize(...)
        # self.a = ...
        res = minimize(fun=lambda a: -objective_function(X, y, a, self.kernel),
                   x0=np.zeros(X.shape[0]),
                   method='SLSQP',
                   constraints=constraints,
                   options={'maxiter': self.max_iter})
        self.a = res.x
        

        
        # self.w = ...
        self.w = np.sum(self.a * y * X.T, axis=1)
        

        
        # self.b = ...
        support_vectors = self.a > 0
        self.b = np.mean(y[support_vectors] - np.dot(X[support_vectors], self.w))

        return self

    def predict(self, X):
        """
        Perform classification on samples in X.

        For a one-class model, +1 or -1 is returned.

        Parameters
        ----------
        X : {array-like, sparse matrix} of shape (n_samples, n_features) or (n_samples_test, n_samples_train)

        Returns
        -------
        y_pred : ndarray of shape (n_samples,)
          Class labels for samples in X.
        """

        y_pred = np.dot(X, self.w) + self.b
        y_pred[y_pred > 0] = 1
        y_pred[y_pred < 0] = -1
        return y_pred
        
    


    def score(self, X, y):
        """
        Return the mean accuracy on the given test data and labels. 

        In multi-label classification, this is the subset accuracy which is a harsh 
        metric since you require for each sample that each label set be correctly 
        predicted.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
          Test samples.
        y : array-like of shape (n_samples,) or (n_samples, n_outputs)
          True labels for X.

        Return
        ------
        score : float
          Mean accuracy of self.predict(X)
        """

        return np.mean(self.predict(X) == y)

        return None
