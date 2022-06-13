import numpy as np
import pandas as pd
from icecream import ic
from context.domains import Dataset
from context.models import Model
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier


class TitanicModel(object):
    model = Model()
    dataset = Dataset()

    def preprocess(self, train_fname, test_fname) -> object:
        this = self.dataset
        that = self.model
        # feature = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked']
        this.train = that.new_dframe(train_fname)
        this.test = that.new_dframe(test_fname)
        this.id = this.test['PassengerId']
        this.label = this.train['Survived']
        # Entity에서 Object로
        this.train = this.train.drop('Survived', axis=1)
        this = self.drop_feature(this, 'SibSp', 'Parch', 'Ticket', 'Cabin')
        this = self.extract_title_from_name(this)
        title_mapping = self.remote_duplicate(this)
        this = self.title_nominal(this, title_mapping)
        this = self.drop_feature(this, 'Name')
        this = self.sex_nominal(this)
        this = self.drop_feature(this, 'Sex')
        this = self.embarked_nominal(this)
        this = self.age_ratio(this)
        this = self.drop_feature(this, 'Age')
        this = self.fare_ratio(this)
        this = self.drop_feature(this, 'Fare')
        this = self.pclass_ordinal(this)

        # k_fold = self.create_k_fold()
        # accuracy = self.get_accuracy(this, k_fold)
        # ic(accuracy)
        # self.df_info(this)
        return this

    def learning(self, train_fname, test_fname):
        this = self.preprocess(train_fname, test_fname)
        k_fold = self.create_k_fold()
        ic(f'사이킷런 알고리즘 정확도: {self.get_accuracy(this, k_fold)}')
        self.submit(this)

    @staticmethod
    def submit(this):
        clf = RandomForestClassifier()
        clf.fit(this.train, this.label)
        prediction = clf.predict(this.test)
        pd.DataFrame({'PassengerId': this.id, 'Survived': prediction}).to_csv('./save/submission.csv', index=False)

    @staticmethod
    def df_info(this):
        [ic(f'{i.info()}') for i in [this.train, this.test]]
        ic(this.train.head(10))
        ic(this.test.head(10))

    @staticmethod
    def null_check(this):
        [ic(f'{i.isnull().sum()}') for i in [this.train, this.test]]

    @staticmethod
    def drop_feature(this, *feature) -> object:
        # for i in [this.train, this.test]:
        #     for j in feature:
        #         i.drop(j, axis=1, inplace=True)

        [i.drop(j, axis=1, inplace=True) for j in feature for i in [this.train, this.test]]
        return this

    @staticmethod
    def kwargs_sample(**kwargs) -> None:            # self.kwargs_sample(key='value', key2='value2')
        print(f'kwargs 타입: {type(kwargs)}')        # kwargs 타입: <class 'dict'>
        print(kwargs)                               # {'key': 'value', 'key2': 'value2'}
        [print(f'{i} is {j}') for i, j in kwargs.items()]

    '''
    
    Categorical vs Quantitative
    Cate -> nominal(이름) vs ordinal(순서)
    Quan -> interval(상대적) vs ratio(절대적)
    
    '''

    @staticmethod
    def extract_title_from_name(this) -> object:
        combine = [this.train, this.test]
        for dataset in combine:
            dataset['Title'] = dataset.Name.str.extract('([A-Za-z]+)\.', expand=False)
        return this

    @staticmethod
    def remote_duplicate(this) -> dict:
        a = set()
        # combine = [this.train, this.test]
        # for dataset in combine:
        #     a += list(set(dataset['Title']))

        [a.update(set(dataset['Title'])) for dataset in [this.train, this.test]]
        # ic(list(a))

        '''
        
        ['Mrs', 'Mme', 'Master', 'Don', 'Mr', 'Rev', 'Ms', 'Mlle', 'Miss', 'Dr', 
        'Major', 'Col', 'Capt', 'Dona', 'Countess', 'Lady', 'Jonkheer', 'Sir']
        
        Royal : ['Countess', 'Lady', 'Sir']
        Rare : ['Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Jonkheer', 'Dona', 'Mme']
        Mr : ['Mlle']
        Ms : ['Miss']
        master
        Mrs
        
        '''
        title_mapping = {'Mr': 1, 'Ms': 2, 'Mrs': 3, 'Master': 4, 'Royal': 5, 'Rare': 6}
        return title_mapping

    @staticmethod
    def title_nominal(this, title_mapping) -> object:
        combine = [this.train, this.test]
        for these in combine:
            these['Title'] = these['Title'].replace(['Countess', 'Lady', 'Sir'], 'Royal')
            these['Title'] = these['Title'].replace(['Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Jonkheer', 'Dona', 'Mme'], 'Rare')
            these['Title'] = these['Title'].replace(['Mlle'], 'Mr')
            these['Title'] = these['Title'].replace(['Miss'], 'Ms')
            # Master, Mrs 는 변화없음
            these['Title'] = these['Title'].fillna(0)
            these['Title'] = these['Title'].map(title_mapping)
            # print(dataset['Title'])
        return this

    @staticmethod
    def sex_nominal(this) -> object:
        gender_mapping = {'male': 0, 'female': 1}
        for these in [this.train, this.test]:
            these['Gender'] = these['Sex'].map(gender_mapping)
        return this

    @staticmethod
    def embarked_nominal(this) -> object:
        embarked_mapping = {'S': 1, 'C': 2, 'Q': 3}
        this.train = this.train.fillna({'Embarked': 'S'})
        for these in [this.train, this.test]:
            these['Embarked'] = these['Embarked'].map(embarked_mapping)
        return this

    @staticmethod
    def age_ratio(this) -> object:
        train = this.train
        test = this.test
        age_mapping = {'Unknown': 0, 'Baby': 1, 'Child': 2, 'Teenager': 3, 'Student': 4,
                       'Young Adult': 5, 'Adult': 6,  'Senior': 7}
        train['Age'] = train['Age'].fillna(-0.5)
        test['Age'] = test['Age'].fillna(-0.5)
        bins = [-1, 0, 5, 12, 18, 24, 35, 55, np.inf]
        labels = ['Unknown', 'Baby', 'Child', 'Teenager', 'Student', 'Young Adult', 'Adult', 'Senior']
        for these in train, test:
            these['AgeGroup'] = pd.cut(these['Age'], bins=bins, right=False, labels=labels)
            these['AgeGroup'] = these['AgeGroup'].map(age_mapping)
        return this

    @staticmethod
    def fare_ratio(this) -> object:
        this.test['Fare'] = this.test['Fare'].fillna(1)
        # this.train['FareBand'] = pd.qcut(this.train['Fare'], 4)
        # print(f'qcut 으로 bins 값 설정 {this.train["FareBand"].head()}')
        bins = [-1, 8, 18, 31, np.inf]
        labels = [1, 2, 3, 4]
        for these in [this.train, this.test]:
            these['FareBand'] = pd.cut(these['Fare'], bins, right=False, labels=labels)
        return this

    @staticmethod
    def pclass_ordinal(this) -> object:
        return this

    @staticmethod
    def create_k_fold() -> object:
        return KFold(n_splits=10, shuffle=True, random_state=0)

    @staticmethod
    def get_accuracy(this, k_fold):
        score = cross_val_score(RandomForestClassifier(), this.train, this.label,
                                cv=k_fold, n_jobs=1, scoring='accuracy')
        return round(np.mean(score)*100, 2)

