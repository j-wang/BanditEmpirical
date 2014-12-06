"""
rejection_MAB.py
James Wang
Nov 28, 2014
"""
import sqlite3
import numpy as np
import gzip
from MAB import MAB


class RejectionMAB(MAB):
    def __init__(self, db, n_rounds, context_list, arm_list, policies):
        super(RejectionMAB, self).__init__(db, n_rounds, context_list,
                                           arm_list, policies)
        self.poolarticles = self.__get_pools()
        self.user_feat = self.__get_user_feat()
        self.article_feat = self.__get_article_feat()
        self.rejects = self.__rejected()
        self.total_pulls = 0
        self.event_buffer = []
        self.feature_cache = dict()  # cache user-feature pairs

    def run(self):
        """Runs selected policies"""
        eventID = 1
        n_policies = len(self.policies)
        t_limit = np.repeat([self.rounds], n_policies)
        t_track = np.repeat([1], n_policies)

        results = {policy: {'arm_pulled': None,  # init empty
                            'context': None,
                            'choices': None,
                            'reward': None}
                   for policy in self.policy_names}
        while np.less_equal(t_track, t_limit).any():
            event = self.get_event(eventID)
            while event['pulled'] in self.rejects:  # get rid of rejects
                eventID += 1
                event = self.get_event(eventID)
            for i in range(n_policies):  # if not filled
                if t_track[i] <= self.rounds:
                    policy = self.policies[i]
                    # print 'Track advanced to {} on {}'.format(t_track[i],
                    #                                           policy.name)
                    pulled = policy.get_arm(context=event['user'],
                                            arms=event['arms'],
                                            features=event['features'])
                    if pulled == event['pulled']:  # sample = policy choice
                        t_track[i] += 1
                        policy.pull_arm(arm=pulled, feedback=event['reward'],
                                        context=event['user'],
                                        features=event['features'])
                        # record results and clear for next t+1 round
                        results[policy.name] = {'arm_pulled': pulled,
                                                'context': event['user'],
                                                'choices': event['arms'],
                                                'reward': event['reward']}
                        self.record_decision(policy.name,
                                             results[policy.name])
                        results[policy.name] = {'arm_pulled': None,
                                                'context': None,
                                                'choices': None,
                                                'reward': None}
                    else:
                        pass  # reject sample for policy
                else:
                    pass  # skip policies that are already done
            eventID += 1
        self.total_pulls = eventID

    def get_db_connection(self, db):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        return c

    def get_ctrs(self):
        self.db.execute('''SELECT cluster, displayed, AVG(click)
                           FROM event LEFT JOIN user
                           ON event.userID=user.userID
                           GROUP BY cluster, displayed''')
        res = self.db.fetchall()
        ctrs = {}
        for c, a, ctr in res:
            if ctrs.get(c) is None:
                ctrs[c] = {a: ctr}
            else:
                ctrs[c].update({a: ctr})
        return ctrs

    def get_event(self, t):
        if self.event_buffer == []:
            self.db.execute('''SELECT cluster, displayed, click, poolID
                               FROM event LEFT JOIN user
                               ON event.userID=user.userID
                               WHERE event.eventID>=? AND event.eventID<=?''',
                            (t, t + 10000))
            buff = self.db.fetchall()
            self.event_buffer = [{'user': clust, 'pulled': pull,
                                  'arms': self.poolarticles[poolID],
                                  'reward': click,
                                  'features': {aID:
                                               self.__get_feature_mat((clust,
                                                                      aID))
                                               for aID in
                                               self.poolarticles[poolID]}}
                                 for clust, pull, click, poolID
                                 in buff]
            try:
                return self.event_buffer.pop(0)
            except IndexError:
                self.__crash_salvage()
        else:
            return self.event_buffer.pop(0)

    def __get_feature_mat(self, (cluster, articleID)):
        """Caches cluster-feature pairs for us."""
        feat = self.feature_cache.get((cluster, articleID))

        if feat is None:
            feat = np.outer(self.user_feat[cluster],
                            self.article_feat[articleID])
            self.feature_cache[(cluster, articleID)] = feat

        return feat

    def __get_user_feat(self):
        self.db.execute('''SELECT cluster, AVG(feat1), AVG(feat2),
                           AVG(feat3), AVG(feat4), AVG(feat5), AVG(feat6)
                           FROM user GROUP BY cluster''')
        return {c: np.array([f1, f2, f3, f4, f5, f6]) for
                c, f1, f2, f3, f4, f5, f6 in self.db.fetchall()}

    def __get_article_feat(self):
        self.db.execute('''SELECT articleID, feat1, feat2, feat3, feat4,
                           feat5, feat6 FROM article''')
        return {a: np.array([f1, f2, f3, f4, f5, f6]) for
                a, f1, f2, f3, f4, f5, f6 in self.db.fetchall()}

    def __get_pools(self):
        pool_dict = dict()
        self.db.execute('''SELECT poolID FROM pool''')
        pools = self.db.fetchall()
        for pool in pools:  # initialize lists to hold articleIDs
            pool_dict[pool[0]] = []
        self.db.execute('''SELECT poolID, articleID FROM poolarticle''')
        pool_entries = self.db.fetchall()
        for entry in pool_entries:
            pool_dict[entry[0]].append(entry[1])

        return pool_dict

    def __rejected(self):
        self.db.execute('''SELECT articleID FROM article
                           WHERE rejected=1''')
        rejects = [art[0] for art in self.db.fetchall()]
        return rejects

    def __crash_salvage(self):
        import time
        self.output_decisions('data/crash.gz')
        print('Crashed: {}'.format(time.time()))
        print('Pulled: {}'.format(self.total_pulls))


class RejectionMABRecordSampling(RejectionMAB):
    def __init__(self, db, n_rounds, context_list, arm_list, policies):
        super(RejectionMABRecordSampling, self).__init__(db, n_rounds,
                                                         context_list,
                                                         arm_list, policies)
        self.accepted = []
        self.rejected = []

    def run(self):
        """Runs selected policies"""
        eventID = 1
        n_policies = len(self.policies)
        t_limit = np.repeat([self.rounds], n_policies)
        t_track = np.repeat([1], n_policies)

        results = {policy: {'arm_pulled': None,  # init empty
                            'context': None,
                            'choices': None,
                            'reward': None}
                   for policy in self.policy_names}
        while np.less_equal(t_track, t_limit).any():
            event = self.get_event(eventID)
            while event['pulled'] in self.rejects:  # get rid of rejects
                eventID += 1
                event = self.get_event(eventID)
            for i in range(n_policies):  # if not filled
                if t_track[i] <= self.rounds:
                    policy = self.policies[i]
                    # print 'Track advanced to {} on {}'.format(t_track[i],
                    #                                           policy.name)
                    pulled = policy.get_arm(context=event['user'],
                                            arms=event['arms'],
                                            features=event['features'])
                    if pulled == event['pulled']:  # sample = policy choice
                        self.accepted.append(pulled)
                        t_track[i] += 1
                        policy.pull_arm(arm=pulled, feedback=event['reward'],
                                        context=event['user'],
                                        features=event['features'])
                        # record results and clear for next t+1 round
                        results[policy.name] = {'arm_pulled': pulled,
                                                'context': event['user'],
                                                'choices': event['arms'],
                                                'reward': event['reward']}
                        self.record_decision(policy.name,
                                             results[policy.name])
                        results[policy.name] = {'arm_pulled': None,
                                                'context': None,
                                                'choices': None,
                                                'reward': None}
                    else:
                        self.rejected.append(pulled)  # record reject
                else:
                    pass  # skip policies that are already done
            eventID += 1
        self.total_pulls = eventID

    def output_accept_reject(self, filename):
        with gzip.open(filename, 'w') as f:
            for rec in self.accepted:
                f.write('accepted\t{}\n'.format(rec))
            for rec in self.rejected:
                f.write('rejected\t{}\n'.format(rec))
