#!/usr/bin/env python
import sys
import random
import argparse
from view import view
import yaml
import numpy as np
import os

from control import controller, eventmanager
from agents import (GreedyEngine, WeightedGreedyEngine, RandomEngine,
                    MonteCarloTreeSearch, NegamaxEngine, AlphaBetaEngine,
                    ABCachedEngine, ABDeepEngine, PVSEngine, PVSCachedEngine,
                    PVSDeepEngine, HumanEngine)

from game.game import GameEngine
from game.arena import arena
from problem.utils import PLAYER1, PLAYER2
from view.settings import set_logging_config


engine_map = {
    'greedy': GreedyEngine,
    'weighted': WeightedGreedyEngine,
    'mcts': MonteCarloTreeSearch,
    'random': RandomEngine,
    'negamax': NegamaxEngine,
    'alphabeta': AlphaBetaEngine,
    'abcached': ABCachedEngine,
    'abdeep': ABDeepEngine,
    'pvs': PVSEngine,
    'pvscached': PVSCachedEngine,
    'pvsdeep': PVSDeepEngine,
    }


def main():
    os.environ['SDL_VIDEO_CENTERED'] = '1'  # This makes the window centered on the screen

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--static-seed', default=None, type=int,
                        help='Force a static seed for reproducible experiments')
    subparsers = parser.add_subparsers(title='Commands',
                                       description='c4 builin commands')

    game_parser = subparsers.add_parser('game', help='Play with an engine')
    game_parser.add_argument('engine', metavar='ENGINE',
                             help='Engine to use. Format: engine_name:par1:par2:...')
    game_parser.add_argument('--player2', default=False, action='store_true',
                             help='Play as player 2')
    game_parser.set_defaults(cmd=run_game)
    arena_parser = subparsers.add_parser('arena', help='Run arena')
    arena_parser.add_argument('config', metavar='CONFIGFILE',
                              type=argparse.FileType('r'))
    arena_parser.add_argument('-r', '--rounds', type=int, default=1,
                              help='Number of rounds')
    arena_parser.set_defaults(cmd=run_arena)

    bm_parser = subparsers.add_parser('bm', help='Select the bestmove')
    bm_parser.add_argument('engine', metavar='ENGINE',
                           help='Engine to use. Format: engine_name:par1:par2:...')
    bm_parser.set_defaults(cmd=run_bm)

    args = parser.parse_args()

    if args.static_seed is not None:
        np.random.seed(args.static_seed)
        random.seed(args.static_seed)

    args.cmd(args)


def run_game(args):

    # setting logging
    set_logging_config(dev=False)

    # parsing ai engine information
    engine_name = args.engine.split(':')[0]
    engine_args = args.engine.split(':')[1:]
    engine_class = engine_map[engine_name]

    # define game manager modules (mvc design)
    ev_manager = eventmanager.EventManager()
    game_model = GameEngine(ev_manager)
    keyboard = controller.Keyboard(ev_manager, game_model)
    graphics = view.GameView(ev_manager, game_model)

    if not args.player2:
        p1 = HumanEngine(PLAYER1, view, 'human')
        p2 = engine_class(PLAYER2, *engine_args)
    else:
        p1 = engine_class(PLAYER1, *engine_args)
        p2 = HumanEngine(PLAYER2, graphics, 'human')

    # Start game
    game_model.run(p1, p2)


def run_arena(args):
    config = yaml.load(args.config)
    engines = []
    subscribed_engines = set()
    for i, engine_cfg in enumerate(config):
        engine_class = engine_map[engine_cfg.pop('class')]
        engine_name = engine_cfg.pop('name', None)
        engine = engine_class(**engine_cfg)
        if engine_name is None:
            engine_name = str(engine)
        if engine_name not in subscribed_engines:
            subscribed_engines.add(engine_name)
        else:
            print >> sys.stderr, 'Error: engine name {} collides,  ' \
                                 'use "name" attribute to make it unique'.format(
                                  engine_name)
            sys.exit(1)

        engines.append((engine_name, engine))

    arena(engines, args.rounds)


def run_bm(args):
    engine_name = args.engine.split(':')[0]
    engine_args = args.engine.split(':')[1:]
    engine_class = engine_map[engine_name]
    engine = engine_class(*engine_args)
    move = engine.choose(Board())
    print('Move: %d' % (move + 1))


if __name__ == '__main__':
    random.seed()
    sys.exit(main())
