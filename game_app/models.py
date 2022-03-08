from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from game_app import db


class Game(db.Model):

    __tablename__ = "game"

    game_id = Column('game_id', Integer, primary_key=True)
    game_code = Column('game_code', String(10))

    def __repr__(self):
        return '<Game {}>'.format(self.game_code)


class Player(db.Model):

    __tablename__ = "player"

    player_id = Column('player_id', Integer, primary_key=True)
    username = Column('username', String(15))
    game_id = Column(Integer, ForeignKey('game.game_id'))
    avatar_id = Column(Integer, ForeignKey('avatar.avatar_id'))

    def __repr__(self):
        return '<Player {}>'.format(self.username)


class Word(db.Model):

    __tablename__ = "word"

    word_id = Column('word_id', Integer, primary_key=True)
    word = Column('word', String(50))

    def __repr__(self):
        return '<Word {}>'.format(self.word)


class Definition(db.Model):

    __tablename__ = "definition"

    definition_id = Column('definition_id', Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('player.player_id'))
    game_id = Column(Integer, ForeignKey('game.game_id'))
    word_id = Column(Integer, ForeignKey('word.word_id'))
    definition = Column('definition', Text)
    is_def = Column('is_def', Boolean, default=False)
    points = Column('points', Integer, default=0)

    def __repr__(self):
        return '<Definition {}>'.format(self.definition)


class WordGame(db.Model):

    __tablename__ = "word_game"

    word_game_id = Column('word_game_id', Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('game.game_id'))
    word_id = Column(Integer, ForeignKey('word.word_id'))
    word_num = Column('word_num', Integer)

    def __repr__(self):
        return '<WordGame {}>'.format(self.word_num)


class Vote(db.Model):

    __tablename__ = "vote"

    vote_id = Column('vote_id', Integer, primary_key=True)
    voter = Column(Integer, ForeignKey('player.player_id'))
    vote_receiver = Column(Integer, ForeignKey('player.player_id'))
    definition_id = Column(Integer, ForeignKey('definition.definition_id'))
    game_id = Column(Integer, ForeignKey('game.game_id'))

    def __repr__(self):
        return '<Voter {} Vote Receiver {}>'.format(self.voter, self.vote_receiver)


class Avatar(db.Model):

    __tablename__ = "avatar"

    avatar_id = Column('avatar_id', Integer, primary_key=True)
    path = Column('path', String(50))

    def __repr__(self):
        return '<Avatar ID {} Path {}>'.format(self.avatar_id, self.path)
