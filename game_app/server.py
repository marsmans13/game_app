from game_app import app
from game_app import db
from flask import (
    flash, redirect, render_template, session, url_for, request
)
from PyDictionary import PyDictionary
import string
import random
from game_app.models import Game, Player, Word, Definition, WordGame, Vote, Avatar


WAIT_VOTE_MESSAGES = ["Go pee or something.", "Get started on that manifesto you've been meaning to write.",
                      "Stretch or something.", "Scream into the void for a minute.",
                      "Look up where candle wax goes when you burn a candle.", "Get a snack. This game takes forever.",
                      "Call your <insert family member here>.", "Clean your screen.",
                      "Let out that fart. No one will hear it.", "Plan your enemy's demise."]

WAIT_RESULTS_MESSAGES = ["Drink some water.", "It's probably Tim--he's taking this way too seriously.",
                         "Do a jumping jack.", "Challenge your dog to a staring contest.", "Update your will.",
                         "Go get your coffee out of the microwave.", "Pick that scab. You've earned it.",
                         "Tell Muriel to just pick a damn definition.", "Unclench your jaw.",
                         "Admire this super awesome website that has no glitches whatsoever and don't look too closely at it."]


@app.route('/home', methods=['POST', 'GET'])
def home():

    if request.method == 'POST':

        if request.form.get('add_word'):
            print('NEW WORD FROM FORM', request.form.get('add_word'))
            new_word_f = request.form.get('add_word')
            add_new_word(new_word_f)

            return redirect(url_for('home'))

        if not request.form.get('game_code'):
            username = request.form['username']
            letters = string.ascii_letters
            game_code = ''.join(random.choice(letters) for i in range(5))

            game = Game(game_code=game_code)
            db.session.add(game)
            db.session.commit()

        elif request.form.get('game_code'):
            username = request.form['username_join']
            game_code = request.form.get('game_code').strip()
            game = Game.query.filter_by(game_code=game_code).all()
            if not game:
                flash("Incorrect game code")
                return redirect(url_for('home'))
            num_players = Player.query.filter_by(game_id=game[0].game_id).all()
            if len(num_players) >= 8:
                flash("I'm sorry this game is so popular it's full :/")
                return redirect(url_for('home'))
            game = game[0]
        else:
            flash("Incorrect game code you silly goose")
            return redirect(url_for('home'))

        print("GAME: ", game)
        session['username'] = username

        existing_player = Player.query.filter_by(username=username, game_id=game.game_id).all()
        if not existing_player:
            cur_players = Player.query.filter_by(game_id=game.game_id).all()
            if cur_players:
                avatar_id = len(cur_players) + 1
            else:
                avatar_id = 1
            player = Player(username=username, game_id=game.game_id, avatar_id=avatar_id)
            db.session.add(player)
            db.session.commit()

        return redirect(url_for('create_game', game_code=game_code))

    return render_template('home.html')


def add_new_word(new_word_f):

    word = Word.query.filter_by(word=new_word_f).all()

    if not word:
        word = Word(word=new_word_f.lower())
        db.session.add(word)
        db.session.commit()

        d = PyDictionary()
        def_dict = d.meaning(new_word_f.lower())
        if not def_dict:
            return
        print("DEF FROM DICT", def_dict)
        try:
            def_key = def_dict[0]
        except Exception:
            print("Definition not found.")
            return

        definition = def_dict[def_key][0]
        print('def', definition)
        new_def = Definition(word_id=word.word_id, definition=definition, is_def=True)

        db.session.add(new_def)
        db.session.commit()

        flash(f"NEW WORD {new_word_f} ADDED")


@app.route('/create-game/<game_code>', methods=['POST', 'GET'])
def create_game(game_code):

    print('GAME CODE FROM CREATE_GAME:', game_code)
    game = Game.query.filter_by(game_code=game_code).all()[0]

    players_in_game = []
    players = Player.query.filter_by(game_id=game.game_id).all()
    for player in players:
        avatar_path = Avatar.query.filter_by(avatar_id=player.avatar_id).first().path
        players_in_game.append((player, avatar_path))
    word_list = []
    if request.method == 'POST':
        word_games = WordGame.query.filter_by(game_id=game.game_id).all()
        if not word_games:
            l_nums = []
            for i in range(1, 11):
                num = random.randint(168, 216)
                while num in l_nums:
                    num = random.randint(168, 216)
                l_nums.append(num)
                word = Word.query.filter_by(word_id=num).first()
                word_list.append(word)

                word_game = WordGame(game_id=game.game_id, word_id=word.word_id, word_num=i)
                print('WORD:', word)
                db.session.add(word_game)
                db.session.commit()
                print(word_list)
            for word in word_list:
                def_true = Definition.query.filter_by(word_id=word.word_id, is_def=True).first()
                definition = Definition(word_id=word.word_id, game_id=game.game_id, definition=def_true.definition, is_def=True)
                db.session.add(definition)
                db.session.commit()
            print("IN POST METHOD:", game_code)

        first_word = WordGame.query.filter_by(game_id=game.game_id, word_num=1).first()
        word = Word.query.filter_by(word_id=first_word.word_id).first()

        return redirect(url_for('new_word', word=word.word, game_code=game_code, word_num=1))

    return render_template('create_game.html', game_code=game_code, players_in_game=players_in_game)


@app.route('/new-word/<game_code>/<word>_<word_num>', methods=['POST', 'GET'])
def new_word(word, game_code, word_num):

    game = Game.query.filter_by(game_code=game_code).first()
    username = session.get('username')
    word_num = word_num

    print(request.method)

    if request.method == 'POST':
        session.pop('_flashes', None)

        print('REQUEST', request.form.get('definition'))

        if request.form.get('definition'):
            definition = request.form.get('definition')
            print("word in request:", word)
            define(word, game.game_id, username, definition)
            word = Word.query.filter_by(word=word).first()
            print("game", game)

            num_definitions = len(Definition.query.filter_by(game_id=game.game_id, word_id=word.word_id).all())
            num_players = len(Player.query.filter_by(game_id=game.game_id).all())

            show_defs= True

            if num_definitions < (num_players + 1):
                show_defs = False

            return redirect(url_for('vote', word=word.word, game_code=game.game_code, word_num=word_num, show_defs=show_defs))

    return render_template('show_word.html', word=word, game_code=game.game_code, word_num=word_num)


def define(word, game_id, username, definition):

    player = Player.query.filter_by(username=username, game_id=game_id).first()
    print('player in define word', player)

    print('word in define', word)
    word = Word.query.filter_by(word=word).first()

    existing_def = Definition.query.filter_by(player_id=player.player_id, word_id=word.word_id, game_id=game_id).all()

    if not existing_def:
        definition = Definition(player_id=player.player_id, word_id=word.word_id, definition=definition.lower().rstrip('.!?'), game_id=game_id)
        db.session.add(definition)
        db.session.commit()

    return None


@app.route('/vote/<game_code>/<word>_<word_num>/<show_defs>', methods=['POST', 'GET'])
def vote(word, game_code, word_num, show_defs):

    game = Game.query.filter_by(game_code=game_code).all()[0]
    username = session.get('username')
    players = Player.query.filter_by(game_id=game.game_id).all()
    word = Word.query.filter_by(word=word).first()
    print('word', word)
    cur_player = Player.query.filter_by(username=username, game_id=game.game_id).first()
    print('current player', cur_player)
    wait_message = None

    print('REQUEST', request.method)
    definitions = []
    if request.method == 'GET':
        print("IN GET METHOD")

        def_placement = random.randint(1, len(players))
        i = 1
        for player in players:
            if i == def_placement:
                definitions.append(Definition.query.filter_by(word_id=word.word_id, game_id=game.game_id, is_def=True).first())
            i += 1
            definitions.append(Definition.query.filter_by(player_id=player.player_id, word_id=word.word_id).first())

        word = Word.query.filter_by(word=word.word).first()
        print('word', word)

        num_definitions = len(Definition.query.filter_by(game_id=game.game_id, word_id=word.word_id).all())
        num_players = len(Player.query.filter_by(game_id=game.game_id).all())
        print("num defs", num_definitions)
        print("num players", num_players)

        show_defs = True

        if num_definitions < (num_players + 1):
            show_defs = False
            message_num = random.randint(0, len(WAIT_VOTE_MESSAGES) - 1)
            wait_message = WAIT_VOTE_MESSAGES[message_num]

    if request.method == 'POST':
        print('TYPE POST')
        print('DEFINITION: ', request.form.get('definitions'))

        print('NEXT WORD', request.form.get('next_word'))

        if request.form.get('next_word'):
            word_num = int(word_num) + 1
            max_words = len(WordGame.query.filter_by(game_id=game.game_id).all())
            print('MAX WORDS', max_words)
            print('word num', word_num)
            if word_num > max_words:
                return redirect(url_for('show_scores', game_code=game_code))
            word_game = WordGame.query.filter_by(game_id=game.game_id, word_num=word_num).first()
            print('WORD GAME', word_game)
            next_word = Word.query.filter_by(word_id=word_game.word_id).first()
            print('NEXT WORD', next_word)

            return redirect(url_for('new_word', word=next_word.word, game_code=game.game_code, word_num=word_num))

        if request.form.get('definitions'):
            definition = request.form.get('definitions')
            definition = Definition.query.filter_by(definition=definition, game_id=game.game_id).first()
            print('definition id', definition.definition_id)
            print(type(definition.is_def))
            print("CUR PLAYER", cur_player.player_id, cur_player.username)

            if definition.is_def:
                existing = Vote.query.filter_by(voter=cur_player.player_id,
                                                definition_id=definition.definition_id).all()
                if not existing:
                    new_vote = Vote(voter=cur_player.player_id,
                                    vote_receiver=cur_player.player_id,
                                    definition_id=definition.definition_id,
                                    game_id=game.game_id)
                    db.session.add(new_vote)
                    db.session.commit()

                    print('new vote', new_vote)

            else:
                existing = Vote.query.filter_by(voter=cur_player.player_id,
                                                definition_id=definition.definition_id).all()
                if not existing:
                    new_vote = Vote(voter=cur_player.player_id,
                                    vote_receiver=definition.player_id,
                                    definition_id=definition.definition_id,
                                    game_id=game.game_id)
                    db.session.add(new_vote)
                    db.session.commit()

                    print('new vote', new_vote)

            return redirect(url_for('show_vote_results', game_code=game.game_code, word=word.word, word_num=word_num))

    return render_template('vote.html', definitions=definitions, word=word.word, game_code=game.game_code,
                           word_num=word_num, show_defs=show_defs, wait_message=wait_message)


@app.route('/scores/<game_code>/<word>_<word_num>', methods=['POST', 'GET'])
def show_vote_results(game_code, word, word_num):

    game = Game.query.filter_by(game_code=game_code).first()
    players = Player.query.filter_by(game_id=game.game_id).all()
    word = Word.query.filter_by(word=word).first()
    wait_result_message = None

    vote_results = {}
    dict_def = Definition.query.filter_by(word_id=word.word_id, game_id=game.game_id, is_def=True).first()
    dict_votes = Vote.query.filter_by(definition_id=dict_def.definition_id).all()
    dict_voters = []
    for dict_vote in dict_votes:
        player = Player.query.filter_by(player_id=dict_vote.voter).first()
        dict_voters.append(player.username)
    vote_results['dictionary'] = [dict_def, dict_voters]

    scores = {}
    for player in players:
        def_obj = Definition.query.filter_by(player_id=player.player_id, word_id=word.word_id).first()
        if not def_obj:
            vote_results[player.username] = ["None", "None"]
        else:
            votes = Vote.query.filter_by(definition_id=def_obj.definition_id).all()
            voters = []
            for vote in votes:
                voter = Player.query.filter_by(player_id=vote.voter).first().username
                voters.append(voter)

            vote_results[player.username] = [def_obj, voters]

        print("VOTE Q", player.username, player.player_id, Vote.query.filter_by(vote_receiver=player.player_id).all())
        player_votes = len(Vote.query.filter_by(vote_receiver=player.player_id).all())
        avatar = Avatar.query.filter_by(avatar_id=player.avatar_id).first()
        scores[player.username] = [player_votes, avatar.path]

    print(vote_results)
    print(scores)

    num_game_votes = len(Vote.query.filter_by(game_id=game.game_id).all())
    num_players = len(players)
    print("num players", num_players)
    print("word num", word_num)
    print("num game votes", num_game_votes)

    if num_players * int(word_num) == num_game_votes:
        show_results = True
    else:
        show_results = False
        message_num = random.randint(0, len(WAIT_RESULTS_MESSAGES)-1)
        wait_result_message = WAIT_RESULTS_MESSAGES[message_num]

    return render_template('show_definitions.html', definitions=vote_results, word=word.word, game_code=game.game_code,
                           word_num=word_num, show_results=show_results, scores=scores,
                           wait_result_message=wait_result_message)


@app.route('/final_scores/<game_code>', methods=['POST', 'GET'])
def show_scores(game_code):

    game = Game.query.filter_by(game_code=game_code).first()
    username = session.get('username')

    if request.method == 'POST':

        print("in scores post")

        Vote.query.filter_by(game_id=game.game_id).delete()
        Definition.query.filter_by(game_id=game.game_id).delete()
        WordGame.query.filter_by(game_id=game.game_id).delete()
        Player.query.filter_by(game_id=game.game_id, username=username).delete()
        remaining_players = Player.query.filter_by(game_id=game.game_id).all()
        if not remaining_players:
            Game.query.filter_by(game_id=game.game_id).delete()
        db.session.commit()

        print("deleted records")

        return redirect(url_for('home'))

    players = Player.query.filter_by(game_id=game.game_id).all()
    print(players)
    scores = {}
    print(session['username'])
    for player in players:
        try:
            votes = Vote.query.filter_by(vote_receiver=player.player_id).all()
            avatar = Avatar.query.filter_by(avatar_id=player.avatar_id).first()
            points = len(votes)
            scores[player.username] = [points, avatar.path]
        except Exception as e:
            print('Error:', e)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1][0], reverse=True)
    print(sorted_scores)

    return render_template('scores.html', scores=sorted_scores, game_code=game_code)
