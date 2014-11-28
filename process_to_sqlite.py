"""
process_to_sqlite.py
James Wang
Nov 24, 2014
"""
import gzip
import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import (create_engine, Column, Integer, Float,
                        Boolean, DateTime, ForeignKey, MetaData,
                        PrimaryKeyConstraint)


class UniqueDict(dict):
    def __setitem__(self, key, value):
        if key in self:
            raise KeyError("Key already exists.")
        elif value in self.values():
            raise ValueError("Value already exists.")
        else:
            dict.__setitem__(self, key, value)

    def update(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError("update expected at most 1 "
                            "arguments, got %d" % len(args))
        other = dict(*args, **kwargs)
        for key in other:
            self[key] = other[key]


class ProcessWebscope(object):
    """Processes Webscope Data"""
    Base = declarative_base()

    class User(Base):
        __tablename__ = 'user'

        userID = Column(Integer, primary_key=True)
        cluster = Column(Integer)
        feat1 = Column(Float)
        feat2 = Column(Float)
        feat3 = Column(Float)
        feat4 = Column(Float)
        feat5 = Column(Float)
        feat6 = Column(Float)
        events = relationship('Event', backref='user')

    class Article(Base):
        __tablename__ = 'article'

        articleID = Column(Integer, primary_key=True, autoincrement=False)
        rejected = Column(Boolean)
        feat1 = Column(Float)
        feat2 = Column(Float)
        feat3 = Column(Float)
        feat4 = Column(Float)
        feat5 = Column(Float)
        feat6 = Column(Float)
        pools = relationship('PoolArticle', backref='article')

    class Pool(Base):
        __tablename__ = 'pool'

        poolID = Column(Integer, primary_key=True)
        articles = relationship('PoolArticle', backref='pool')
        events = relationship('Event', backref='pool')

    class PoolArticle(Base):
        __tablename__ = 'poolarticle'
        __table_args__ = (PrimaryKeyConstraint('poolID', 'articleID',
                                               name='poolarticle_pk'),)

        poolID = Column(Integer, ForeignKey('pool.poolID'))
        articleID = Column(Integer, ForeignKey('article.articleID'))

    class Event(Base):
        __tablename__ = 'event'

        eventID = Column(Integer, primary_key=True)
        datetime = Column(DateTime)
        displayed = Column(Integer, ForeignKey('article.articleID'))
        click = Column(Integer)
        poolID = Column(Integer, ForeignKey('pool.poolID'))
        userID = Column(Integer, ForeignKey('user.userID'))

    def __init__(self, db, log=True):
        self.engine = create_engine('sqlite:///' + db, echo=log)
        metadata = MetaData(bind=self.engine)
        metadata.reflect()

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        if len(metadata.sorted_tables) == 0:
            self.Base.metadata.create_all(self.engine)
            self.pool = dict()
            self.article_set = set()
        else:
            # get metadata and article pool if the database exists
            self.Base = declarative_base(metadata=metadata)
            self.pool = self.__get_pool_dict()
            self.article_set = self.__get_article_set()

    def process_file(self, filename, num_lines=False, skip_lines=0):
        """Processes a given Webscope file (in gzip format) into SQLite db."""
        counter = 0
        f = gzip.open(filename)
        if not num_lines:
            # read lines until done
            processing = "all"
            for line in f:
                if counter >= skip_lines:
                    self.parse_text(line)
                else:
                    counter += 1
        else:
            # read specified lines
            processing = '{0:d}'.format(num_lines)
            for i in range(num_lines):
                if counter >= skip_lines:
                    self.parse_text(i)
                else:
                    counter += 1

        print('Done processing file ({} lines).'.format(processing))
        f.close()

    def parse_text(self, string):
        """Parse individual lines"""
        l = string.split(' ')
        max_idx, max_val = max(enumerate(map(lambda x: float(x[2:]),
                                             l[4:9])), key=lambda i: i[1])
        user = self.User(feat2=float(l[4][2:]), feat3=float(l[5][2:]),
                         feat4=float(l[6][2:]), feat5=float(l[7][2:]),
                         feat6=float(l[8][2:]), feat1=float(l[9][2:]),
                         cluster=max_idx + 2)  # cluster correspond to feat

        self.session.add(user)
        self.session.flush()  # gives us the primary key for user
        current_userID = user.userID

        # read in set of articles
        article_dict = dict()  # key is ID, value is list of features 2-6, 1
        temp_dict = dict()
        for i in l[10:]:
            if i[:1] == '|':
                if temp_dict != dict():  # if we have existent article
                    article_dict[temp_dict['id']] = temp_dict['feat']
                    temp_dict = dict()
                temp_dict['id'] = int(i[1:])
                temp_dict['feat'] = []
            else:
                feat_num = int(i[:1])
                feat_current = float(i[2:])

                if feat_num == 7:  # reject bad data
                    temp_dict['feat'] = [0, 0, 0, 0, 0, 0]
                else:
                    temp_dict['feat'].append(feat_current)

        if temp_dict != dict():  # add last article
            article_dict[temp_dict['id']] = temp_dict['feat']

        # add articles to db table
        current_articles = []
        for k, v in article_dict.items():
            if k in self.article_set:
                pass
            else:
                if v == [0, 0, 0, 0, 0, 0]:
                    reject_feat = True
                else:
                    reject_feat = False

                article = self.Article(articleID=k, rejected=reject_feat,
                                       feat2=v[0], feat3=v[1], feat4=v[2],
                                       feat5=v[3], feat6=v[4], feat1=v[5])
                self.session.add(article)
                self.session.flush()
                self.article_set.add(k)

            current_articles.append(k)

        # check if article pool already exists (to get poolID)
        current_pool = set(current_articles)
        if current_pool in self.pool.values():
            for k, v in self.pool.items():
                if v == current_pool:
                    current_poolID = k
                    break
        else:
            pool = self.Pool()  # new pool
            self.session.add(pool)
            self.session.flush()
            current_poolID = pool.poolID

            for aID in current_articles:  # add to db
                poolarticle = self.PoolArticle(poolID=current_poolID,
                                               articleID=aID)
                self.session.add(poolarticle)
                self.session.flush()

            self.pool[current_poolID] = current_pool  # update tracked pools

        event = self.Event(datetime=datetime.datetime.fromtimestamp(int(l[0])),
                           poolID=current_poolID, userID=current_userID,
                           displayed=int(l[1]), click=int(l[2]))
        self.session.add(event)

        self.session.commit()
        return {'event': event, 'user': user,
                'pool': {'id': current_poolID, 'articles': current_pool}}

    def __get_pool_dict(self):
        """Gets the articlePool Dict if the db already exists"""
        # k = poolID, v = set of articleIDs
        pool_dict = dict()

        all_pools = self.session.query(self.Pool).all()
        for p in all_pools:
            pool_dict[p.poolID] = set()
            a = self.session.query(self.PoolArticle).filter_by(poolID=p.poolID)
            for article in a:
                pool_dict[p.poolID].add(article.articleID)

        return pool_dict

    def __get_article_set(self):
        """Gets set of articles in database"""
        art_set = set()

        all_articles = self.session.query(self.Article).all()
        for article in all_articles:
            art_set.add(article.articleID)

        return art_set


def main():
    pass


if __name__ == "__main__":
    main()
