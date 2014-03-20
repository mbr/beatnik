from itertools import count

from sqlalchemy import Column, Integer, Unicode, ForeignKey, UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import relationship, sessionmaker



# idgen_hack for sqlite
lite_id = count().next


Base = declarative_base()
Session = sessionmaker()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)

    def to_dict(self):
        # FIXME: this is a workaroundu
        return {
            'id': self.id,
            'name': self.name,
        }


class Playlist(Base):
    __tablename__ = 'playlist'
    # we use playlists as a demonstration for "sub-resources":
    # a playlist has a key consisting of a (user_id, id) tuple
    # on the url:
    #
    # /users/123/playlists/1/
    #
    # playlists are not adressable without a user

    id = Column(Integer, primary_key=True, default=lite_id)
    user_id = Column(Integer, ForeignKey(User.id), primary_key=True)
    user = relationship(User, backref='playlists')

    playlist_songs = relationship('PlaylistSong',
                                      order_by='PlaylistSong.sort_key',
                                      collection_class=ordering_list(
                                         'sort_key')
                                     )
    songs = association_proxy('playlist_songs', 'song',
        creator=lambda song, **kwargs: PlaylistSong(
            song=song, **kwargs)
    )


class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    artist = Column(Unicode)


class PlaylistSong(Base):
    __tablename__ = 'playlist_song'
    # we have a key for playlist entries, as they may be duplicate
    # and triple-integer-keys are a bit unwieldy.
    # having a key like this would probably work well when playlists
    # are running into editing conflicts
    id = Column(Integer, primary_key=True)

    song_id = Column(Integer, ForeignKey(Song.id))
    song = relationship(Song)
    playlist_id = Column(Integer, ForeignKey(Playlist.id))
    sort_key = Column(Integer)

    __table_args__ = (
        UniqueConstraint('song_id', 'playlist_id', 'sort_key'),
    )


def create_fixtures(session):
    alice = User(name='Alice')
    bob = User(name='Bob')
    cecille = User(name='Cecille')

    # some rock
    make_yourself = Song(artist='Incubus', title='Make Yourself')
    hash_pipe = Song(artist='Weezer', title='Hash Pipe')
    basket_case = Song(artist='Green Day', title='Basket Case')

    # some electronic
    verdict = Song(artist='Gui Boratto', title='The Verdict')
    android = Song(artist='Kraddy', title='Android Porn')
    concepts = Song(artist='Robert DeLong', title='Global Concepts')

    # and something entirely different
    nest = Song(artist='Captain Planet', title='Nest')

    # alice has one rock playlist
    alice_1 = Playlist(user=alice)
    alice_1.songs.append(make_yourself)
    alice_1.songs.append(hash_pipe)
    alice_1.songs.append(basket_case)

    # she really likes to listen to gui boratto in a loop
    alice_2 = Playlist(user=alice)
    alice_2.songs.append(verdict)
    alice_2.songs.append(verdict)
    alice_2.songs.append(verdict)

    # bob likes electronic music and some rock, in two playlists
    bob_1 = Playlist(user=bob)
    bob_1.songs.append(verdict)
    bob_1.songs.append(android)
    bob_1.songs.append(concepts)

    bob_2 = Playlist(user=bob)
    bob_2.songs.append(hash_pipe)

    # cecille mixes it up
    cecille_1 = Playlist(user=cecille)
    cecille_1.songs.append(basket_case)
    cecille_1.songs.append(concepts)
    cecille_1.songs.append(make_yourself)
    cecille_1.songs.append(verdict)
    cecille_1.songs.append(nest)

    session.add_all([alice, bob, cecille])
