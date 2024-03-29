import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time

import operator

class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__ ( self, gb, trail, val_sh, var_sh, cc ):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck ( self ):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True

    """
        Part 1 TODO: Implement the Forward Checking Heuristic

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        Note: remember to trail.push variables before you change their domain
        Return: true is assignment is consistent, false otherwise
    """

    #removes the assignment from most recently assigned var from neighbor vars
    #in constraint network
    def removeAssignmentsFromDomain(self):

        # find constraints where variable has been changed
        for c in self.network.getModifiedConstraints():
                for variable in c.vars:
                # see if the variable has been assigned
                    if variable.isAssigned():
                        assignment = variable.getAssignment()
                        # print("Removing var assignment:")
                        # print(variable)

                        # if it has been assigned check the domains of the neighbors
                        for var_neighbor in self.network.getNeighborsOfVariable(variable):
                            # print("\n\nNeightbors:\n");
                            # print(var_neighbor);

                            #check the neighbors domain to see if it contains the assignment
                            #if contains remove it
                            if var_neighbor.domain.contains(assignment):
                                if var_neighbor.size() > 1:
                                    # print("Neighbor Domain:\n")
                                    # print(var_neighbor.domain)
                                    self.trail.push(var_neighbor)
                                    var_neighbor.domain.remove(assignment)
                                else :
                                    #contradiction
                                    return False

        return True


    def forwardChecking ( self ):

        #remove latest assignment from domain of neighbors
        if not self.removeAssignmentsFromDomain():
            return False

        return self.network.isConsistent()

    """
        Part 2 TODO: Implement both of Norvig's Heuristics

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        (2) If a constraint has only one possible place for a value
            then put the value there.

        Note: remember to trail.push variables before you change their domain
        Return: true is assignment is consistent, false otherwise
    """

    def assign_single_val_place(self):
        #loop through the constraints
        #find find assignments that only have one place


        for constraint in self.network.getConstraints():
            #incremeent count in dict if seen a key in the domain of
            #neighbor constraints
            val_dct = dict((val,0) for val in range(1, self.gameboard.N+1))
            # print(val_dct)
            dct_keys = val_dct.keys()

            # print(val_dct)

            for single_var in constraint.vars:
                #check domains and increment dict count
                for val in single_var.domain.values:
                    # print(single_var.domain.values)
                    if val in dct_keys:
                        val_dct[val] += 1


            # print(val_dct)

            #assign values that only have one value in constraint
            for possible_assignment in dct_keys:
                # contradiction
                if val_dct[possible_assignment] == 0:
                    # print("Failed. Constraint violated. Some values in domain don't exist.")
                    # print(val_dct)
                    # for const_var in constraint.vars:
                    #     print(const_var)
                    return False

                if val_dct[possible_assignment] == 1:
                    #find variable with that value
                    for assigning_var in constraint.vars:
                        if assigning_var.domain.contains(possible_assignment) and not assigning_var.isAssigned():
                                #assign the variable
                                # Store place in trail and push variable's state on trail

                                # print("assigning_var " + str(possible_assignment))
                                # print(assigning_var)

                                # for const_var in constraint.vars:
                                #     print(const_var)
                                #
                                # print("\n")
                                # self.trail.placeTrailMarker()
                                self.trail.push(assigning_var)
                                assigning_var.assignValue(possible_assignment)

                                assigning_var.setModified(False)

                                #remove from domains of neighbor vars
                                self.removeValFromNeighbors(assigning_var, possible_assignment)
                                break

    def removeValFromNeighbors(self, var, val):
        for neighbor in self.network.getNeighborsOfVariable(var):
            if neighbor.domain.contains(val):
                if neighbor.domain.size() > 1:
                    # remove the val
                    self.trail.push(neighbor)
                    neighbor.removeValueFromDomain(val)
                    neighbor.setModified(False)

    def norvigCheck ( self ):

        # forward check to eliminate assignment from neighbor_vars
        if not self.removeAssignmentsFromDomain():
            return False

        #assign values to vars in constraints with only one item in domain
        self.assign_single_val_place()

        # if not self.removeAssignmentsFromDomain():
        #     return False

        return self.network.isConsistent()

    """
         Optional TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournCC ( self ):
        return None

    # ==================================================================
    # Variable Selectors
    # ==================================================================

    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable ( self ):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
        Part 1 TODO: Implement the Minimum Remaining Value Heuristic

        Return: The unassigned variable with the smallest domain
    """
    def getMRV ( self ):
        min_domain_var = None
        min_domain_size = 100000

        # loop through all vars in ConstraintNetwork and find unassigned vars
        for var in self.network.variables:
            if not var.isAssigned():
                if var.domain.size() < min_domain_size:
                    min_domain_size = var.domain.size()
                    min_domain_var = var


        return min_domain_var


    def getVarDegree(self, var):
        #get the number of unassigned neighbors of var
        degree = 0
        var_neighbors = self.network.getNeighborsOfVariable(var)
        for neighbor_var in var_neighbors:
            if not neighbor_var.isAssigned():
                degree += 1


        return degree


    def getHighestDegreeVar(self, var_list):
        ret_var = None
        max_degree = -1

        for var in var_list:
            if ret_var == None:
                ret_var = var
                max_degree = self.getVarDegree(ret_var)
            else:
                # check to see if the current var degree greater than max
                temp_degree = self.getVarDegree(var)

                if temp_degree > max_degree:
                    ret_var = var
                    max_degree = temp_degree


        # print("highest degree: " + str(max_degree) + "\nVar:\n")
        # print(ret_var)

        return ret_var



    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with, first, the smallest domain
                and, second, the most unassigned neighbors
    """
    def MRVwithTieBreaker ( self ):
        # hold list of values with minimum domains
        var_list = []
        min_domain_size = 100000

        #loop through unassigned vars and save their domain size
        for var in self.network.variables:
            if not var.isAssigned():
                # if the var is less than min domain
                # clear list, set new domain size
                var_domain_size = var.size()

                if not var_list:
                    var_list.append(var)

                elif var_domain_size < min_domain_size:
                    var_list.clear()
                    var_list.append(var)
                    min_domain_size = var_domain_size
                #domain is equal to min domain keep in list for tie breaker
                elif var_domain_size == min_domain_size:
                    var_list.append(var)

        # print("var list:\n")
        # for var in var_list:
        #   print(var)
        # print("\n\n")

        #if var list is empty return nothing
        if not var_list:
            return None

        #if there is only a single variable return right away
        if len(var_list) == 1:
            return var_list[0]

        # there are vars with same size domain
        #use degree heuristic to break tie
        else:

            #return var with highest degree
            #ie, var involved in most constraints where other var in unassigned
            ret_var = self.getHighestDegreeVar(var_list)

            # print("Ret_var:\n")
            # print(ret_var)

            return ret_var;


    """
         Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVar ( self ):
        return None

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder ( self, v ):
        values = v.domain.values
        return sorted( values )

    """
        Part 1 TODO: Implement the Least Constraining Value Heuristic

        The Least constraining value is the one that will knock the least
        values out of it's neighbors domain.

        Return: A list of v's domain sorted by the LCV heuristic
                The LCV is first and the MCV is last
    """
    def getValuesLCVOrder ( self, v ):
        #use dict to keep track of count of values in domain
        #of neighbor variables
        lcv_dict = {}

        for value in v.getDomain().values:
            lcv_dict[value] = 0;

        for neighbor_var in self.network.getNeighborsOfVariable(v):
            for value in lcv_dict:
                # check if the key exists in the domains of other
                # vars, if it does increment count in dictionary
                if neighbor_var.getDomain().contains(value):
                    lcv_dict[value] += 1


        # print("LCV Dict:\n");
        # print(lcv_dict);
        #
        # print("Order:\n");

        #order dict and get keys
        sorted_lcv_list = sorted(lcv_dict.items(), key=operator.itemgetter(1))

        sorted_lcv_list = [i[0] for i in sorted_lcv_list]

        return sorted_lcv_list;



    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVal ( self, v ):
        return None

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve ( self ):
        if self.hassolution:
            return

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if ( v == None ):
            for var in self.network.variables:

                # If all variables haven't been assigned
                if not var.isAssigned():
                    print ( "Error" )

            # Success
            self.hassolution = True
            return

        # Attempt to assign a value
        for i in self.getNextValues( v ):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push( v )

            # Assign the value
            v.assignValue( i )

            # Propagate constraints, check consistency, recurse
            if self.checkConsistency():
                self.solve()

            # If this assignment succeeded, return
            if self.hassolution:
                return

            # Otherwise backtrack
            self.trail.undo()

    def checkConsistency ( self ):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable ( self ):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues ( self, v ):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder( v )

        if self.valHeuristics == "tournVal":
            return self.getTournVal( v )

        else:
            return self.getValuesInOrder( v )

    def getSolution ( self ):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)
