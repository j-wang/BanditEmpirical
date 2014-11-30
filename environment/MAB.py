"""
MAB.py
James Wang
Nov 28, 2014
"""
import gzip


class MAB(object):
    """Runs multi-armed bandit test."""
    results = dict()  # k=policy_name, v=dict with regret, arm_pulled, reward

    def __init__(self, db, n_rounds, context_list, arm_list, policies):
        self.db = self.get_db_connection(db)
        self.rounds = n_rounds
        self.num_contexts = len(context_list)
        self.contexts = context_list
        self.arms = arm_list
        self.policies = policies
        self.policy_names = [policy.name for policy in policies]
        self.ctr = self.get_ctrs()
        self.results = {policy: {'arm_pulled': [], 'reward': [], 'regret': []}
                        for policy in self.policy_names}

    def run(self):
        """Runs the selected policies"""
        raise NotImplementedError("This method needs to be overridden")
        # Call each policy each round

        # pass __record_decisions a dictionary with:
        # k=policy_name, v=dict with arm_pulled, context, choices, reward

        # increment self.T += 1

    def get_db_connection(self, db):
        raise NotImplementedError("This method needs to be overridden")

    def get_ctrs(self):
        """Returns dict of dicts, where {context: {arm: avg reward}}"""
        raise NotImplementedError("This method needs to be overridden")

    def get_event(self, t):
        raise NotImplementedError("This method needs to be overridden")

    def get_regret(self, policy_name):
        """
        Returns per T policy regret as list (expected regret per t).
        Specify 'all' to get regret for all policies.
        """
        return self.__get_results_attr('regret', policy_name)

    def get_pulls(self, policy_name):
        """
        Returns arms pulled by specified policy as list (arm per t).
        Specify 'all' to get regret for all policies.
        """
        return self.__get_results_attr('arms_pulled', policy_name)

    def get_rewards(self, policy_name):
        """
        Returns realized reward per round t as list.
        Specify all to get rewards per round for all policies.
        """
        return self.__get_results_attr('reward', policy_name)

    def __get_results_attr(self, attr, policy_name):
        if policy_name == 'all':
            return {policy: v[attr] for policy, v in self.results}
        else:
            return self.results[policy_name][attr]

    def record_decisions(self, results):
        """
        Record the results of decisions for all policies this round.
        Results has form of:
        {policy_name: {context, arm_pulled, reward, choices}}
        """
        for policy in self.policy_names:
            policy_results = self.results[policy]
            from_round = results[policy]
            pulled = from_round['arm_pulled']
            context = from_round['context']
            choices = from_round['choices']

            possible = {c: self.ctr[context][c] for c in choices}
            expected = possible[pulled]
            best = max(possible.values())

            policy_results['arm_pulled'].append(pulled)
            policy_results['reward'].append(from_round['reward'])
            policy_results['regret'].append(best - expected)

    def record_decision(self, policy_name, results):
        """
        Record the results of decision for a specific policy this round.
        Results has the form of:
        {context, arm_pulled, reward, choices}
        """
        policy_results = self.results[policy_name]

        pulled = results['arm_pulled']
        context = results['context']
        choices = results['choices']

        possible = {c: self.ctr[context][c] for c in choices}
        expected = possible[pulled]
        best = max(possible.values())

        policy_results['arm_pulled'].append(pulled)
        policy_results['reward'].append(results['reward'])
        policy_results['regret'].append(best - expected)

    def output_decisions(self, filename):
        """Writes out decisions to specified file."""
        with gzip.open(filename, 'wb') as f:
            f.write('policy\tT\tarm_pulled\treward\tregret\n')
            line = '{0}\t{1:d}\t{2:d}\t{3:d}\t{4:g}\n'
            for policy in self.policy_names:
                pol_values = self.results[policy]
                for i in range(len(pol_values['arm_pulled'])):
                    f.write(line.format(policy,
                                        i,
                                        pol_values['arm_pulled'][i],
                                        pol_values['reward'][i],
                                        pol_values['regret'][i]))
