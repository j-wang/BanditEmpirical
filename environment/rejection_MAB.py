"""
rejection_MAB.py
James Wang
Nov 28, 2014
"""
import sqlite3
import numpy as np
from MAB import MAB


class RejectionMAB(MAB):
    def __init__(self, db, n_rounds, context_list, arm_list, policies):
        super(RejectionMAB, self).__init__(db, n_rounds, context_list,
                                           arm_list, policies)
        self.user_feat = self.__get_user_feat()
        self.article_feat = self.__get_article_feat()
        self.total_pulls = 0

    def run(self):
        """Runs selected policies"""
        eventID = 1
        for t in range(self.rounds):
            policy_list = list(self.policies)
            results = {policy: {'arm_pulled': None,  # init empty
                                'context': None,
                                'choices': None,
                                'reward': None}
                       for policy in self.policy_names}
            while policy_list != []:  # while policies unexecuted
                event = self.get_event(eventID)
                for policy in policy_list:
                    pulled = policy.get_arm(context=event['user'],
                                            arms=event['arms'],
                                            features=event['features'])
                    if pulled == event['pulled']:  # sample = policy choice
                        policy_list.remove(policy)
                        policy.pull_arm(arm=pulled, feedback=event['reward'],
                                        context=event['user'])
                        results[policy.name] = {'arm_pulled': pulled,
                                                'context': event['user'],
                                                'choices': event['arms'],
                                                'reward': event['reward']}
                    else:
                        pass  # reject sample for policy
                eventID += 1
            self.total_pulls = eventID
            self.record_decisions(results)

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
        self.db.execute('''SELECT cluster, displayed, click, poolID
                           FROM event LEFT JOIN user
                           ON event.userID=user.userID
                           WHERE event.eventID=?''', (t,))
        cluster, pull, click, poolID = self.db.fetchone()
        self.db.execute('''SELECT articleID FROM poolarticle
                           WHERE poolID=?''', (poolID,))
        pool = [article[0] for article in self.db.fetchall()]
        features = {artID: np.outer(self.user_feat[cluster],
                                    self.article_feat[artID])
                    for artID in pool}
        return {'user': cluster, 'pulled': pull, 'arms': pool,
                'reward': click, 'features': features}

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
