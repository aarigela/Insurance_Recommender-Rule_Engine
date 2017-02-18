
'''

Creating a Rule-Based Expert System

Authors:

	Aaditya Arigela

INSTRUCTIONS:

	Simply run command :- python RuleEngine.py

Future work:

	- Write advanced rules to enhance Knowledge base
	- Develop a user interface to produce a deliverable system.
	
	
NOTE: The rules are written in plain English.

'''

#Global variables
question_mode = False
questions_asked = []

#Rules data 
rules = [('life-stage-retirement',
			['is-equal age ?person 75'],
			['is-in-life-stage ?person retirement']),
		 ('life-stage-not-retirement',
			['is-equal age ?person 45'],
			['is-in-life-stage ?person retirement']),
		 ('no-insurance-implies-basic-insurance-coverage-inadequate',
			['has-taken health-insurance ?person no'],
			['is-b-insurance-coverage-adequate ?person no']),
		 ('married-implies-life-insurance',
			['is-married? person yes'],
			['should-have-h-insurance ?person yes']),
		 ('married-implies-life-insurance',
			['has-children? person yes'],
			['should-have-h-insurance ?person yes']),
		 ('no-l-insurance-implies-basic-insurance-coverage-inadequate',
			['has-l-insurance ?person no, should-have-l-insurance ?person yes'],
			['is-b-insurance-coverage-adequate ?person no']),
		 ('no-l-insurance-implies-basic-insurance-coverage-inadequate',
			['has-h-insurance ?person yes, has-l-insurance ?person yes'],
			['is-b-insurance-coverage-adequate ?person yes']),
		 ('low-basic-ins-coverage-implies-no-investment',
			['is-b-insurance-coverage-adequate ?person no'],
			['fund-category ?person none']),
		 ('savings-implies-money-market-investment',
			['has-savings- ?person yes'],
			['fund-category ?person money-market']),
		 ('invest-in-conservative-growth-funds',
			['is-less-than years-to-retire ?person 10'],
			['fund-category ?person conservative-growth']),
		 ('invest-in-gi-funds',
			['is-greater-than years-to-retire ?person 10, is-less-than years-to-retire ?person 20'],
			['fund-category ?person conservative-growth']),
		 ('late-retirement-plan',
			['has-investment-goal ?person retirement',
			'is-greater-than years-for-retirement ?person 20'],
			['Category-of-Funds ?person Growth&Income']),
		 ('investment-goal-child-education',
			['has-investment-goal ?person child-education',
			'is-less-than age ?oldest-child 7'],
			['Category-of-Funds ?person Growth&Income']),
		 ('investment goal is childs education',
			['has-investment-goal ?person child-education',
			'is-greater-than age ?oldest-child 7'],
			['Category-of-Funds ?person Conservative-Growth']),
		 ('no-pension-no-retirement-implies-retirement-investment',
			['pension ?person No',
			'individual-Retirement-Account ?person No',
			'is-less-than number-of-years-for-retirement ?person 10'],
			['has-investment-goal ?person retirement']),
		 ('education-fund-not-avail-implies-education-investment',
			['going-to ?child college',
			'education-funded ?child No'],
			['has-investment-goal ?child child-education']),
		 ('son-is-child',
			['is-son-of ?A ?B'],
			['is-child-of ?A ?B']),
		 ('daughter-is-child',
			['is-daughter-of ?A ?B'],
			['is-child-of ?A ?B'])]	

			
#Working Memory			
wm = [
	  'has-investment-goal Monica retirement',
	  'is-equal years-to-retire Monica 25 ',
	  'is-equal current-savings Jason three-times-Monthly-Salary',
	  'investment-goal James child-education',
	  'is-equal age-of-oldest-child James 5',
	  'is-daughter-of Mary James',
	  'investment-goal Harry retirement',
	  'is-equal years-to-retire Harry 7',
	  'going-to Mary college',
	  'education-funded Mary No'
	  ]
			
			
'''
Utility function to test whether a given string is a variable
'''			
def var(obj):
    if obj[0] == '?' and obj.find(' ') is -1: #adding check for space to avoid any vague input
        return True
    return False

	
'''
This function returns the pattern with the variables from the substitution substituted into it
'''
def substitute(substitution, pattern):
    no_substitutions = False
	
    while no_substitutions is False:
        old_pattern = pattern
		
        for token in substitution:
            if var(token[0]):
                pattern = pattern.replace(token[0], token[1])

        if old_pattern == pattern:
            no_substitutions = True

    return pattern


'''
This function checks for and returns either an updated substitution, possibly the empty list or False
'''
def unify(pattern1, pattern2, substitution):

    if pattern1 == pattern2:
        return substitution

    #The below two checks perform unification if one of the two patterns fit in properly for rule matching.
    #Either of the form - {p1,p2} or {p2,p1}

    elif var(pattern1):
        return unify_var(pattern1, pattern2, substitution)
    elif var(pattern2):
        return unify_var(pattern2, pattern1, substitution)
    elif pattern1.find(' ') is -1 or pattern2.find(' ') is -1:
        return False
		
    else:
        pattern1_list = pattern1.split(' ')
        pattern2_list = pattern2.split(' ')

        for word in pattern1_list:
            if not var(word) and not var(pattern2_list[pattern1_list.index(word)]) and word != pattern2_list[pattern1_list.index(word)]:
                return False

        for word in pattern2_list:
            if not var(word) and not var(pattern1_list[pattern2_list.index(word)]) and word != pattern1_list[pattern2_list.index(word)]:
                return False

        for word in pattern1_list:
            result = unify(word, pattern2_list[pattern1_list.index(word)], substitution)

            if result is False:
                return False
            substitution = substitution + result

        return list(set(substitution))

'''
This function performs unification if one of the two patterns fit in properly for rule matching.
'''
def unify_var(var, pat, substitution):
    for token in substitution:

        #Perform unification for the immediate next token if current token is a variable.

        if token[0] == var:
            return unify(token[1], pat, substitution)

    result = substitute(substitution, pat)
	
    if result.find(var) > -1:
        return False

	#Get the appropriate binding
    binding = (var, pat)

    #If binding does not exist in substitutions then insert it.

    if binding not in substitution:
        substitution.append((var, pat))
		
    return substitution


'''
This function computes all possible new states which can be reached by matching the first antecedent in the list
'''
def match_antecedent(anteceds, wm, sub):
    antec = anteceds[0]

    def ma_helper(states, wm_left):
        # If wm_left is empty return states.
        if wm_left == []:
            return states

        # Otherwise attempt to unify antec with next pattern in wm_left in the context of sub.
        else:
            unification = unify(antec, wm_left[0], sub)

            #Depending on unification fails or succeeds, call ma_helper accordingly
            if unification is False:
                return ma_helper(states, wm_left[1:])
            states.append((anteceds[1:], unification))
            return ma_helper(states, wm_left[1:])

    return ma_helper([], wm)


'''
This function generates the list of new patterns (which is not added to the working memory yet)
'''
def execute(subsitution, rhs_rules, wm):
    new_patterns = []

    #Loop through the rules in RHS, get new patterns and if not found in WM, then append them
    for consequent in rhs_rules:
        new_pattern = substitute(subsitution, consequent)
        if new_pattern not in wm:
            new_patterns.append(new_pattern)

    return new_patterns


'''
Based on exhaustive depth-first search this function finds all possible ways to satisfy the rule using patterns in the working memory.
'''
def match_rule(name, lhs, rhs, wm):
    global question_mode
    global questions_asked
    print('\nAttempting to match rule "' + name + '":')

    def mr_helper(queue, new_wm):
        # if the queue is empty, return new_wm
        if queue == []:
            return new_wm
        else:
            #examine the first item in the queue
            state1 = queue[0]

            #If state1 has no antecedents then state1 is a goal state => the rule is matched
            if state1[0] == []:
                new_patterns = execute(state1[1], rhs, wm)

                #mr_helper applied to the rest of the queue, appending new WM assertions that "execute" returned.
                return mr_helper(queue[1:], new_patterns)

            #if state1 has antecedents, apply "match_antecedent" to them along with WM and the substitutions in state1.
            new_states = match_antecedent(state1[0], wm, state1[1])

            #Depending on new states are returned or not, call "mr_helper"
            if new_states == []:
                return mr_helper(queue[1:], new_wm)

            queue.pop(0)

            for state in new_states:
                queue.insert(0, state)

            return mr_helper(queue, wm)

    extra_assersions = []

    #Working of Question Mode
    if question_mode:

        #Find potential assertions to be added to the Working memory
        for fact in wm:
            min_one_match_found = False
            unmatched_lhss = []
            matched_lhss = []
            unmatched_list = []
            temp = []

            #For each LHS (antecedent), see if any inference can be generated
            #This means checking for all possible conditions as described in the Assignment.

            for each_lhs in lhs:
                unification = unify(each_lhs, fact, [])
                if unification:
                    min_one_match_found = True
                    if unification != []:
                        matched_lhss.append(substitute(unification, each_lhs))
                        unif_temp = unification
                else:
                    unmatched_lhss.append(substitute(temp, each_lhs))

            #If at least one match is found, loop through all unmatched LHSs and append to a list of unmatched LHS

            if min_one_match_found:
                for each_lhs in unmatched_lhss:
                    unmatched_list.append(substitute(unif_temp, each_lhs))

                #For all potential assertions, ask the user if he/she is willing to add it to the WM.
                for unknown_assertion in unmatched_list:
                    if unknown_assertion not in questions_asked and unknown_assertion not in wm and '?' not in unknown_assertion:
                        response = ''
                        while response not in ('Yes', 'No', 'Quit'):
                            response = input('\n"' + unknown_assertion + '"' + ' was not found in WM.\n\nWould you like to add it? (Yes / No / Quit): ')
                            if response not in ('Yes', 'No', 'Quit'):
                                print('Invalid Input.')

                        #In case of Yes, add the assertion along with the information that it is of positive form or negative
                        if response == 'Yes':
                            extra_assersions.append(unknown_assertion)
                            if unknown_assertion[-9:] == ' positive':
                                questions_asked.append(unknown_assertion)
                                questions_asked.append(unknown_assertion[:-9] +' negative')
                            else:
                                questions_asked.append(unknown_assertion)
                                questions_asked.append(unknown_assertion[:-9] +' positive')

                        #Continue with the next inference
                        elif response == 'No':
                            questions_asked.append(unknown_assertion)
                            continue

                        #Terminate the inference process
                        elif response == 'Quit':
                            print_wm(wm)
                            exit()
                        elif unknown_assertion[-9] == ' positive':
                            questions_asked.append(unknown_assertion)
                        else:
                            questions_asked.append(unknown_assertion[:-9] + ' negative')

    #Generate the final list of assertions to be added to the WM
    assertions_temp = mr_helper(match_antecedent(lhs, wm, []), [])
    assertions_temp = assertions_temp + extra_assersions
    assertions = []
    for assertion in assertions_temp:
        if assertion not in wm:
            assertions.append(assertion)

    #Print appropriate message to the user
    if assertions == []:
        print('Failing...')
    else:
        print('Match succeeds !\n')
        print('Adding assertions to WM:')
        for assertion in assertions:
            print('"' + assertion + '"')

    return assertions


'''
This function returns a list of new patterns resulting from matching rules.
'''
def match_rules(rules, wm):
    new_patterns = []
	
    for rule in rules:
        new_patterns.extend(match_rule(rule[0], rule[1], rule[2], wm))

    return new_patterns


'''
run_ps : 	Returns updated working memory.
			Calls match_rules repeatedly, appending the new patterns that are returned, onto the working memory, until no new patterns are found
'''
def run_ps(rules, wm, q_mode):
    global question_mode
    has_no_new_pattern = True
    i = 1

	#Serach for potential new assertions and if any found then add them to the WM
    while has_no_new_pattern is False:
        print('CYCLE' + str(i))
        i += 1
		
        print('\nCURRENT WORKING MEMORY:')
        for fact in wm:
            print('"' + fact + '"')

        new_patterns = match_rules(rules, wm)
        if new_patterns == []:
            has_no_new_pattern = True
            print('\nNO CHANGES ON LAST CYCLE, HALTING')
        else:
            wm.extend(new_patterns)
            print('\n')

    print_wm(wm)

	#In Question mode, re-run with the possibility of antecedent matches
    #Through forward chaining, this can lead to multiple rules being matched subsequently leading to many new assertions.

    if q_mode:
        has_no_new_pattern = False
        question_mode = True
		
        print('\n\n\n\nQUESTION MODE ENABLED\n')
		
        while has_no_new_pattern is False:
            print('CYCLE ' + str(i))
            i += 1
            print('\nCURRENT WORKING MEMORY:')
            for fact in wm:
                print('"' + fact + '"')

            new_patterns = match_rules(rules, wm)
            if new_patterns == []:
                has_no_new_pattern = True
                print('\nNO CHANGES ON LAST CYCLE, HALTING')
            else:
                wm.extend(new_patterns)
                print('\n')

        print_wm(wm)
    return wm

	
#Print Final WM
def print_wm(wm):
    print('\n\nFINAL WORKING MEMORY:\n')
    for fact in wm:
        print('"' + fact + '"')


#Driver Function
def main():
    response = ''
    while response not in ('Y', 'N'):
        response = input('\nRun with question mode ON ? (Y / N): ')
        if response is 'Y':
            run_ps(rules, wm, True)
        elif response is 'N':
            run_ps(rules, wm, False)
        else:
            print('Invalid input.')


if __name__ == '__main__':
    main()